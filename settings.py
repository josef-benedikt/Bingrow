"""
settings.py  -  Bingrow  (Settings Screen)

STANDALONE - no external variables needed.

HOW IT'S CALLED FROM menu.py:
    from settings import show_settings_screen
    show_settings_screen(screen, clock)

ASSETS (same folder as this .py file):
    settingsbg.png
    Gameplay Music.mp3
"""

import pygame
import sys

# ── Init ───────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 620
FPS        = 60
BG_IMAGE   = "settingsbg.png"
MUSIC_FILE = "Main Menu and Stage Selection.mp3"

# Colours
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GREEN      = (106, 191,  75)
GREEN_DARK = (78,  154,  46)
YELLOW     = (212, 232,  74)
PURPLE     = (168,  85, 200)
GRAY       = (180, 180, 180)

# Slider settings
SLIDER_W  = 420
SLIDER_H  = 24
KNOB_R    = 14
TRACK_CX  = SCREEN_W // 2
MUSIC_Y   = 255
SFX_Y     = 345

# Fonts
FONT_LABEL   = pygame.font.Font("LilitaOne-Regular.ttf", 17)
FONT_PCT     = pygame.font.Font("LilitaOne-Regular.ttf", 17)
FONT_VERSION = pygame.font.Font("LilitaOne-Regular.ttf",  9)
FONT_BACK    = pygame.font.Font("LilitaOne-Regular.ttf", 18)
FONT_CHECK   = pygame.font.Font("LilitaOne-Regular.ttf", 20)


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


def draw_back_btn(surface, font):
    cx, cy, size, r = 42, 42, 36, 8
    x0, y0 = cx - size//2, cy - size//2
    draw_rounded_rect(surface, GREEN_DARK, (x0+2, y0+2, size, size), r)
    draw_rounded_rect(surface, GREEN,      (x0,   y0,   size, size), r)
    label = font.render("<", True, WHITE)
    surface.blit(label, (cx - label.get_width()//2, cy - label.get_height()//2))
    return pygame.Rect(x0, y0, size, size)


def draw_slider(surface, cx, y, width, value):
    """Draw a slider track + knob. value = 0.0 to 1.0"""
    x0 = cx - width // 2
    track_y = y + SLIDER_H // 2
    fill_x  = x0 + int(value * width)

    # Track background (dark green)
    draw_rounded_rect(surface, GREEN_DARK,
                      (x0, y, width, SLIDER_H), SLIDER_H // 2)
    # Filled portion (bright green)
    if fill_x > x0:
        fill_w = fill_x - x0
        draw_rounded_rect(surface, GREEN,
                          (x0, y, max(fill_w, SLIDER_H), SLIDER_H), SLIDER_H // 2)

    # Knob
    kx = x0 + int(value * width)
    pygame.draw.circle(surface, WHITE,     (kx, track_y), KNOB_R)
    pygame.draw.circle(surface, GREEN_DARK,(kx, track_y), KNOB_R, 3)

    # Return knob rect and track x0 for hit detection
    return pygame.Rect(kx - KNOB_R, track_y - KNOB_R, KNOB_R*2, KNOB_R*2), x0


# ── Settings Screen ────────────────────────────────────────────────────────────
def show_settings_screen(screen, clock):

    bg         = load_image(BG_IMAGE, (SCREEN_W, SCREEN_H))
    music_vol = pygame.mixer.music.get_volume() 
    
    # SFX pulls from a global variable we create
    global GLOBAL_SFX_VOL
    if 'GLOBAL_SFX_VOL' not in globals():
        GLOBAL_SFX_VOL = 1.0 # Default if it's the first time opening settings
    
    sfx_vol = GLOBAL_SFX_VOL
    dragging = None
    dragging   = None   # "music" or "sfx"

    # Apply initial music volume
    try:
        pygame.mixer.music.set_volume(music_vol)
    except Exception:
        pass

    while True:
        mx, my = pygame.mouse.get_pos()

        # ── Draw ──────────────────────────────────────────────────────────────
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((184, 220, 240))

        # Purple border
        pygame.draw.rect(screen, PURPLE, (0, 0, SCREEN_W, SCREEN_H), 3)

        # Version
        v1 = FONT_VERSION.render("v.1.0.0", True, WHITE)
        v2 = FONT_VERSION.render("A BONDOX STUDIOS GAME", True, WHITE)
        screen.blit(v1, (SCREEN_W - v1.get_width() - 8,  6))
        screen.blit(v2, (SCREEN_W - v2.get_width() - 8, 16))

        # Back button
        back_rect = draw_back_btn(screen, FONT_BACK)

        track_x0 = TRACK_CX - SLIDER_W // 2

        # ── MUSIC slider ──────────────────────────────────────────────────────
        music_lbl = FONT_LABEL.render("MUSIC", True, WHITE)
        music_pct = FONT_PCT.render(f"{int(music_vol*100)}%", True, WHITE)
        screen.blit(music_lbl, (track_x0, MUSIC_Y - 26))
        screen.blit(music_pct, (track_x0 + SLIDER_W - music_pct.get_width(),
                                MUSIC_Y - 26))
        music_knob, _ = draw_slider(screen, TRACK_CX, MUSIC_Y, SLIDER_W, music_vol)
        music_track   = pygame.Rect(track_x0, MUSIC_Y, SLIDER_W, SLIDER_H)

        # ── SFX slider ────────────────────────────────────────────────────────
        sfx_lbl = FONT_LABEL.render("SFX", True, WHITE)
        sfx_pct = FONT_PCT.render(f"{int(sfx_vol*100)}%", True, WHITE)
        screen.blit(sfx_lbl, (track_x0, SFX_Y - 26))
        screen.blit(sfx_pct, (track_x0 + SLIDER_W - sfx_pct.get_width(),
                               SFX_Y - 26))
        sfx_knob, _ = draw_slider(screen, TRACK_CX, SFX_Y, SLIDER_W, sfx_vol)
        sfx_track   = pygame.Rect(track_x0, SFX_Y, SLIDER_W, SLIDER_H)

        # ── Dragging sliders ──────────────────────────────────────────────────
        if dragging == "music":
              raw = (mx - track_x0) / SLIDER_W
              music_vol = max(0.0, min(1.0, raw))
              pygame.mixer.music.set_volume(music_vol) # Directly updates the music player

        elif dragging == "sfx":
              raw = (mx - track_x0) / SLIDER_W
              sfx_vol = max(0.0, min(1.0, raw))
        # Update the global variable so it's remembered session-wide
              GLOBAL_SFX_VOL = sfx_vol

        pygame.display.flip()
        clock.tick(FPS)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mx, my):
                    return  # returns to menu.py

                if music_knob.collidepoint(mx, my) or music_track.collidepoint(mx, my):
                    dragging = "music"

                if sfx_knob.collidepoint(mx, my) or sfx_track.collidepoint(mx, my):
                    dragging = "sfx"

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = None


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Bingrow - Settings")
    clock = pygame.time.Clock()

    # Load music for testing
    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    show_settings_screen(screen, clock)
    pygame.quit()
