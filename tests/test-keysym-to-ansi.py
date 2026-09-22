#!/usr/bin/env python3
"""Host test for the SDL2 Keysym_to_ANSI() character mapping.

Compiles the production work/grafx2/src/keyboard.c against the host SDL2
headers and checks that keys without a character (modifiers, function
keys, cursor keys) map to 0, that the keypad maps to its characters, and
that letters and keymap code points are unchanged. Guest evidence is in
docs/attachments/2026-09-22-keyboard-modifiers/.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
src = root / 'work/grafx2/src'
sdl_prefix = Path(subprocess.run(['brew', '--prefix', 'sdl2'], capture_output=True,
                                 text=True, check=True).stdout.strip())

harness = r'''
#include <SDL.h>
#include <stdio.h>
#include <string.h>
#include "struct.h"
#include "keyboard.h"
static int fails;
static void check(SDL_Keycode sym, Uint16 mod, unsigned expect, const char *name)
{
  SDL_Keysym k; memset(&k, 0, sizeof k); k.sym = sym; k.mod = mod;
  k.scancode = SDL_GetScancodeFromKey(sym);
  unsigned got = Keysym_to_ANSI(k);
  printf("%-12s expect 0x%04x got 0x%04x %s\n", name, expect, got, got == expect ? "ok" : "FAIL");
  if (got != expect) fails++;
}
int main(void)
{
  check(SDLK_LSHIFT, 0, 0, "LSHIFT");
  check(SDLK_RSHIFT, 0, 0, "RSHIFT");
  check(SDLK_LCTRL, 0, 0, "LCTRL");
  check(SDLK_LALT, 0, 0, "LALT");
  check(SDLK_LGUI, 0, 0, "LGUI");
  check(SDLK_CAPSLOCK, 0, 0, "CAPSLOCK");
  check(SDLK_F1, 0, 0, "F1");
  check(SDLK_F3, 0, 0, "F3");
  check(SDLK_F12, 0, 0, "F12");
  check(SDLK_LEFT, 0, 0, "LEFT");
  check(SDLK_HOME, 0, 0, "HOME");
  check(SDLK_KP_DIVIDE, 0, '/', "KP_DIVIDE");
  check(SDLK_KP_MULTIPLY, 0, '*', "KP_MULTIPLY");
  check(SDLK_KP_MINUS, 0, '-', "KP_MINUS");
  check(SDLK_KP_PLUS, 0, '+', "KP_PLUS");
  check(SDLK_KP_PERIOD, 0, '.', "KP_PERIOD");
  check(SDLK_KP_ENTER, 0, '\r', "KP_ENTER");
  check(SDLK_KP_0, 0, '0', "KP_0");
  check(SDLK_KP_7, 0, '7', "KP_7");
  check(SDLK_MINUS, 0, '-', "MINUS");
  check(SDLK_ESCAPE, 0, 27, "ESCAPE");
  check(SDLK_RETURN, 0, '\r', "RETURN");
  check(SDLK_a, 0, 'a', "a");
  check(SDLK_a, KMOD_LSHIFT, 'A', "shift-a");
  check(0xE9, 0, 0xE9, "e-acute");
  printf("%d failures\n", fails);
  return fails != 0;
}
'''

with tempfile.TemporaryDirectory() as tmp:
    test_c = Path(tmp) / 'test.c'
    test_c.write_text(harness)
    exe = Path(tmp) / 'test'
    subprocess.run(['cc', '-DUSE_SDL2', '-w', '-I', str(sdl_prefix / 'include/SDL2'),
                    '-I', str(src), '-o', str(exe), str(test_c), str(src / 'keyboard.c'),
                    '-L', str(sdl_prefix / 'lib'), '-lSDL2'], check=True)
    result = subprocess.run([str(exe)], text=True, capture_output=True)
    print(result.stdout, end='')
    sys.exit(result.returncode)
