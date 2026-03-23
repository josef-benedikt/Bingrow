import pygame
import sys
import random
import time

# Initialize PyGame, Font, and Audio Mixer
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Custom Event for when a music track finishes playing
MUSIC_END = pygame.USEREVENT + 1

# Constants (Internal Virtual Resolution)
VIRTUAL_WIDTH = 1920
VIRTUAL_HEIGHT = 1080
FPS = 60

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_STAMP = (154, 192, 86) # #9ac056
COLOR_RED = (220, 60, 60) 
COLOR_DIM = (0, 0, 0, 180)

def calculate_difficulty(stage_number):
    """Calculates scaling difficulty based on the stage number."""
    session_time = max(45.0, 180.0 * (0.98 ** (stage_number - 1)))
    reaction_time = max(0.85, 7 * (0.98 ** (stage_number - 1)))
    point_multiplier = 1.0 + (stage_number * 0.1)
    return session_time, reaction_time, point_multiplier

def render_outlined_text(surface, text, font, text_color, outline_color, pos, thickness=6):
    """Renders text with a simulated solid stroke/outline using a radial offset."""
    outline_surface = font.render(text, True, outline_color)
    text_surface = font.render(text, True, text_color)
    x, y = pos
    
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx*dx + dy*dy <= thickness*thickness:
                surface.blit(outline_surface, (x + dx, y + dy))
                
    surface.blit(text_surface, (x, y))

def render_outlined_text_centered(surface, text, font, text_color, outline_color, center_pos, thickness=6):
    """Renders centered text with a solid stroke/outline."""
    outline_surface = font.render(text, True, outline_color)
    text_surface = font.render(text, True, text_color)
    
    base_x = center_pos[0] - text_surface.get_width() // 2
    base_y = center_pos[1] - text_surface.get_height() // 2
    
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx*dx + dy*dy <= thickness*thickness:
                surface.blit(outline_surface, (base_x + dx, base_y + dy))
                
    surface.blit(text_surface, (base_x, base_y))

class BingoCard:
    def __init__(self, start_x, start_y, width, height):
        self.card_rect = pygame.Rect(start_x, start_y, width, height)
        
        # Perfect mathematical symmetry based on an 820x960 canvas
        self.cell_width = 142
        self.cell_height = 142
        
        # Precise grid offsets to match the line borders of the PNG
        self.grid_start_x = start_x + 56
        self.grid_start_y = start_y + 191
        
        self.numbers = self.generate_numbers()
        self.stamped = [[False for _ in range(5)] for _ in range(5)]
        self.stamped[2][2] = True # FREE space
        
        # Track individual alpha states for smooth 0.1s hover transitions
        self.alphas = [[255.0 for _ in range(5)] for _ in range(5)] 

    def generate_numbers(self):
        bounds = [(1, 18), (19, 36), (37, 54), (55, 72), (73, 90)]
        grid = []
        for col in range(5):
            col_nums = random.sample(range(bounds[col][0], bounds[col][1] + 1), 5)
            if col == 2:
                col_nums[2] = "FREE"
            grid.append(col_nums)
        return [[grid[col][row] for col in range(5)] for row in range(5)]

    def get_cell_rect(self, row, col):
        return pygame.Rect(
            self.grid_start_x + (col * self.cell_width), 
            self.grid_start_y + (row * self.cell_height), 
            self.cell_width, self.cell_height
        )

    def is_blackout(self):
        for row in range(5):
            for col in range(5):
                if not self.stamped[row][col]:
                    return False
        return True

