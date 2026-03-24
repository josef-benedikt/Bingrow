import pygame
import sys
from database import save_account
from settings import show_settings_screen
from login import show_login_screen

# -- Init --
pygame.init()
pygame.mixer.init()

# -- Constants --
SCREEN_W, SCREEN_H = 1100, 620
FPS        = 60
BG_IMAGE   = "menubg.png"
MUSIC_FILE = "Main Menu and Stage Selection.mp3"

# -- Global Session Data --
PLAYER_NAME   = ""
PLAYER_PASS   = ""
STAGE_SCORES  = [0.0] * 50
CURRENT_STAGE = 1
HAS_SAVE_DATA = False   

WHITE, GREEN, GREEN_DARK = (255,255,255), (106,191,75), (78,154,46)
BROWN_LIGHT, BROWN_DARK  = (180,120,60), (100,60,20)
GRAY = (180, 180, 180)

try:
    FONT_BTN   = pygame.font.Font("LilitaOne-Regular.ttf", 16)
    FONT_SIGN  = pygame.font.Font("LilitaOne-Regular.ttf", 11)
    FONT_SIGN2 = pygame.font.Font("LilitaOne-Regular.ttf", 14)
except:
    FONT_BTN   = pygame.font.SysFont("Arial", 16, True)
    FONT_SIGN  = pygame.font.SysFont("Arial", 11)
    FONT_SIGN2 = pygame.font.SysFont("Arial", 14, True)

def start_music():
    if not pygame.mixer.music.get_busy():
        try:
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1)
        except: pass

def draw_rounded_rect(surface, color, rect, radius):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
    for p in [(x+radius, y+radius), (x+w-radius, y+radius), (x+radius, y+h-radius), (x+w-radius, y+h-radius)]:
        pygame.draw.circle(surface, color, p, radius)

def draw_pill_button(surface, text, cx, cy, w, h, color, dark, text_color, font):
    r = 15
    # White Border
    draw_rounded_rect(surface, WHITE, (cx - w//2 - 3, cy - h//2 - 3, w + 6, h + 6), r)
    # Shadow
    draw_rounded_rect(surface, dark, (cx - w//2, cy - h//2 + 2, w, h), r)
    # Button
    draw_rounded_rect(surface, color, (cx - w//2, cy - h//2, w, h), r)
    lbl = font.render(text, True, text_color)
    surface.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))
    return pygame.Rect(cx - w//2, cy - h//2, w, h)

def show_menu(screen, clock):
    try: 
        bg = pygame.image.load(BG_IMAGE)
        bg = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
    except: bg = None

    while True:
        mx, my = pygame.mouse.get_pos()
        btn_rects = {}
        if bg: screen.blit(bg, (0, 0))
        else: screen.fill((168, 216, 168))

        show_continue = (CURRENT_STAGE > 1 or sum(STAGE_SCORES) > 0)
        btns = ["CONTINUE", "NEW GAME", "PLANT HEIGHT", "SETTINGS"] if show_continue else ["NEW GAME", "SETTINGS"]
        y_start = 280 if show_continue else 340
        gap = 60

        for i, label in enumerate(btns):
            rect = draw_pill_button(screen, label, SCREEN_W//2, y_start + i*gap, 220, 44, GREEN, GREEN_DARK, WHITE, FONT_BTN)
            btn_rects[label] = rect

        btn_rects["EXIT"] = draw_pill_button(screen, "EXIT GAME", SCREEN_W - 100, SCREEN_H - 50, 140, 40, WHITE, GRAY, GREEN_DARK, FONT_BTN)

        screen.blit(FONT_SIGN.render("WELCOME BACK,", True, BROWN_LIGHT), (140, 455))
        screen.blit(FONT_SIGN2.render(f"{PLAYER_NAME.upper()}!", True, BROWN_DARK), (150, 475))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in btn_rects.items():
                    if rect.collidepoint(mx, my):
                        return label.lower().replace(" ", "_")

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    
    # Capture all 4 values from login
    login_res = show_login_screen(screen, clock)
    if login_res:
        PLAYER_NAME, STAGE_SCORES, CURRENT_STAGE, PLAYER_PASS = login_res
    else:
        pygame.quit(); sys.exit()

    start_music()

    while True:
        action = show_menu(screen, clock)
        if action in ("exit", "exit_game"):
            pygame.quit(); sys.exit()

        if action == "new_game":
            STAGE_SCORES = [0.0] * 50
            CURRENT_STAGE = 1
            save_account(PLAYER_NAME, PLAYER_PASS, STAGE_SCORES, CURRENT_STAGE)
            from stages import show_stage_screen
            res = show_stage_screen(screen, clock, PLAYER_NAME, STAGE_SCORES, CURRENT_STAGE, PLAYER_PASS)
            start_music()
            if res: PLAYER_NAME, STAGE_SCORES, CURRENT_STAGE, PLAYER_PASS = res

        elif action == "continue":
            from stages import show_stage_screen
            res = show_stage_screen(screen, clock, PLAYER_NAME, STAGE_SCORES, CURRENT_STAGE, PLAYER_PASS)
            start_music()
            if res: PLAYER_NAME, STAGE_SCORES, CURRENT_STAGE, PLAYER_PASS = res

        elif action == "plant_height":
            from plant import show_plant_height_screen
            show_plant_height_screen(screen, clock, PLAYER_NAME, sum(STAGE_SCORES))
            start_music()

        elif action == "settings":
            show_settings_screen(screen, clock)
            start_music()