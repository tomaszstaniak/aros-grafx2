---
type: report
updated: 2026-10-08
---

# Keyboard layouts in text fields, 2026-10-08

Reported by AMIGASYSTEM (Italian user): "some of the Shift, Alt, Caps Lock,
Caret, and asterisk combinations aren't working, but the Windows PC version
has the same issues. What keyboard layout is GrafX set to internally?"
The report names no exact keys, field or keymap. The Italian keymap was
tested because the reporter is Italian and because `^` and `*` are both
shifted keys there (`Shift+ì`, `Shift++`). That choice is an inference.

## Environment

- AROS One 1.3 x86_64, ABIv11, pool slot `v11-2`, QEMU TCG, headless.
  Keys sent as QMP qcodes, i.e. PC key positions.
- ABIv11 SDK `~/Work/AROS/sdk`, SDL 2.32.10 for AROS ("sources by Ilkka
  Lehtoranta", AROS port by Kalamatee, per the strings in `libSDL2.a`).
- Toolchain `x86_64-aros-gcc` 10.5.0.
- Keymaps `pc105_i` and `pc105_d` from the guest's `DEVS:Keymaps`, set with
  `SetKeyboard` before each program was started.
- Binaries (SHA-256): revision 4 `GrafX2` `7487be19…3e04` (the file in
  the published revision 4 package); this build `fe310e6f…a1a9`;
  `keyprobe-old` `5a13e464…eaa`; `keyprobe-new` `f1f4b081…b39c`.
- mainline v1 not tested.

## How the AROS SDL2 backend delivers a key (static, from the SDK objects)

Read from `SDL_arosevents.o` and `SDL_aroskeyboard.o` in the SDK's
`libSDL2.a` (disassembly and `.rodata`):

1. **Scancode** = `table[rawkey]` for raw keys 0x00-0x71. Positional; the
   table is the same as SDL3's `scancodes_amigaos.h`.
2. **Keycode** (`sym`) comes from a keymap SDL builds once at startup: for
   every raw key except the one under Esc, `MapRawKey` of the *active AROS
   keymap* without qualifiers. A Latin-1 result is stored through a signed
   char, so `ì` becomes keycode `0xffffffec`.
3. No backend object calls `SDL_SendKeyboardText`. `SDL_TEXTINPUT` never
   arrives; confirmed by the probes (0 TEXTINPUT lines in four logs).

## Confirmed causes (guest)

Patch 0011 turned `sym` back into a raw key with a US table, then called
`MapRawKey` again. Because `sym` already carries the keymap:

- **Keymap applied twice.** QWERTZ: the `z` key gave `y` and the `y` key
  `z` (`kp-old-de-1008.txt`, lines 0 and 2).
- **Characters above 0x7F.** Their negative keycode is not in 0011's table,
  so the generic code returned it as `0xffxx`: `ì`, `ò`, `è`, `ö`, `ü` and
  every combination on those keys (`Shift+ì` = `^`, `AltGr+ò` = `@`,
  `AltGr+è` = `[`) were lost. The comment field rejects them; the filename
  field accepted the low byte, i.e. the unshifted character.
- **Keys missing from 0011's table** (`+` on Italian) used the unshifted
  keycode, so `Shift++` gave `+` instead of `*`.

Same physical keys typed into the Save-picture comment field, Italian keymap:

| Program | Result |
|---|---|
| AROS Shell (`it-shell.png`) | `ì^+*@òç*` |
| GrafX2 revision 4 (`it-rev4-comment.png`) | `aA++*yzA` |
| GrafX2 with 0012 (`it-0012-comment.png`) | `aAì^+*@òç*yzA` |

German keymap, same key sequence (`keys-de.sh`):

| Program | Result |
|---|---|
| AROS Shell (`de-shell.png`) | `zyZöü*é^e^ @` |
| GrafX2 with 0012 (`de-0012-comment.png`) | `zyZöü*e^e^ @` |

Filename field with 0012 (`it-0012-filename.png`): `ok`, `Shift++`, `ì`,
`Shift+ì` gave `okì^`; `*` was refused by the AROS filename validator, as
intended. Return then saved the picture (title bar `NO_NAMEokì^…`).

## Fix

Patch `0012-aros-keymap-rawkey-from-scancode`: the raw key is found from the
scancode (inverse of the backend table), and `MapRawKey`'s result is used
only when it is one printable Latin-1 character. Control characters and CSI
sequences (Return, Esc, cursor and function keys) keep the generic handling.
Num Lock no longer sets `IEQUALIFIER_NUMERICPAD`. After review, a control
character produced with Ctrl also gives no text: the first 0012 build let
Ctrl+A fall through to the generic code, which inserts `a` (revision 4
inserted nothing; the probe logs above predate that change).

## Checked and not a cause

- **Double insertion** (KEYDOWN and TEXTINPUT): impossible with this SDK,
  which never sends TEXTINPUT. Would need rechecking if the SDK's SDL2
  starts to.
- **Caps Lock**: SDL toggles `KMOD_CAPS` on every press and the backend
  sends a press for both; `Caps+a`, `Caps+Shift+a` gave `A` (Amiga keymaps
  do not invert Caps with Shift).
- **Shortcuts**: `Keysym_to_keycode` is untouched. The probes' `Key`
  column is identical for old and new code on both keymaps. Shortcuts use
  the keymap's unshifted keycode plus modifier bits; non-ASCII keys get
  codes like `0x09ec` that can be assigned but whose names look odd.
- **Left Alt vs AltGr**: both give the keymap's Alt column (`@` from `ò`
  either way), as in the Shell; AROS keymaps do not separate them.

