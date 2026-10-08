#!/usr/bin/env python3
"""Host test for the AROS branch of the SDL2 Keysym_to_ANSI() (patch 0012).

Compiles the production work/grafx2/src/keyboard.c with __AROS__ defined,
against the host SDL2 headers, the SDK's real devices/rawkeycodes.h and a
small stand-in for keymap.library MapRawKey. The stand-in carries the rows
of the AROS keymaps pc104_usa, pc105_i and pc105_d (workbench/devs/keymaps
in the AROS tree) that the cases below press.

Each key is fed as the AROS SDL2 backend delivers it: scancode from the
raw key position, keycode from the active keymap without qualifiers
(Latin-1 bytes sign-extended, as SDL_aroskeyboard.o does with movsbl).

The raw-key table is checked against the one in the SDK's libSDL2.a (read
from the archive, not from keyboard.c): every raw key the backend can send
must map back to itself, and other scancodes must not reach MapRawKey.

What it cannot show: the real keymap.library, the modifier state SDL keeps
on AROS (Caps Lock in particular), and QEMU's key delivery. Those need a
guest run; see docs/attachments/2026-10-08-keyboard-layouts/.
"""
from pathlib import Path
import os
import shutil
import struct
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
src = root / 'work/grafx2/src'
sdk = Path(os.environ.get('AROS_SDK', Path.home() / 'Work/AROS/sdk'))
sdl_prefix = Path(subprocess.run(['brew', '--prefix', 'sdl2'], capture_output=True,
                                 text=True, check=True).stdout.strip())

inputevent_h = r'''
#ifndef DEVICES_INPUTEVENT_H
#define DEVICES_INPUTEVENT_H
typedef unsigned char UBYTE;
typedef unsigned short UWORD;
typedef short WORD;
typedef char *STRPTR;
struct InputEvent { UBYTE ie_Class; UWORD ie_Code; UWORD ie_Qualifier; };
#define IECLASS_RAWKEY 1
#define IEQUALIFIER_LSHIFT     (1<<0)
#define IEQUALIFIER_RSHIFT     (1<<1)
#define IEQUALIFIER_CAPSLOCK   (1<<2)
#define IEQUALIFIER_CONTROL    (1<<3)
#define IEQUALIFIER_LALT       (1<<4)
#define IEQUALIFIER_RALT       (1<<5)
#define IEQUALIFIER_LCOMMAND   (1<<6)
#define IEQUALIFIER_RCOMMAND   (1<<7)
#define IEQUALIFIER_NUMERICPAD (1<<8)
#endif
'''

keymap_h = r'''
#ifndef PROTO_KEYMAP_H
#define PROTO_KEYMAP_H
#include <devices/inputevent.h>
WORD MapRawKey(struct InputEvent *event, STRPTR buffer, WORD length, void *keymap);
#endif
'''

# Columns as in the .akmd files: alt+shift, alt, shift, none.
# -1 is a dead key (KCF_DEAD): MapRawKey returns 0 characters for it alone.
fake = r'''
#include <string.h>
#include <devices/inputevent.h>
#define DEAD -1
struct row { int rawkey; int vanilla; int c[4]; };
static const struct row us[] = {
  {0x0C, 0, {'+', '=', '+', '='}},
  {0x1B, 0, {'}', ']', '}', ']'}},
  {0x15, 1, {'Y', 'y', 'Y', 'y'}},
  {0x31, 1, {'Z', 'z', 'Z', 'z'}},
  {0x20, 1, {0xC1, 0xE1, 'A', 'a'}},
  {0, 0, {0}}
};
static const struct row it[] = {
  {0x0C, 0, {'~', '~', '^', 0xEC}},
  {0x1B, 0, {']', ']', '*', '+'}},
  {0x29, 0, {'@', '@', 0xE7, 0xF2}},
  {0x15, 1, {'Y', 'y', 'Y', 'y'}},
  {0x31, 1, {'<', 0xAB, 'Z', 'z'}},
  {0x20, 1, {'A', 'a', 'A', 'a'}},
  {0, 0, {0}}
};
static const struct row de[] = {
  {0x0C, 0, {DEAD, DEAD, DEAD, DEAD}},
  {0x1B, 0, {'*', '~', '*', '+'}},
  {0x29, 0, {':', ';', 0xD6, 0xF6}},
  {0x15, 1, {0xA5, 0xA4, 'Z', 'z'}},
  {0x31, 1, {'Y', 'y', 'Y', 'y'}},
  {0x20, 1, {'A', 'a', 'A', 'a'}},
  {0, 0, {0}}
};
const struct row *active = us;
int last_code = -1;
void select_keymap(int which) { active = which == 0 ? us : which == 1 ? it : de; }

WORD MapRawKey(struct InputEvent *e, STRPTR buf, WORD len, void *km)
{
  UWORD q = e->ie_Qualifier;
  int shift = (q & (IEQUALIFIER_LSHIFT|IEQUALIFIER_RSHIFT)) != 0;
  int alt = (q & (IEQUALIFIER_LALT|IEQUALIFIER_RALT)) != 0;
  const struct row *r;
  int ch;
  (void)km;
  last_code = e->ie_Code;
  if (e->ie_Code == 0x0D) {  /* filter boundaries: shift gives C1 0x85, alt NBSP */
    buf[0] = (char)(alt ? 0xA0 : shift ? 0x85 : 0x7F);
    return 1;
  }
  if (e->ie_Code >= 0x60 && e->ie_Code <= 0x67) return 0;  /* qualifier keys */
  if (e->ie_Code == 0x44) { buf[0] = '\r'; return 1; }
  if (e->ie_Code == 0x50) { memcpy(buf, "\x9b" "0~", 3); return 3; }  /* F1 */
  if (e->ie_Code == 0x5D) { buf[0] = '*'; return 1; }  /* keypad * */
  for (r = active; r->rawkey || r->c[0]; r++) {
    if (r->rawkey != e->ie_Code) continue;
    if (r->vanilla && (q & IEQUALIFIER_CAPSLOCK)) shift = 1;
    ch = r->c[alt ? (shift ? 0 : 1) : (shift ? 2 : 3)];
    if (ch == DEAD) return 0;
    if (r->vanilla && (q & IEQUALIFIER_CONTROL)) ch &= 0x1F;
    buf[0] = (char)ch;
    return 1;
  }
  return 0;
}
'''

