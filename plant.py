import pygame
import sys

SCREEN_W, SCREEN_H = 1100, 620
FPS = 60
TREE_IMAGES = ["tree1.png", "tree2.png", "tree3.png", "tree4.png", "tree5.png"]
HEIGHT_THRESHOLDS = [(3000, 4), (1000, 3), (500, 2), (100, 1), (0, 0)]
WHITE, GREEN, YELLOW, BLACK = (255,255,255), (106,191,75), (212,232,74), (0,0,0)

try:
    FONT_NAME    = pygame.font.Font("LilitaOne-Regular.ttf", 32)
    FONT_HEIGHT  = pygame.font.Font("LilitaOne-Regular.ttf", 48)
    FONT_BACK    = pygame.font.Font("LilitaOne-Regular.ttf", 36)
except:
    FONT_NAME    = pygame.font.SysFont("Arial", 32, True)
    FONT_HEIGHT  = pygame.font.SysFont("Arial", 48, True)
    FONT_BACK    = pygame.font.SysFont("Arial", 36, True)

def tree_index_for_height(cm):
    for threshold, idx in HEIGHT_THRESHOLDS:
        if cm >= threshold: return idx
    return 0

def draw_rounded_rect(surface, color, rect, radius):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
    for p in [(x+radius, y+radius), (x+w-radius, y+radius), (x+radius, y+h-radius), (x+w-radius, y+h-radius)]:
        pygame.draw.circle(surface, color, p, radius)

def show_plant_height_screen(screen, clock, player_name, plant_height_cm):
    idx = tree_index_for_height(plant_height_cm)
    try:
        tree_img = pygame.image.load(TREE_IMAGES[idx]).convert_alpha()
        tree_img = pygame.transform.scale(tree_img, (SCREEN_W, SCREEN_H))
    except: tree_img = None

    while True:
        mx, my = pygame.mouse.get_pos()
        if tree_img: screen.blit(tree_img, (0, 0))
        else: screen.fill((184, 220, 240))

        # Back Button with Border
        back_rect = pygame.Rect(30, 30, 55, 55)
        draw_rounded_rect(screen, WHITE, (back_rect.x-3, back_rect.y-3, 61, 61), 12)
        draw_rounded_rect(screen, GREEN, back_rect, 10)
        lbl = FONT_BACK.render("<", True, WHITE)
        screen.blit(lbl, (back_rect.centerx - lbl.get_width()//2, back_rect.centery - lbl.get_height()//2 - 2))

        label_x, label_y = SCREEN_W - 220, SCREEN_H - 140
        height_str = f"{plant_height_cm:.2f} cm"

        for offset, color in [(2, BLACK), (0, YELLOW)]:
            name_s = FONT_NAME.render(f"{player_name.upper()}'S PLANT", True, color if offset==0 else BLACK)
            ht_s   = FONT_HEIGHT.render(height_str, True, color)
            screen.blit(name_s, (label_x - name_s.get_width()//2 + offset, label_y + offset))
            screen.blit(ht_s,   (label_x - ht_s.get_width()//2 + offset, label_y + 40 + offset))

        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_rect.collidepoint(mx, my): return