import pygame
import sys
from database import save_account

# -- Constants --
SCREEN_W, SCREEN_H = 1100, 620
FPS = 60
BG_IMAGE = "stagebg.png"
TOTAL_STAGES = 50           
STAGES_PER_PAGE = 5

WHITE, GREEN, GRAY, GREEN_DARK = (255, 255, 255), (106, 191, 75), (136, 136, 136), (78, 154, 46)

pygame.font.init()
FONT_MAIN = pygame.font.Font("LilitaOne-Regular.ttf", 36)
FONT_STG = pygame.font.Font("LilitaOne-Regular.ttf", 80)
FONT_INFO = pygame.font.Font("LilitaOne-Regular.ttf", 18)
FONT_SMALL = pygame.font.Font("LilitaOne-Regular.ttf", 14)

def draw_rounded_rect(surface, color, rect, radius):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x+radius, y, w-2*radius, h))
    pygame.draw.rect(surface, color, (x, y+radius, w, h - 2*radius))
    for p in [(x+radius, y+radius), (x+w-radius, y+radius), (x+radius, y+h-radius), (x+w-radius, y+h-radius)]:
        pygame.draw.circle(surface, color, p, radius)

def show_stage_screen(screen, clock, player_name, stage_scores, current_stage, player_pass):
    try:
        bg = pygame.image.load(BG_IMAGE).convert()
        bg = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
    except:
        bg = pygame.Surface((SCREEN_W, SCREEN_H))
        bg.fill((135, 206, 235))
    
    page = (current_stage - 1) // STAGES_PER_PAGE
    
    while True:
        mx, my = pygame.mouse.get_pos()
        screen.blit(bg, (0,0))

        total_height = sum(stage_scores)
        info_txt = FONT_INFO.render(f"YOUR PLANT HEIGHT: {total_height:.2f} cm", True, WHITE)
        screen.blit(info_txt, (SCREEN_W - info_txt.get_width() - 30, 30))

        # Back Button with Border
        back_rect = pygame.Rect(30, 30, 50, 50)
        draw_rounded_rect(screen, WHITE, (back_rect.x-3, back_rect.y-3, 56, 56), 12)
        draw_rounded_rect(screen, GREEN, back_rect, 10)
        screen.blit(FONT_MAIN.render("<", True, WHITE), (43, 33))

        # Nav Buttons with Border
        prev_rect = pygame.Rect(SCREEN_W//2 - 60, 480, 40, 40)
        next_rect = pygame.Rect(SCREEN_W//2 + 20, 480, 40, 40)
        
        for r in [prev_rect, next_rect]:
            draw_rounded_rect(screen, WHITE, (r.x-3, r.y-3, 46, 46), 10)
            draw_rounded_rect(screen, WHITE, r, 8)
            
        pygame.draw.polygon(screen, GREEN, [(prev_rect.centerx+5, prev_rect.centery-8), (prev_rect.centerx+5, prev_rect.centery+8), (prev_rect.centerx-5, prev_rect.centery)])
        pygame.draw.polygon(screen, GREEN, [(next_rect.centerx-5, next_rect.centery-8), (next_rect.centerx-5, next_rect.centery+8), (next_rect.centerx+5, next_rect.centery)])

        # Cards
        card_rects = {}
        start_idx = page * STAGES_PER_PAGE
        start_x = (SCREEN_W - (STAGES_PER_PAGE * 160 + 4 * 25)) // 2
        
        for i in range(STAGES_PER_PAGE):
            stage_num = start_idx + i + 1
            if stage_num > TOTAL_STAGES: break
            
            rect = pygame.Rect(start_x + i * 185, 260, 160, 200)
            card_rects[stage_num] = rect
            
            is_locked = stage_num > current_stage
            is_done   = stage_num < current_stage 
            
            draw_rounded_rect(screen, WHITE, (rect.x-4, rect.y-4, 168, 208), 15)
            color = GREEN if not is_locked else GRAY
            draw_rounded_rect(screen, color, rect, 15)
            
            num_txt = FONT_STG.render(str(stage_num), True, WHITE)
            screen.blit(num_txt, (rect.centerx - num_txt.get_width()//2, rect.centery - num_txt.get_height()//2))
            
            if is_done:
                this_score = stage_scores[stage_num - 1]
                pts_lbl = FONT_SMALL.render(f"+ {this_score:.2f} cm", True, WHITE)
                screen.blit(pts_lbl, (rect.right - pts_lbl.get_width() - 10, rect.bottom - 25))
                pygame.draw.circle(screen, WHITE, (rect.left + 20, rect.bottom - 20), 10)

        pygame.display.flip()
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(mx, my): 
                    return player_name, stage_scores, current_stage, player_pass
                if prev_rect.collidepoint(mx, my) and page > 0: page -= 1
                if next_rect.collidepoint(mx, my) and page < (TOTAL_STAGES - 1) // STAGES_PER_PAGE: page += 1
                
                for stage_num, rect in card_rects.items():
                    if rect.collidepoint(mx, my) and stage_num <= current_stage:
                        from game import run_game
                        earned_score, status = run_game(screen, stage_num, sum(stage_scores))
                        pygame.mixer.music.load("Main Menu and Stage Selection.mp3")
                        pygame.mixer.music.play(-1)
                        if status == "continue":
                            stage_scores[stage_num - 1] = float(earned_score)
                            if stage_num == current_stage:
                                current_stage += 1
                                page = (current_stage - 1) // STAGES_PER_PAGE
                            save_account(player_name, player_pass, stage_scores, current_stage)