harness = r'''
#include <SDL.h>
#include <stdio.h>
#include <string.h>
#include "struct.h"
#include "keyboard.h"
void select_keymap(int which);
extern int last_code;
static int fails;
/* Raw key -> scancode as the SDK's libSDL2.a has it (SDL_aroskeyboard.o
   .rodata), read by the Python driver, not copied from keyboard.c. */
static const int sdk_table[] = { SDK_TABLE };
/* sym is what the AROS backend reports: the unshifted keymap character of
   the key, sign-extended from a signed char. */
static void check(const char *map, SDL_Scancode sc, int keymap_char, Uint16 mod,
                  unsigned expect, const char *name)
{
  SDL_Keysym k; memset(&k, 0, sizeof k);
  k.scancode = sc;
  k.sym = keymap_char ? (SDL_Keycode)(signed char)keymap_char : SDL_GetKeyFromScancode(sc);
  k.mod = mod;
  unsigned got = Keysym_to_ANSI(k);
  printf("%-3s %-22s expect 0x%04x got 0x%04x %s\n", map, name, expect, got,
         got == expect ? "ok" : "FAIL");
  if (got != expect) fails++;
}
int main(void)
{
  select_keymap(0);
  check("us", SDL_SCANCODE_A, 'a', 0, 'a', "a");
  check("us", SDL_SCANCODE_A, 'a', KMOD_LSHIFT, 'A', "Shift+a");
  check("us", SDL_SCANCODE_A, 'a', KMOD_CAPS, 'A', "Caps+a");
  check("us", SDL_SCANCODE_A, 'a', KMOD_CAPS|KMOD_RSHIFT, 'A', "Caps+Shift+a");
  check("us", SDL_SCANCODE_EQUALS, '=', KMOD_LSHIFT, '+', "Shift+=");
  check("us", SDL_SCANCODE_Y, 'y', 0, 'y', "y");
  check("us", SDL_SCANCODE_LSHIFT, 0, KMOD_LSHIFT, 0, "Shift alone");
  check("us", SDL_SCANCODE_F1, 0, 0, 0, "F1");
  check("us", SDL_SCANCODE_RETURN, 0, 0, '\r', "Return");
  check("us", SDL_SCANCODE_KP_MULTIPLY, 0, 0, '*', "keypad *");
  check("us", SDL_SCANCODE_A, 'a', KMOD_LCTRL, 0, "Ctrl+a (no text)");
  check("us", SDL_SCANCODE_BACKSLASH, 0, 0, '\\', "0x7F -> generic");
  check("us", SDL_SCANCODE_BACKSLASH, 0, KMOD_LSHIFT, '\\', "C1 0x85 -> generic");
  check("us", SDL_SCANCODE_BACKSLASH, 0, KMOD_LALT, 0xA0, "Alt NBSP 0xA0");

  /* Every raw key the backend can produce must come back as that raw key
     (first one for a scancode listed twice); scancodes the backend never
     produces must not reach MapRawKey at all. */
  {
    int i, j, n = (int)(sizeof(sdk_table)/sizeof(sdk_table[0])), bad = 0;
    for (i = 0; i < n; i++) {
      SDL_Keysym k;
      if (sdk_table[i] == 0) continue;
      for (j = 0; j < i && sdk_table[j] != sdk_table[i]; j++) ;
      if (j < i) continue;
      memset(&k, 0, sizeof k);
      k.scancode = sdk_table[i];
      k.sym = SDL_GetKeyFromScancode(k.scancode);
      last_code = -1;
      Keysym_to_ANSI(k);
      if (last_code != i) {
        printf("raw 0x%02x scancode %d came back as raw %d FAIL\n", i, sdk_table[i], last_code);
        bad++;
      }
    }
    for (i = 1; i < SDL_NUM_SCANCODES; i++) {
      SDL_Keysym k;
      for (j = 0; j < n && sdk_table[j] != i; j++) ;
      if (j < n) continue;
      memset(&k, 0, sizeof k);
      k.scancode = i;
      k.sym = SDL_GetKeyFromScancode(i);
      last_code = -1;
      Keysym_to_ANSI(k);
      if (last_code != -1) {
        printf("scancode %d not in the backend table reached MapRawKey as raw %d FAIL\n", i, last_code);
        bad++;
      }
    }
    printf("backend table: %d raw keys, %d mismatches\n", n, bad);
    fails += bad;
  }

  select_keymap(1);
  check("it", SDL_SCANCODE_RIGHTBRACKET, '+', 0, '+', "+");
  check("it", SDL_SCANCODE_RIGHTBRACKET, '+', KMOD_LSHIFT, '*', "Shift++ = *");
  check("it", SDL_SCANCODE_EQUALS, 0xEC, 0, 0xEC, "i-grave");
  check("it", SDL_SCANCODE_EQUALS, 0xEC, KMOD_LSHIFT, '^', "Shift+i-grave = ^");
  check("it", SDL_SCANCODE_SEMICOLON, 0xF2, 0, 0xF2, "o-grave");
  check("it", SDL_SCANCODE_SEMICOLON, 0xF2, KMOD_RALT, '@', "AltGr+o-grave = @");
  check("it", SDL_SCANCODE_A, 'a', KMOD_CAPS, 'A', "Caps+a");

  select_keymap(2);
  check("de", SDL_SCANCODE_Y, 'z', 0, 'z', "z (QWERTZ)");
  check("de", SDL_SCANCODE_Z, 'y', 0, 'y', "y (QWERTZ)");
  check("de", SDL_SCANCODE_Y, 'z', KMOD_LSHIFT, 'Z', "Shift+z (QWERTZ)");
  check("de", SDL_SCANCODE_SEMICOLON, 0xF6, 0, 0xF6, "o-umlaut");
  check("de", SDL_SCANCODE_RIGHTBRACKET, '+', KMOD_LSHIFT, '*', "Shift++ = *");
  check("de", SDL_SCANCODE_EQUALS, 0, 0, 0, "dead acute alone");
  printf("%d failures\n", fails);
  return fails != 0;
}
'''

