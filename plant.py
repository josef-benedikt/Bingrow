"""
plant.py  -  Bingrow  (Plant Height Screen)

STANDALONE - no external variables needed.

HOW IT'S CALLED FROM menu.py:
    from plant import show_plant_height_screen
    show_plant_height_screen(screen, clock, player_name, plant_height_cm)

ASSETS (same folder as this .py file):
    tree1.png to tree5.png  (each includes its own background)
    Gameplay Music.mp3

HEIGHT THRESHOLDS (edit freely):
    tree1.png :    0 -   99 cm
    tree2.png :  100 -  499 cm
    tree3.png :  500 -  999 cm
    tree4.png : 1000 - 2999 cm
    tree5.png : 3000+      cm
"""

import pygame
import sys

# ── Init ───────────────────────────────────────────────────────────────────────
pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 620
FPS         = 60
TREE_IMAGES = ["tree1.png","tree2.png","tree3.png","tree4.png","tree5.png"]
MUSIC_FILE  = "Gameplay Music.mp3"

# Height thresholds (edit cm values freely, ordered highest first)
HEIGHT_THRESHOLDS = [
    (3000, 4),
    (1000, 3),
    (500,  2),
    (100,  1),
    (0,    0),
]

# Colours
WHITE      = (255, 255, 255)
GREEN      = (106, 191,  75)
GREEN_DARK = (78,  154,  46)
GREEN_TEXT = (106, 191,  75)
YELLOW     = (212, 232,  74)
PURPLE     = (168,  85, 200)
BLACK      = (0,   0,   0)

# Fonts
FONT_NAME    = pygame.font.SysFont("Arial", 22, bold=True)
FONT_HEIGHT  = pygame.font.SysFont("Arial", 18, bold=True)
FONT_VERSION = pygame.font.SysFont("Arial",  9, bold=True)
FONT_BACK    = pygame.font.SysFont("Arial", 18, bold=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None


def tree_index_for_height(cm):
    for threshold, idx in HEIGHT_THRESHOLDS:
        if cm >= threshold:
            return idx
    return 0


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


# ── Plant Height Screen ────────────────────────────────────────────────────────
def show_plant_height_screen(screen, clock, player_name, plant_height_cm):

    idx        = tree_index_for_height(plant_height_cm)
    tree_image = load_image(TREE_IMAGES[idx], (SCREEN_W, SCREEN_H))

    while True:
        mx, my = pygame.mouse.get_pos()

        # ── Draw ──────────────────────────────────────────────────────────────
        if tree_image:
            screen.blit(tree_image, (0, 0))
        else:
            screen.fill((184, 220, 240))

        # Purple border
        pygame.draw.rect(screen, PURPLE, (0, 0, SCREEN_W, SCREEN_H), 3)

        # Version label
        v1 = FONT_VERSION.render("v.1.0.0", True, WHITE)
        v2 = FONT_VERSION.render("A BONDOX STUDIOS GAME", True, WHITE)
        screen.blit(v1, (SCREEN_W - v1.get_width() - 8,  6))
        screen.blit(v2, (SCREEN_W - v2.get_width() - 8, 16))

        # Back button
        back_rect = draw_back_btn(screen, FONT_BACK)

        # Player name + height — bottom right beside the tree
        label_x = SCREEN_W - 200
        label_y = SCREEN_H - 120

        # Shadow
        shadow_name = FONT_NAME.render(
            f"{player_name.upper()}'S PLANT", True, BLACK)
        shadow_cm   = FONT_HEIGHT.render(
            f"{plant_height_cm:,} cm", True, BLACK)
        screen.blit(shadow_name, (label_x - shadow_name.get_width()//2 + 2,
                                  label_y + 2))
        screen.blit(shadow_cm,   (label_x - shadow_cm.get_width()//2 + 2,
                                  label_y + 38))

        # Coloured text
        name_surf = FONT_NAME.render(
            f"{player_name.upper()}'S PLANT", True, GREEN_TEXT)
        cm_surf   = FONT_HEIGHT.render(
            f"{plant_height_cm:,} cm", True, YELLOW)
        screen.blit(name_surf, (label_x - name_surf.get_width()//2,
                                label_y))
        screen.blit(cm_surf,   (label_x - cm_surf.get_width()//2,
                                label_y + 36))

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


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Bingrow - Plant Height Test")
    clock = pygame.time.Clock()
    show_plant_height_screen(screen, clock, "Josef", 3017)
    pygame.quit()#PLANT HEIGHT HERE!
