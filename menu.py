"""
menu.py  -  Bingrow  (Main Menu Screen)

STANDALONE - no external variables needed.

TO CONNECT TO OTHER FILES:
    CONTINUE / NEW GAME  -> stage.py    : show_stage_screen(...)
    PLANT HEIGHT         -> plant.py    : show_plant_height_screen(...)
    SETTINGS             -> settings.py : show_settings_screen(...)

ASSETS (same folder as this .py file):
    menubg.png
    Gameplay Music.mp3

RUN THIS FILE to launch the game:
    python menu.py
"""

import pygame
import sys

# ── Init ───────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 620
FPS        = 60
BG_IMAGE   = "menubg.png"
MUSIC_FILE = "Gameplay Music.mp3"

# Save data (replace with your actual save/load logic when ready)
PLAYER_NAME   = "Josef"
HAS_SAVE_DATA = True
PLANT_HEIGHT  = 8
CURRENT_STAGE = 3

# Colours
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
GREEN       = (106, 191, 75)
GREEN_DARK  = (78,  154, 46)
GREEN_TEXT  = (106, 191, 75)
YELLOW      = (212, 232, 74)
BROWN_LIGHT = (180, 120, 60)
BROWN_DARK  = (100,  60, 20)
GRAY        = (200, 200, 200)
PURPLE      = (168,  85, 200)

# Fonts
FONT_TITLE  = pygame.font.SysFont("Arial",  28, bold=True)
FONT_BTN    = pygame.font.SysFont("Arial",  16, bold=True)
FONT_SMALL  = pygame.font.SysFont("Arial",   9, bold=True)
FONT_SIGN   = pygame.font.SysFont("Arial",  11, bold=True)
FONT_SIGN2  = pygame.font.SysFont("Arial",  14, bold=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None


def draw_rounded_rect(surface, color, rect, radius):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
    pygame.draw.circle(surface, color, (x + radius,     y + radius),     radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius),     radius)
    pygame.draw.circle(surface, color, (x + radius,     y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)


def draw_pill_button(surface, text, cx, cy, w, h, color, dark, text_color, font):
    r = h // 2
    # Shadow
    draw_rounded_rect(surface, dark, (cx - w//2 + 2, cy - h//2 + 3, w, h), r)
    # Button face
    draw_rounded_rect(surface, color, (cx - w//2, cy - h//2, w, h), r)
    # Text
    label = font.render(text, True, text_color)
    surface.blit(label, (cx - label.get_width()//2, cy - label.get_height()//2))
    return pygame.Rect(cx - w//2, cy - h//2, w, h)


def draw_exit_button(surface, cx, cy, w, h, font):
    r = h // 2
    draw_rounded_rect(surface, WHITE, (cx - w//2, cy - h//2, w, h), r)
    pygame.draw.rect(surface, GREEN_DARK,
                     (cx - w//2 + r, cy - h//2, w - 2*r, h), 2)
    pygame.draw.circle(surface, GREEN_DARK, (cx - w//2 + r, cy), r, 2)
    pygame.draw.circle(surface, GREEN_DARK, (cx + w//2 - r, cy), r, 2)
    label = font.render("EXIT GAME", True, GREEN_DARK)
    surface.blit(label, (cx - label.get_width()//2, cy - label.get_height()//2))
    return pygame.Rect(cx - w//2, cy - h//2, w, h)


def start_music():
    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
    except Exception:
        pass


# ── Menu Screen ────────────────────────────────────────────────────────────────
def show_menu(screen, clock=None):
    if clock is None:
        clock = pygame.time.Clock()

    bg = load_image(BG_IMAGE, (SCREEN_W, SCREEN_H))

    # Button layout
    BTN_W, BTN_H = 220, 44
    if HAS_SAVE_DATA:
        buttons = ["CONTINUE", "NEW GAME", "PLANT HEIGHT", "SETTINGS"]
        start_y = 280
    else:
        buttons = ["NEW GAME", "SETTINGS"]
        start_y = 320

    gap = 58

    while True:
        mx, my = pygame.mouse.get_pos()
        btn_rects = {}

        # ── Draw ──────────────────────────────────────────────────────────────
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((168, 216, 168))

        # Purple border
        pygame.draw.rect(screen, PURPLE,
                         (0, 0, SCREEN_W, SCREEN_H), 3)

        # Version label
        v1 = FONT_SMALL.render("v.1.0.0", True, WHITE)
        v2 = FONT_SMALL.render("A BONDOX STUDIOS GAME", True, WHITE)
        screen.blit(v1, (SCREEN_W - v1.get_width() - 8, 6))
        screen.blit(v2, (SCREEN_W - v2.get_width() - 8, 16))

        # Buttons
        for i, label in enumerate(buttons):
            cy  = start_y + i * gap
            col = GREEN
            tag = label
            r   = draw_pill_button(screen, label, SCREEN_W//2, cy,
                                   BTN_W, BTN_H, col, GREEN_DARK, WHITE, FONT_BTN)
            btn_rects[tag] = r

        # Exit button
        btn_rects["EXIT"] = draw_exit_button(
            screen, SCREEN_W - 100, SCREEN_H - 50, 140, 40, FONT_BTN)

        # Welcome back sign
        if HAS_SAVE_DATA:
            line1 = FONT_SIGN.render("WELCOME BACK,", True, BROWN_LIGHT)
            line2 = FONT_SIGN2.render(f"{PLAYER_NAME.upper()}!", True, BROWN_DARK)
            screen.blit(line1, (88, 358))
            screen.blit(line2, (100, 374))

        pygame.display.flip()
        clock.tick(FPS)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rects.get("CONTINUE",    pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                    return ("continue", PLAYER_NAME, PLANT_HEIGHT, CURRENT_STAGE)
                if btn_rects.get("NEW GAME",    pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                    return ("new_game", PLAYER_NAME, 0, 1)
                if btn_rects.get("PLANT HEIGHT",pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                    return ("plant_height", PLAYER_NAME, PLANT_HEIGHT, CURRENT_STAGE)
                if btn_rects.get("SETTINGS",    pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                    return ("settings", PLAYER_NAME, PLANT_HEIGHT, CURRENT_STAGE)
                if btn_rects["EXIT"].collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Bingrow")
    clock  = pygame.time.Clock()
    start_music()

    while True:
        result = show_menu(screen, clock)
        if result is None:
            break

        action, player, height, stage = result

        if action in ("continue", "new_game"):
            from stage import show_stage_screen
            show_stage_screen(screen, clock,
                              player_name=player,
                              plant_height_cm=height,
                              current_stage=stage)

        elif action == "plant_height":
            from plant import show_plant_height_screen
            show_plant_height_screen(screen, clock,
                                     player_name=player,
                                     plant_height_cm=height)

        elif action == "settings":
            from settings import show_settings_screen
            show_settings_screen(screen, clock)
