import pygame
import sys
from database import verify_login, save_account, load_all_accounts

# -- Constants --
SCREEN_W, SCREEN_H = 1100, 620
WHITE  = (255, 255, 255)
GREEN  = (106, 191, 75)
BLACK  = (0, 0, 0)
GRAY   = (200, 200, 200)
RED    = (200, 0, 0)
GREEN_DARK = (78, 154, 46)

pygame.font.init()
try:
    FONT = pygame.font.Font("LilitaOne-Regular.ttf", 24)
    FONT_SMALL = pygame.font.Font("LilitaOne-Regular.ttf", 18)
except:
    FONT = pygame.font.SysFont("Arial", 24, True)
    FONT_SMALL = pygame.font.SysFont("Arial", 18)

def show_login_screen(screen, clock):
    user_text = ""
    pass_text = ""
    active_field = "user" # Tracks which box is being typed in
    error_msg = ""
    success_msg = ""

    while True:
        # Match the menu's background color
        screen.fill((168, 216, 168))
        
        # UI Rectangles
        user_rect = pygame.Rect(SCREEN_W//2 - 150, 200, 300, 50)
        pass_rect = pygame.Rect(SCREEN_W//2 - 150, 300, 300, 50)
        login_btn = pygame.Rect(SCREEN_W//2 - 155, 400, 150, 50)
        reg_btn   = pygame.Rect(SCREEN_W//2 + 5, 400, 150, 50)

        # Labels
        screen.blit(FONT.render("USERNAME:", True, BLACK), (user_rect.x, user_rect.y - 35))
        screen.blit(FONT.render("PASSWORD:", True, BLACK), (pass_rect.x, pass_rect.y - 35))
        
        # Input Boxes
        pygame.draw.rect(screen, WHITE, user_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK if active_field == "user" else GRAY, user_rect, 2, border_radius=10)
        
        pygame.draw.rect(screen, WHITE, pass_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK if active_field == "pass" else GRAY, pass_rect, 2, border_radius=10)

        # Render Inputted Text
        screen.blit(FONT.render(user_text, True, BLACK), (user_rect.x + 10, user_rect.y + 10))
        screen.blit(FONT.render("*" * len(pass_text), True, BLACK), (pass_rect.x + 10, pass_rect.y + 10))
        
        # Buttons (Login and Register)
        pygame.draw.rect(screen, GREEN, login_btn, border_radius=10)
        pygame.draw.rect(screen, GREEN_DARK, reg_btn, border_radius=10)
        
        login_lbl = FONT.render("LOGIN", True, WHITE)
        reg_lbl   = FONT.render("REGISTER", True, WHITE)
        screen.blit(login_lbl, (login_btn.centerx - login_lbl.get_width()//2, login_btn.centery - login_lbl.get_height()//2))
        screen.blit(reg_lbl, (reg_btn.centerx - reg_lbl.get_width()//2, reg_btn.centery - reg_lbl.get_height()//2))

        # Error/Success Messages
        if error_msg:
            err_surf = FONT_SMALL.render(error_msg, True, RED)
            screen.blit(err_surf, (SCREEN_W//2 - err_surf.get_width()//2, 470))
        if success_msg:
            suc_surf = FONT_SMALL.render(success_msg, True, GREEN_DARK)
            screen.blit(suc_surf, (SCREEN_W//2 - suc_surf.get_width()//2, 470))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if user_rect.collidepoint(event.pos): active_field = "user"
                if pass_rect.collidepoint(event.pos): active_field = "pass"
                
                # Handle Login Logic
                if login_btn.collidepoint(event.pos):
                    data = verify_login(user_text, pass_text)
                    if data:
                        # Returns 4 values to menu.py to prevent unpacking error
                        return user_text, data["stage_scores"], data["current_stage"], pass_text
                    else:
                        success_msg = ""
                        error_msg = "Invalid username or password!"
                
                # Handle Registration Logic
                if reg_btn.collidepoint(event.pos):
                    if len(user_text) >= 3 and len(pass_text) >= 3:
                        accounts = load_all_accounts()
                        if user_text in accounts:
                            error_msg = "Username already exists!"
                        else:
                            save_account(user_text, pass_text, [0.0]*50, 1)
                            error_msg = ""
                            success_msg = f"Account {user_text} registered! Please Login."
                    else:
                        error_msg = "Min. 3 characters required for both fields."

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if active_field == "user": user_text = user_text[:-1]
                    else: pass_text = pass_text[:-1]
                elif event.key == pygame.K_TAB:
                    active_field = "pass" if active_field == "user" else "user"
                elif event.key == pygame.K_RETURN:
                    # Trigger login on Enter key
                    data = verify_login(user_text, pass_text)
                    if data: return user_text, data["stage_scores"], data["current_stage"], pass_text
                else:
                    # Add character if limit not reached
                    if len(user_text if active_field == "user" else pass_text) < 15:
                        if event.unicode.isalnum() or event.unicode in "._-":
                            if active_field == "user": user_text += event.unicode
                            else: pass_text += event.unicode