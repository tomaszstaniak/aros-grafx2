/* Guest probe for GrafX2's SDL2 keyboard paths on AROS.
 *
 * Linked against the production work/grafx2/src/keyboard.c, so the logged
 * Keysym_to_keycode()/Keysym_to_ANSI() values are what GrafX2 computes for
 * the same event. Next to them it logs what the AROS SDL2 backend delivered
 * (scancode, keycode, modifiers), any SDL_TEXTINPUT, and MapRawKey's full
 * output for the raw key at that scancode, so each boundary can be checked.
 *
 * Usage: keyprobe <logfile>   Esc twice in a row quits.
 * Build: tests/build-guest-keyprobe.sh
 */
#include <SDL.h>
#include <stdio.h>
#include <string.h>
#include <devices/inputevent.h>
#include <proto/keymap.h>
#include "struct.h"
#include "keyboard.h"

/* Same table as keyboard.c (patch 0012), kept separate so the old build
   of keyboard.c can be probed too. */
#define S(x) SDL_SCANCODE_##x
static const SDL_Scancode table[] = {
  S(GRAVE), S(1), S(2), S(3), S(4), S(5), S(6), S(7),
  S(8), S(9), S(0), S(MINUS), S(EQUALS), S(BACKSLASH), S(INTERNATIONAL3), S(KP_0),
  S(Q), S(W), S(E), S(R), S(T), S(Y), S(U), S(I),
  S(O), S(P), S(LEFTBRACKET), S(RIGHTBRACKET), S(UNKNOWN), S(KP_1), S(KP_2), S(KP_3),
  S(A), S(S), S(D), S(F), S(G), S(H), S(J), S(K),
  S(L), S(SEMICOLON), S(APOSTROPHE), S(INTERNATIONAL1), S(UNKNOWN), S(KP_4), S(KP_5), S(KP_6),
  S(INTERNATIONAL2), S(Z), S(X), S(C), S(V), S(B), S(N), S(M),
  S(COMMA), S(PERIOD), S(SLASH), S(UNKNOWN), S(KP_PERIOD), S(KP_7), S(KP_8), S(KP_9),
  S(SPACE), S(BACKSPACE), S(TAB), S(KP_ENTER), S(RETURN), S(ESCAPE), S(DELETE), S(INSERT),
  S(PAGEUP), S(PAGEDOWN), S(KP_MINUS), S(F11), S(UP), S(DOWN), S(RIGHT), S(LEFT),
  S(F1), S(F2), S(F3), S(F4), S(F5), S(F6), S(F7), S(F8),
  S(F9), S(F10), S(KP_LEFTPAREN), S(KP_RIGHTPAREN), S(KP_DIVIDE), S(KP_MULTIPLY), S(KP_PLUS), S(SCROLLLOCK),
  S(LSHIFT), S(RSHIFT), S(CAPSLOCK), S(LCTRL), S(LALT), S(RALT), S(LGUI), S(RGUI),
  S(UNKNOWN), S(UNKNOWN), S(UNKNOWN), S(MENU), S(KP_PERIOD), S(PRINTSCREEN), S(PAUSE), S(F12),
  S(HOME), S(END)
};
#undef S

static UWORD qual(SDL_Keymod mod)
{
  UWORD q = 0;
  if (mod & KMOD_LSHIFT) q |= IEQUALIFIER_LSHIFT;
  if (mod & KMOD_RSHIFT) q |= IEQUALIFIER_RSHIFT;
  if (mod & KMOD_CAPS)   q |= IEQUALIFIER_CAPSLOCK;
  if (mod & KMOD_CTRL)   q |= IEQUALIFIER_CONTROL;
  if (mod & KMOD_LALT)   q |= IEQUALIFIER_LALT;
  if (mod & KMOD_RALT)   q |= IEQUALIFIER_RALT;
  if (mod & KMOD_LGUI)   q |= IEQUALIFIER_LCOMMAND;
  if (mod & KMOD_RGUI)   q |= IEQUALIFIER_RCOMMAND;
  return q;
}

int main(int argc, char **argv)
{
  FILE *log;
  SDL_Window *win;
  SDL_Event ev;
  int escapes = 0, n = 0, running = 1;

  if (argc < 2) { fprintf(stderr, "usage: keyprobe <logfile>\n"); return 20; }
  log = fopen(argv[1], "w");
  if (!log) { fprintf(stderr, "cannot open %s\n", argv[1]); return 20; }
  if (SDL_Init(SDL_INIT_VIDEO) != 0) { fprintf(log, "SDL_Init: %s\n", SDL_GetError()); fclose(log); return 20; }
  win = SDL_CreateWindow("keyprobe", 40, 40, 320, 120, 0);
  SDL_StartTextInput();
  fprintf(log, "# n type scancode sym mod | rawkey qual maprawkey_len bytes | Key Key_ANSI\n");
  while (running && SDL_WaitEvent(&ev)) {
    if (ev.type == SDL_KEYDOWN || ev.type == SDL_KEYUP) {
      SDL_Keysym k = ev.key.keysym;
      int rawkey = -1, i, len = -2;
      UBYTE buf[16];
      struct InputEvent ie = { 0 };
      for (i = 0; i < (int)(sizeof(table)/sizeof(table[0])); i++)
        if (table[i] == k.scancode && k.scancode != SDL_SCANCODE_UNKNOWN) { rawkey = i; break; }
      fprintf(log, "%d %s sc=%d sym=0x%08x mod=0x%04x |", n++,
              ev.type == SDL_KEYDOWN ? (ev.key.repeat ? "REPEAT" : "DOWN") : "UP",
              (int)k.scancode, (unsigned)k.sym, (unsigned)k.mod);
      if (ev.type == SDL_KEYDOWN && rawkey >= 0) {
        ie.ie_Class = IECLASS_RAWKEY;
        ie.ie_Code = rawkey;
        ie.ie_Qualifier = qual(k.mod);
        len = MapRawKey(&ie, (STRPTR)buf, sizeof(buf), NULL);
        fprintf(log, " raw=0x%02x q=0x%04x len=%d", rawkey, ie.ie_Qualifier, len);
        for (i = 0; i < len && i < (int)sizeof(buf); i++)
          fprintf(log, " %02x", buf[i]);
      } else {
        fprintf(log, " raw=%d", rawkey);
      }
      if (ev.type == SDL_KEYDOWN)
        fprintf(log, " | Key=0x%04x ANSI=0x%04x\n", Keysym_to_keycode(k), Keysym_to_ANSI(k));
      else
        fprintf(log, "\n");
      if (ev.type == SDL_KEYDOWN && !ev.key.repeat) {
        escapes = (k.sym == SDLK_ESCAPE) ? escapes + 1 : 0;
        if (escapes >= 2) running = 0;
      }
    } else if (ev.type == SDL_TEXTINPUT) {
      fprintf(log, "%d TEXTINPUT '%s'\n", n++, ev.text.text);
    } else if (ev.type == SDL_QUIT) {
      running = 0;
    }
    fflush(log);
  }
  fprintf(log, "# end\n");
  fclose(log);
  SDL_DestroyWindow(win);
  SDL_Quit();
  return 0;
}
