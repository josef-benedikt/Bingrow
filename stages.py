"""
stage.py  -  Bingrow  (Stage Selector Screen)

STANDALONE - no external variables needed.

HOW IT'S CALLED FROM menu.py:
    from stage import show_stage_screen
    show_stage_screen(screen, clock, player_name, plant_height_cm, current_stage)

ASSETS (same folder as this .py file):
    stagebg.png
"""

import pygame
import sys

# ── Init ───────────────────────────────────────────────────────────────────────
pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 620
FPS            = 60
BG_IMAGE       = "stagebg.png"
TOTAL_STAGES   = 10
STAGES_PER_PAGE= 5

# Points awarded per stage (edit freely, index 0 = stage 1)
STAGE_POINTS = [5, 3, 8, 10, 15, 20, 25, 30, 40, 50]

# Colours
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
GREEN        = (106, 191,  75)
GREEN_DARK   = (78,  154,  46)
GREEN_TEXT   = (106, 191,  75)
YELLOW       = (212, 232,  74)
GRAY         = (136, 136, 136)
GRAY_DARK    = (100, 100, 100)
PURPLE       = (168,  85, 200)

# Card dimensions
CARD_W    = 160
CARD_H    = 170
CARD_GAP  = 20
CARD_R    = 18
CARDS_TOTAL_W = STAGES_PER_PAGE * CARD_W + (STAGES_PER_PAGE - 1) * CARD_GAP
CARDS_X   = (SCREEN_W - CARDS_TOTAL_W) // 2
CARDS_Y   = SCREEN_H // 2 - 10

# Fonts - Updated to match the bold/rounded look of the image
FONT_STAGE_NUM = pygame.font.SysFont("Arial Black", 80)
FONT_LABEL     = pygame.font.SysFont("Arial Black", 22)
FONT_SMALL     = pygame.font.SysFont("Arial Black", 12)
FONT_PTS       = pygame.font.SysFont("Arial Black", 16)
FONT_TITLE     = pygame.font.SysFont("Arial Black", 50)
FONT_HEIGHT    = pygame.font.SysFont("Arial Black", 22)
FONT_NAV       = pygame.font.SysFont("Arial Black", 24)


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None


