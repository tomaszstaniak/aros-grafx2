---
type: report
updated: 2026-09-22
---

# Stray characters from modifier, function and keypad keys, 2026-09-22

Reported: in GrafX2 on AROS, Amiga, Alt, Ctrl, Shift, Caps Lock, the
`-` and `+` keys and the function keys type strange letters. Verified on
AROS One 1.3 x86_64 ABIv11 under QEMU.

## Cause

`Keysym_to_ANSI()` in `src/keyboard.c` has two versions. The SDL 1.2 one
returns 0 for a key that has no character. The SDL2 one returned
`K2K(sym)` for every keysym at or above 128, which is a keycode
(`0x800 | scancode`), not a character. On AROS the SDL2 backend in the
SDK never calls `SDL_SendKeyboardText` (checked with `nm` on
`libSDL2.a`), so the KEYDOWN path added by patch 0003 is the only way
text reaches `Readline`, and it inserted that keycode. The low byte is
what showed: Left Shift is scancode 225, so `á` (0xE1); Caps Lock is 57,
so `9`; F1 is 58, so `:`; keypad `+` is 87, so `W`.

## Fix

Patch `0010-sdl2-keysym-to-ansi-no-character`: for a scancode-based
keysym return the keypad character (digits, `.`, `-`, `+`, `/`, `*`,
Enter) or 0, as the SDL 1.2 version does. A keycode without the scancode
bit is a Unicode code point from the keymap and is returned as itself.
The file-selector quicksearch reads the same variable and benefits too.
Generic SDL2 code, upstream candidate.

## Evidence

Same key sequence in the Save-picture filename field, both builds
(`before-fix-typed.png`, `after-fix-typed.png`):

| Keys pressed | Before | After |
|---|---|---|
| Shift Ctrl Alt Amiga, Caps Lock twice, KP- KP+, `-`, Shift+`=`, F1 F3, `ok` | `NO_NAME.GIFáàâã99UW-á=:<ok` | `NO_NAME.GIF+-=ok` |

Comment field on the fixed build (`after-fix-comment.png`): keypad
`/ * +` then `ab`, Left, `X` gave `/*+aXb`, so keypad operators, Shift
with a letter and cursor editing all work.

Host test `tests/test-keysym-to-ansi.py`: 10 failures on the old code, 0
on the new. `scripts/check-reproduction.sh`: PASS, 10 patches.

## What remains, outside this patch

- Shifted punctuation on the main row is not resolved: Shift+`=` types
  `=`, as before. Resolving it needs the keymap (keymap.library
  `MapRawKey`), which SDL2 does not expose.
- Under QEMU, AROS One delivers the PC keypad row `/ * - +` as `) / * +`.
  The AROS Shell shows the same (`shell-keypad.png`: `echo ")/*+"`), so
  it is the AROS keymap or keyboard driver, not SDL2 or GrafX2. After the
  fix keypad `-` therefore types `*` under QEMU, which the filename
  validator rejects. Unverified on real hardware.

## Package

Revision 3, `build/one/grafx2.x86_64-aros-v11.lha` (4 204 000 bytes),
ReadMe and manifest updated. Not installed to `SYS:` in this run; the
test ran from `Qemu Vvfat:`. Return in the filename field saves the
picture; use Esc to leave the field without saving.