def sdk_scancode_table(tmp):
    """Raw key -> SDL scancode from the SDK's libSDL2.a, checked against the
    copy SDL_arosevents.o indexes when it sends a key."""
    toolchain = Path(os.environ.get('AROS_TOOLCHAIN', Path.home() / 'Work/AROS/toolchain'))
    objcopy = toolchain / 'x86_64-aros-objcopy'
    lib = sdk / 'lib/libSDL2.a'
    out = tmp / 'sdl2'
    out.mkdir()
    subprocess.run(['llvm-ar' if shutil.which('llvm-ar') else '/opt/homebrew/opt/llvm/bin/llvm-ar',
                    'x', str(lib), 'SDL_aroskeyboard.o', 'SDL_arosevents.o'], cwd=out, check=True)
    def rodata(obj):
        dst = out / (obj + '.rodata')
        subprocess.run([str(objcopy), '-O', 'binary', '--only-section=.rodata',
                        str(out / obj), str(dst)], check=True)
        return dst.read_bytes()
    kb = rodata('SDL_aroskeyboard.o')
    table = list(struct.unpack('<%di' % (len(kb) // 4), kb))
    ev = rodata('SDL_arosevents.o')
    if ev[0x1e0:0x1e0 + len(kb)] != kb:
        sys.exit('SDL_arosevents.o does not carry the same raw-key table at .rodata+0x1e0; '
                 'the SDK SDL2 changed, re-derive the table')
    return table


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    harness = harness.replace('SDK_TABLE', ', '.join(str(v) for v in sdk_scancode_table(tmp)))
    (tmp / 'devices').mkdir()
    (tmp / 'proto').mkdir()
    (tmp / 'devices/inputevent.h').write_text(inputevent_h)
    (tmp / 'devices/rawkeycodes.h').write_bytes((sdk / 'include/devices/rawkeycodes.h').read_bytes())
    (tmp / 'proto/keymap.h').write_text(keymap_h)
    (tmp / 'fake.c').write_text(fake)
    (tmp / 'test.c').write_text(harness)
    exe = tmp / 'test'
    subprocess.run(['cc', '-DUSE_SDL2', '-D__AROS__', '-w', '-I', str(tmp),
                    '-I', str(sdl_prefix / 'include/SDL2'), '-I', str(src),
                    '-o', str(exe), str(tmp / 'test.c'), str(tmp / 'fake.c'),
                    str(src / 'keyboard.c'), '-L', str(sdl_prefix / 'lib'), '-lSDL2'],
                   check=True)
    result = subprocess.run([str(exe)], text=True, capture_output=True)
    print(result.stdout, end='')
    sys.exit(result.returncode)