def draw_rounded_rect(surface, color, rect, radius, width=0):
    x, y, w, h = rect
    if width == 0:
        pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
        pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
        pygame.draw.circle(surface, color, (x + radius,     y + radius),     radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + radius),     radius)
        pygame.draw.circle(surface, color, (x + radius,     y + h - radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)
    else:
        # Outline only
        draw_rounded_rect(surface, color, rect, radius, 0)


def draw_nav_btn(surface, cx, cy, text, font):
    r = 22
    draw_rounded_rect(surface, WHITE,      (cx-r-2, cy-r-2, r*2+4, r*2+4), 8)
    draw_rounded_rect(surface, GREEN,      (cx-r, cy-r, r*2, r*2), 8)
    label = font.render(text, True, WHITE)
    surface.blit(label, (cx - label.get_width()//2, cy - label.get_height()//2 - 2))
    return pygame.Rect(cx - r, cy - r, r*2, r*2)


def draw_back_btn(surface, font):
    cx, cy, size, r = 60, 60, 50, 10
    x0, y0 = cx - size//2, cy - size//2
    draw_rounded_rect(surface, WHITE,      (x0-3, y0-3, size+6, size+6), r+2)
    draw_rounded_rect(surface, GREEN,      (x0,   y0,   size, size), r)
    label = font.render("<", True, WHITE)
    surface.blit(label, (cx - label.get_width()//2, cy - label.get_height()//2 - 2))
    return pygame.Rect(x0, y0, size, size)


# ── Stage Screen ───────────────────────────────────────────────────────────────
def show_stage_screen(screen, clock, player_name, plant_height_cm,
                      current_stage, is_new_game=False):

    if is_new_game:
        current_stage   = 1
        plant_height_cm = 0

    completed_stages = set(range(1, current_stage))
    page = 0
    bg   = load_image(BG_IMAGE, (SCREEN_W, SCREEN_H))

    while True:
        mx, my = pygame.mouse.get_pos()

        # ── Draw ──────────────────────────────────────────────────────────────
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((168, 216, 234))

        # Purple border
        pygame.draw.rect(screen, PURPLE, (0, 0, SCREEN_W, SCREEN_H), 3)

        # Plant height top-right
        ph = FONT_HEIGHT.render(
            f"YOUR PLANT HEIGHT: {plant_height_cm} cm", True, WHITE)
        screen.blit(ph, (SCREEN_W - ph.get_width() - 30, 30))

        # "STAGE" title
        title = FONT_TITLE.render("STAGE", True, WHITE)
        # Simple outline/shadow effect for the title
        title_bg = FONT_TITLE.render("STAGE", True, GREEN_TEXT)
        screen.blit(title_bg, (SCREEN_W//2 - title.get_width()//2 + 2, 102))
        screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 100))

        # Back button
        back_rect = draw_back_btn(screen, FONT_NAV)

        # Stage cards
        card_rects = {}
        page_start = page * STAGES_PER_PAGE
        for i in range(STAGES_PER_PAGE):
            stage_num = page_start + i + 1
            if stage_num > TOTAL_STAGES:
                break

            cx = CARDS_X + i * (CARD_W + CARD_GAP) + CARD_W // 2
            cy = CARDS_Y
            x0 = cx - CARD_W // 2
            y0 = cy - CARD_H // 2

            is_unlocked  = stage_num <= current_stage
            is_completed = stage_num in completed_stages
            fill  = GREEN     if is_unlocked else (100, 100, 100)

            # Thick White border
            draw_rounded_rect(screen, WHITE,
                              (x0-6, y0-6, CARD_W+12, CARD_H+12), CARD_R+4)
            # Card face
            draw_rounded_rect(screen, fill,
                              (x0, y0, CARD_W, CARD_H), CARD_R)

            # Stage number
            num = FONT_STAGE_NUM.render(str(stage_num), True, WHITE)
            screen.blit(num, (cx - num.get_width()//2,
                              cy - num.get_height()//2 - 10))

            # Checkmark if completed
            if is_completed:
                # Circular background for checkmark like in the image
                pygame.draw.circle(screen, WHITE, (x0 + 25, y0 + CARD_H - 25), 14)
                chk = FONT_PTS.render("✓", True, GREEN)
                screen.blit(chk, (x0 + 25 - chk.get_width()//2, y0 + CARD_H - 25 - chk.get_height()//2))

            # +X cm label
            pts = STAGE_POINTS[stage_num-1] if stage_num <= len(STAGE_POINTS) else 0
            if is_unlocked:
                pts_label = FONT_PTS.render(f"+ {pts} cm", True, WHITE)
                screen.blit(pts_label,
                            (x0 + CARD_W - pts_label.get_width() - 15,
                             y0 + CARD_H - 35))

            if is_unlocked:
                card_rects[stage_num] = pygame.Rect(x0, y0, CARD_W, CARD_H)

        # Nav buttons
        nav_y = CARDS_Y + CARD_H // 2 + 75
        prev_rect = draw_nav_btn(screen, SCREEN_W//2 - 45, nav_y, "<", FONT_NAV)
        next_rect = draw_nav_btn(screen, SCREEN_W//2 + 45, nav_y, ">", FONT_NAV)

        pygame.display.flip()
        clock.tick(FPS)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mx, my):
                    return  

                if prev_rect.collidepoint(mx, my) and page > 0:
                    page -= 1

                max_page = (TOTAL_STAGES - 1) // STAGES_PER_PAGE
                if next_rect.collidepoint(mx, my) and page < max_page:
                    page += 1

                for stage_num, rect in card_rects.items():
                    if rect.collidepoint(mx, my):
                        try:
                            from gameplay import show_gameplay
                            show_gameplay(screen, clock,
                                         stage_number=stage_num,
                                         player_name=player_name,
                                         plant_height_cm=plant_height_cm)
                        except ImportError:
                            print(f"Stage {stage_num} clicked")


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Bingrow - Stage Select Test")
    clock = pygame.time.Clock()
    show_stage_screen(screen, clock,
                      player_name="Josef",
                      plant_height_cm=8,
                      current_stage=3)
    pygame.quit()#STAGE SELECTOR HERE!