def run_game(screen, stage_number, global_points):
    clock = pygame.time.Clock()
    display_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    
    # Fonts
    font_huge = pygame.font.Font("LilitaOne-Regular.ttf", 200)
    font_large = pygame.font.Font("LilitaOne-Regular.ttf", 90) 
    font_medium = pygame.font.Font("LilitaOne-Regular.ttf", 65) 
    font_small = pygame.font.Font("LilitaOne-Regular.ttf", 45) 

    # --- ASSET LOADING & SCALING ---
    try:
        bg_img = pygame.image.load("background.jpg").convert()
        card_img = pygame.transform.smoothscale(pygame.image.load("bingo_card.png").convert_alpha(), (820, 960))
        num_display_img = pygame.transform.smoothscale(pygame.image.load("bingo_number.png").convert_alpha(), (500, 500))
        quit_btn_img = pygame.transform.smoothscale(pygame.image.load("quit_button.png").convert_alpha(), (120, 120))
        pause_btn_img = pygame.transform.smoothscale(pygame.image.load("pause_button.png").convert_alpha(), (120, 120))
    except Exception as e:
        print(f"Error loading assets: {e}")
        return global_points, "quit"

    # --- MUSIC INITIALIZATION ---
    pygame.mixer.music.set_endevent(0) # Clear any previous event just in case
    try:
        pygame.mixer.music.load("Gameplay Music.mp3")
        pygame.mixer.music.play(-1) # Play indefinitely
    except Exception as e:
        print(f"Error loading gameplay music: {e}")

    # Helper function to properly stop music when leaving the session
    def exit_game(points, action):
        pygame.mixer.music.set_endevent(0)
        pygame.mixer.music.stop()
        return points, action

    # --- PRECISE ALIGNMENTS ---
    CARD_X, CARD_Y = 1040, 60
    TARGET_CIRCLE_CENTER = (520, 540)
    QUIT_CENTER = (105, 980) 
    PAUSE_CENTER = (245, 980)

    num_display_rect = num_display_img.get_rect(center=TARGET_CIRCLE_CENTER)
    quit_rect = quit_btn_img.get_rect(center=QUIT_CENTER)
    pause_rect = pause_btn_img.get_rect(center=PAUSE_CENTER)
    
    total_session_time, max_reaction_time, p_mult = calculate_difficulty(stage_number)
    session_time_left = total_session_time
    reaction_time_left = max_reaction_time
    
    card = BingoCard(CARD_X, CARD_Y, 820, 960)
    session_points = 0.0
    
    # --- RIGGED ROULETTE GENERATION ---
    card_nums = []
    for row in range(5):
        for col in range(5):
            if card.numbers[row][col] != "FREE":
                card_nums.append(card.numbers[row][col])
                
    other_nums = [n for n in range(1, 91) if n not in card_nums]
    random.shuffle(other_nums)
    
    max_guaranteed_draws = int(total_session_time / max_reaction_time)
    safe_fakes_count = min(66, max(0, max_guaranteed_draws - 24))
    
    first_batch = card_nums + other_nums[:safe_fakes_count]
    random.shuffle(first_batch)
    
    remaining_fakes = other_nums[safe_fakes_count:]
    random.shuffle(remaining_fakes)
    
    available_targets = remaining_fakes + first_batch
    current_target = available_targets.pop()
    
    state = "PLAYING" 
    
    # Fading & Animation States
    overlay_fade = 0.0
    overlay_state_memory = None
    quit_alpha = 255.0
    pause_alpha = 255.0
    floating_texts = []
    
    # Stamp Surface
    stamp_size = int(card.cell_width * 0.9)
    stamp_surface = pygame.Surface((stamp_size, stamp_size + 9), pygame.SRCALPHA)
    pygame.draw.circle(stamp_surface, (*COLOR_STAMP, 128), (stamp_size//2, stamp_size//2), stamp_size//2)

    # Helper function to trigger game over/completed and switch music
    def trigger_game_end(new_state):
        nonlocal state, overlay_state_memory
        state = new_state
        overlay_state_memory = new_state
        try:
            if new_state == "GAME_COMPLETED":
                pygame.mixer.music.load("Stage Completed.mp3")
            else:
                pygame.mixer.music.load("Stage Failed.mp3")
            pygame.mixer.music.play(0) # Play the jingle once
            pygame.mixer.music.set_endevent(MUSIC_END) # Wait for it to finish
        except Exception as e:
            print(f"Error loading end music: {e}")

    last_time = time.time()

    while True:
        dt = time.time() - last_time
        last_time = time.time()
        
        # --- SCALING CALCULATIONS ---
        current_w, current_h = screen.get_size()
        scale = min(current_w / VIRTUAL_WIDTH, current_h / VIRTUAL_HEIGHT)
        scaled_w = int(VIRTUAL_WIDTH * scale)
        scaled_h = int(VIRTUAL_HEIGHT * scale)
        offset_x = (current_w - scaled_w) // 2
        offset_y = (current_h - scaled_h) // 2
        
        real_mouse_pos = pygame.mouse.get_pos()
        virtual_mouse_pos = (
            (real_mouse_pos[0] - offset_x) / scale,
            (real_mouse_pos[1] - offset_y) / scale
        )

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle MUSIC_END event to resume gameplay music after the jingle
            elif event.type == MUSIC_END:
                pygame.mixer.music.set_endevent(0) # Clear event to prevent loops
                try:
                    pygame.mixer.music.load("Gameplay Music.mp3")
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"Error resuming gameplay music: {e}")
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "PLAYING":
                    if pause_rect.collidepoint(virtual_mouse_pos):
                        state = "PAUSED"
                        overlay_state_memory = "PAUSED"
                        pygame.mixer.music.pause() # Pause Music!
                    elif quit_rect.collidepoint(virtual_mouse_pos):
                        state = "QUIT_CONFIRM" 
                        overlay_state_memory = "QUIT_CONFIRM"
                        pygame.mixer.music.pause() # Pause Music!
                    
                    for row in range(5):
                        for col in range(5):
                            cell_rect = card.get_cell_rect(row, col)
                            if cell_rect.collidepoint(virtual_mouse_pos):
                                num = card.numbers[row][col]
                                if num == current_target and not card.stamped[row][col]:
                                    card.stamped[row][col] = True
                                    
                                    time_fraction = reaction_time_left / max_reaction_time
                                    points_earned = (0.5 * (time_fraction / 0.5)) * p_mult
                                    session_points += points_earned
                                    
                                    floating_texts.append({
                                        "points": points_earned,
                                        "timer": 1.1 
                                    })
                                    
                                    if card.is_blackout():
                                        trigger_game_end("GAME_COMPLETED")
                                    elif not available_targets:
                                        trigger_game_end("GAME_OVER")
                                    else:
                                        current_target = available_targets.pop()
                                        reaction_time_left = max_reaction_time
                                        
                # Overlay interactions (Active when overlay is mostly visible)
                elif state == "PAUSED" and overlay_fade > 0.8:
                    state = "PLAYING"
                    pygame.mixer.music.unpause() # Resume Music!
                    
                elif state == "QUIT_CONFIRM" and overlay_fade > 0.8:
                    yes_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 580, 500, 100)
                    no_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 720, 500, 100)
                    
                    if yes_rect.collidepoint(virtual_mouse_pos):
                        return exit_game(global_points, "quit")
                    elif no_rect.collidepoint(virtual_mouse_pos):
                        state = "PLAYING" 
                        pygame.mixer.music.unpause() # Resume Music!
                        
                elif state == "GAME_COMPLETED" and overlay_fade > 0.8:
                    play_again_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 580, 500, 100)
                    continue_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 720, 500, 100)
                    
                    if play_again_rect.collidepoint(virtual_mouse_pos):
                        return exit_game(global_points, "play_again")
                    elif continue_rect.collidepoint(virtual_mouse_pos):
                        return exit_game(global_points + session_points, "continue")
                        
                elif state == "GAME_OVER" and overlay_fade > 0.8:
                    play_again_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 580, 500, 100)
                    quit_rect_go = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 720, 500, 100)
                    
                    if play_again_rect.collidepoint(virtual_mouse_pos):
                        return exit_game(global_points, "play_again")
                    elif quit_rect_go.collidepoint(virtual_mouse_pos):
                        return exit_game(global_points, "quit")

        # --- GAME LOGIC ---
        if state == "PLAYING":
            session_time_left -= dt
            reaction_time_left -= dt
            
            if overlay_fade > 0:
                overlay_fade = max(0.0, overlay_fade - (dt * 10.0))
            
            if reaction_time_left <= 0:
                missed_required = False
                for r in range(5):
                    for c in range(5):
                        if card.numbers[r][c] == current_target and not card.stamped[r][c]:
                            missed_required = True
                            break
                    if missed_required:
                        break
                        
                if missed_required:
                    trigger_game_end("GAME_OVER")
                elif available_targets:
                    current_target = available_targets.pop()
                    reaction_time_left = max_reaction_time
                else:
                    trigger_game_end("GAME_OVER")
                
            if session_time_left <= 0 and state == "PLAYING":
                trigger_game_end("GAME_OVER")
        else:
            if overlay_fade < 1.0:
                overlay_fade = min(1.0, overlay_fade + (dt * 10.0))

        # --- HOVER ALPHA INTERPOLATION ---
        alpha_speed = 640.0 
        
        target_quit = 191 if state == "PLAYING" and quit_rect.collidepoint(virtual_mouse_pos) else 255
        if quit_alpha < target_quit: quit_alpha = min(quit_alpha + alpha_speed * dt, target_quit)
        elif quit_alpha > target_quit: quit_alpha = max(quit_alpha - alpha_speed * dt, target_quit)
        
        target_pause = 191 if state == "PLAYING" and pause_rect.collidepoint(virtual_mouse_pos) else 255
        if pause_alpha < target_pause: pause_alpha = min(pause_alpha + alpha_speed * dt, target_pause)
        elif pause_alpha > target_pause: pause_alpha = max(pause_alpha - alpha_speed * dt, target_pause)

        # --- DRAWING THE GAME (Background layer) ---
        display_surface.blit(bg_img, (0, 0))
        display_surface.blit(card_img, (CARD_X, CARD_Y))
        display_surface.blit(num_display_img, num_display_rect)
        
        quit_btn_img.set_alpha(int(quit_alpha))
        display_surface.blit(quit_btn_img, quit_rect)
        
        pause_btn_img.set_alpha(int(pause_alpha))
        display_surface.blit(pause_btn_img, pause_rect)
        
        # Main UI Text
        render_outlined_text(display_surface, f"STAGE {stage_number}", font_medium, COLOR_STAMP, COLOR_WHITE, (45, 45), thickness=6)
        
        time_sec = max(0, int(session_time_left))
        timer_str = f"{time_sec // 60:02d}:{time_sec % 60:02d} REMAINING"
        render_outlined_text(display_surface, timer_str, font_small, COLOR_STAMP, COLOR_WHITE, (45, 115), thickness=6)
        
        height_str = f"PLANT HEIGHT: {session_points:.2f} cm"
        render_outlined_text(display_surface, height_str, font_small, COLOR_STAMP, COLOR_WHITE, (45, 165), thickness=6)
        
        # Target Bingo Number (Optically centered for the font)
        target_text = font_huge.render(str(current_target), True, COLOR_STAMP)
        t_rect = target_text.get_rect(center=(TARGET_CIRCLE_CENTER[0], TARGET_CIRCLE_CENTER[1] - 5))
        display_surface.blit(target_text, t_rect)
        
        # --- REACTION TIME BAR WITH COLOR LERP ---
        time_fraction = max(0, reaction_time_left) / max_reaction_time
        bar_w = 300
        fill_w = int(bar_w * time_fraction)
        bar_x = TARGET_CIRCLE_CENTER[0] - (bar_w // 2)
        bar_y = TARGET_CIRCLE_CENTER[1] + 280
        
        current_r = int(COLOR_RED[0] + (COLOR_STAMP[0] - COLOR_RED[0]) * time_fraction)
        current_g = int(COLOR_RED[1] + (COLOR_STAMP[1] - COLOR_RED[1]) * time_fraction)
        current_b = int(COLOR_RED[2] + (COLOR_STAMP[2] - COLOR_RED[2]) * time_fraction)
        current_bar_color = (current_r, current_g, current_b)

        pygame.draw.rect(display_surface, COLOR_WHITE, (bar_x, bar_y, bar_w, 20), border_radius=10)
        pygame.draw.rect(display_surface, current_bar_color, (bar_x, bar_y, fill_w, 20), border_radius=10)

        # Bingo Grid
        for row in range(5):
            for col in range(5):
                cell_rect = card.get_cell_rect(row, col)
                num = card.numbers[row][col]
                
                if num != "FREE":
                    txt_surf = font_large.render(str(num), True, COLOR_STAMP)
                    
                    target_cell = 191 if not card.stamped[row][col] and state == "PLAYING" and cell_rect.collidepoint(virtual_mouse_pos) else 255
                    if card.alphas[row][col] < target_cell:
                        card.alphas[row][col] = min(card.alphas[row][col] + alpha_speed * dt, target_cell)
                    elif card.alphas[row][col] > target_cell:
                        card.alphas[row][col] = max(card.alphas[row][col] - alpha_speed * dt, target_cell)
                        
                    txt_surf.set_alpha(int(card.alphas[row][col]))
                    txt_rect = txt_surf.get_rect(center=(cell_rect.centerx, cell_rect.centery - 8))
                    display_surface.blit(txt_surf, txt_rect)
                
                if card.stamped[row][col]:
                    s_rect = stamp_surface.get_rect(center=cell_rect.center)
                    display_surface.blit(stamp_surface, s_rect.topleft)

        # Draw Floating Score Popups 
        for ft in floating_texts[:]:
            ft["timer"] -= dt
            if ft["timer"] <= 0:
                floating_texts.remove(ft)
                continue
                
            alpha = 255
            if ft["timer"] < 0.1:
                alpha = max(0, int((ft["timer"] / 0.1) * 255))
                
            if alpha > 0:
                temp_surf = pygame.Surface((800, 400), pygame.SRCALPHA)
                msg = f"+{ft['points']:.2f} cm!"
                render_outlined_text_centered(temp_surf, msg, font_large, COLOR_STAMP, COLOR_WHITE, (400, 200), thickness=6)
                temp_surf.set_alpha(alpha)
                display_surface.blit(temp_surf, (720 - 400, 140 - 200))

        # --- FADING OVERLAYS ---
        if overlay_fade > 0:
            dim_surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((0, 0, 0, int(180 * overlay_fade)))
            display_surface.blit(dim_surf, (0, 0))
            
            ui_surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)

            if overlay_state_memory == "PAUSED":
                pause_msg = font_huge.render("PAUSED", True, COLOR_WHITE)
                cont_msg = font_medium.render("CLICK ANYWHERE TO CONTINUE!", True, COLOR_STAMP)
                ui_surf.blit(pause_msg, pause_msg.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2 - 100)))
                ui_surf.blit(cont_msg, cont_msg.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2 + 100)))

            elif overlay_state_memory == "QUIT_CONFIRM":
                quit_msg = font_large.render("ARE YOU SURE YOU WANT TO QUIT?", True, COLOR_WHITE)
                sub_msg = font_small.render("YOU WILL LOSE ALL OF YOUR PROGRESS!", True, COLOR_RED)
                ui_surf.blit(quit_msg, quit_msg.get_rect(center=(VIRTUAL_WIDTH//2, 350)))
                ui_surf.blit(sub_msg, sub_msg.get_rect(center=(VIRTUAL_WIDTH//2, 450)))
                
                yes_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 580, 500, 100)
                no_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 720, 500, 100)
                
                yes_color = (255, 100, 100) if yes_rect.collidepoint(virtual_mouse_pos) else COLOR_RED
                no_color = (220, 220, 220) if no_rect.collidepoint(virtual_mouse_pos) else COLOR_WHITE
                
                pygame.draw.rect(ui_surf, yes_color, yes_rect, border_radius=20)
                pygame.draw.rect(ui_surf, no_color, no_rect, border_radius=20)
                
                yes_text = font_medium.render("YES", True, COLOR_WHITE)
                no_text = font_medium.render("NO", True, COLOR_STAMP)
                ui_surf.blit(yes_text, yes_text.get_rect(center=yes_rect.center))
                ui_surf.blit(no_text, no_text.get_rect(center=no_rect.center))

            elif overlay_state_memory == "GAME_COMPLETED":
                # Big Green Blackout Text
                over_msg = font_huge.render("BLACKOUT!", True, COLOR_STAMP)
                outline_msg = font_huge.render("BLACKOUT!", True, COLOR_WHITE)
                msg_rect = over_msg.get_rect(center=(VIRTUAL_WIDTH//2, 310))
                for dx in range(-6, 7):
                    for dy in range(-6, 7):
                        if dx*dx + dy*dy <= 36:
                            ui_surf.blit(outline_msg, (msg_rect.x + dx, msg_rect.y + dy))
                ui_surf.blit(over_msg, msg_rect)
                
                # Points Subtext
                sub_msg = font_large.render(f"YOUR PLANT GREW +{session_points:.2f} cm!", True, COLOR_WHITE)
                ui_surf.blit(sub_msg, sub_msg.get_rect(center=(VIRTUAL_WIDTH//2, 470)))
                
                play_again_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 580, 500, 100)
                continue_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 720, 500, 100)
                
                cont_color = (220, 220, 220) if continue_rect.collidepoint(virtual_mouse_pos) else COLOR_WHITE
                pa_color = (130, 170, 70) if play_again_rect.collidepoint(virtual_mouse_pos) else COLOR_STAMP
                
                pygame.draw.rect(ui_surf, pa_color, play_again_rect, border_radius=20)
                pygame.draw.rect(ui_surf, cont_color, continue_rect, border_radius=20)
                
                pa_text = font_medium.render("PLAY AGAIN", True, COLOR_WHITE)
                cont_text = font_medium.render("CONTINUE", True, COLOR_STAMP)
                ui_surf.blit(pa_text, pa_text.get_rect(center=play_again_rect.center))
                ui_surf.blit(cont_text, cont_text.get_rect(center=continue_rect.center))

            elif overlay_state_memory == "GAME_OVER":
                # Big Red Game Over Text
                over_msg = font_huge.render("GAME OVER!", True, COLOR_RED)
                outline_msg = font_huge.render("GAME OVER!", True, COLOR_WHITE)
                msg_rect = over_msg.get_rect(center=(VIRTUAL_WIDTH//2, 370))
                for dx in range(-6, 7):
                    for dy in range(-6, 7):
                        if dx*dx + dy*dy <= 36:
                            ui_surf.blit(outline_msg, (msg_rect.x + dx, msg_rect.y + dy))
                ui_surf.blit(over_msg, msg_rect)
                
                play_again_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 580, 500, 100)
                quit_rect_go = pygame.Rect(VIRTUAL_WIDTH//2 - 250, 720, 500, 100)
                
                quit_color = (255, 100, 100) if quit_rect_go.collidepoint(virtual_mouse_pos) else COLOR_RED
                pa_color = (130, 170, 70) if play_again_rect.collidepoint(virtual_mouse_pos) else COLOR_STAMP
                
                pygame.draw.rect(ui_surf, pa_color, play_again_rect, border_radius=20)
                pygame.draw.rect(ui_surf, quit_color, quit_rect_go, border_radius=20)
                
                pa_text = font_medium.render("PLAY AGAIN", True, COLOR_WHITE)
                qt_text = font_medium.render("QUIT", True, COLOR_WHITE)
                ui_surf.blit(pa_text, pa_text.get_rect(center=play_again_rect.center))
                ui_surf.blit(qt_text, qt_text.get_rect(center=quit_rect_go.center))

            ui_surf.set_alpha(int(255 * overlay_fade))
            display_surface.blit(ui_surf, (0, 0))

        # --- FINAL RENDER TO ACTUAL SCREEN ---
        screen.fill(COLOR_BLACK)
        scaled_display = pygame.transform.smoothscale(display_surface, (scaled_w, scaled_h))
        screen.blit(scaled_display, (offset_x, offset_y))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE) 
    pygame.display.set_caption("Bingrow")
    pts, action = run_game(screen, 666, 0)
    print(f"Ended: {action}, Points: {pts}")