## Remaining limits

- **Dead keys** do not compose: German `´` then `e` gives `e`, the Shell
  gives `é`. `MapRawKey` is called without the previous key; supporting it
  means tracking the last key in `ie_Prev1DownCode`. Italian has no dead
  keys.
- A key mapped to a string longer than one character inserts nothing.
- Keypad: under QEMU the keypad operators arrive one raw key off from the
  SDL table (`kp_multiply` → raw 0x5C, SDL `KP_DIVIDE`). The keymap gives
  the right character, so text is right with 0012, but keypad *shortcuts*
  follow SDL's name (`KEY_KP_MULTIPLY` fires on keypad `-`). Not changed.
- The table is copied from the SDK backend. If the SDK's SDL2 changes its
  table, this must change too.
- Windows: not reproduced. On Windows text arrives through SDL_TEXTINPUT,
  a different path, so these findings do not explain it.

## Reproduce

Host: `python3 tests/test-aros-keymap-text.py` (56 failures on the 0011
code, 0 with 0012). Besides key cases it reads the raw-key table out of the
SDK's `libSDL2.a` and requires every raw key to map back to itself and no
other scancode to reach `MapRawKey`; swapping two entries of the table in
`keyboard.c` makes it fail. Guest probes: `tests/build-guest-keyprobe.sh <dir> <commit>`
builds `keyprobe-old` from keyboard.c at the given work commit (the 2026-10-08
run used the commit `0011-aros-keymap-text-fallback.patch`) and
`keyprobe-new` from the current tree; run `keyprobe RESULTS:<new-name>.txt`, press keys, Esc twice
to quit. Key sequences: `keys-*.sh` (qcodes for `tools/vmctl.py key`).

## Revision 5 package test

`dist/GrafX2-2.9-r5.x86_64-aros-v11.lha`, binary SHA-256 `3bd9fbf7…99c6`
(after the Ctrl change). The guest has no `lha`, so the archive was unpacked
on the host with the same LHa for UNIX 1.14i that created it and staged as a
ZIP; the `GrafX2` binary was 9 991 264 bytes in the guest, as in the archive.
Pool slot `v11-3` (ABIv11 2026.09 base, QEMU TCG), `SetKeyboard pc105_i`,
run from `RAM:p5/x/GrafX2`. Keys: `keys-r5-package.sh`, then Ctrl+a and `k`.

| Where | Result |
|---|---|
| AROS Shell (`r5-it-shell.png`) | `aAAAAaì^+*@òç*yz` |
| Comment field (`r5-it-comment.png`) | `aAAAAaì^+*@òç*yzk` |

So Caps+a and Caps+Shift+a give `A` in both, and Ctrl+a inserted nothing.
Filename field (`r5-it-filename.png`): `r5`, `Shift+ì`, `Shift++`, `ì` gave
`NO_NAMEr5^ì`; `*` was refused. Return saved `NO_NAMEr5^ì.gif`, 1 774 bytes
(`r5-saved-list.png`); GrafX2 then quit normally and wrote its settings.
`gfx2.lck` stays by design (patch 0006). Not run on AROS One 1.3 with this
exact binary (the 1.3 runs above used the first 0012 build, which differs
only in the Ctrl handling) and not on mainline v1.
