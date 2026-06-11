import cv2
import pygame
import math
import random
import os
from game_objects import Fruit, Bomb
from ui_manager import draw_lives, GameOverScreen, PauseMenu

def run_fruit_game(screen, clock, cap, tracker, WIDTH, HEIGHT):
    
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    def load_sound(name):
        path = os.path.join("assets", name)
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
        return None

    # Load the sounds
    slice_sound = load_sound("fruit_slice.wav")
    bomb_sound  = load_sound("fruit_bomb.wav")

    cam_w, cam_h = 640, 480
    player_x, player_y = WIDTH // 2, HEIGHT // 2
    smooth_factor = 0.3
    trail_positions = []
    max_trail = 10

    fruits = []
    bombs  = []
    score  = 0
    lives  = 3
    is_game_over = False

    # Pause variables
    pause_menu = PauseMenu(WIDTH, HEIGHT)
    is_paused = False
    pause_hover_timer = 0
    pause_target_action = None

    # Combo system variables
    combo_count  = 0
    combo_timer  = 0
    COMBO_RESET_FRAMES = 90   # If the combo isn't interrupted within ~1.5 seconds, it will reset.

    hover_timer   = 0
    target_action = None

    # ------------------------------------------------------------------ #
    def load_image(name, size):
        path = os.path.join("assets", name)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        else:
            fallback = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.circle(fallback, (255, 100, 100),
                               (size[0] // 2, size[1] // 2), size[0] // 2)
            return fallback

    fruit_images = {
        "apple":       load_image("apple.png",       (80,  80)),
        "watermelon":  load_image("watermelon.png",  (120, 120)),
        "banana":      load_image("banana.png",      (70,  70)),
        "strawberry":  load_image("strawberry.png",  (70,  70)),
    }
    bomb_image  = load_image("bomb.png",  (85, 85))
    heart_image = load_image("heart.png", (40, 40))
    game_over_ui = GameOverScreen(WIDTH, HEIGHT)

    bg_path = os.path.join("assets", "wooden.png")
    if os.path.exists(bg_path):
        bg_image = pygame.image.load(bg_path).convert()
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    else:
        bg_image = None

    # Font
    font_impact  = pygame.font.SysFont("impact", 48)
    combo_font   = pygame.font.SysFont("impact", 70)

    # ------------------------------------------------------------------ #
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
                # Q for pause
                if event.key == pygame.K_q and not is_game_over:
                    is_paused = not is_paused

        # --- CAMERA (The cursor should be able to move even when the game is paused) ---
        success, img = cap.read()
        target_x, target_y = player_x, player_y
        if success:
            img = cv2.flip(img, 1)
            img, pos = tracker.get_finger_position(img)
            if pos:
                target_x = int((pos[0] / cam_w) * WIDTH)
                target_y = int((pos[1] / cam_h) * HEIGHT)

        player_x += (target_x - player_x) * smooth_factor
        player_y += (target_y - player_y) * smooth_factor

        trail_positions.append((int(player_x), int(player_y)))
        if len(trail_positions) > max_trail:
            trail_positions.pop(0)

        # --- GAME LOGIC (Only works if the game is not paused and has not ended) ---
        if not is_game_over and not is_paused:
            
            # --- COUNTDOWN COMBO COUNTER ---
            if combo_timer > 0:
                combo_timer -= 1
            else:
                combo_count = 0   

            # Fruit spawn
            if random.randint(1, 100) <= 2:
                fruits.append(Fruit(WIDTH, HEIGHT, fruit_images))

            # Bomba spawn
            if random.randint(1, 150) <= 1:
                bombs.append(Bomb(WIDTH, HEIGHT, bomb_image))

            # Update the fruits
            for fruit in fruits[:]:
                fruit.update()
                distance = math.hypot(player_x - fruit.x, player_y - fruit.y)

                if distance < fruit.radius + 15 and not fruit.is_sliced:
                    fruit.is_sliced = True

                    # --- COMBO LOGIC ---
                    combo_count += 1
                    combo_timer  = COMBO_RESET_FRAMES   # Sayacı yenile

                    if combo_count >= 5:
                        multiplier = 5
                    elif combo_count >= 3:
                        multiplier = 2
                    else:
                        multiplier = 1

                    score += 10 * multiplier

                    if slice_sound:
                        slice_sound.play()

                if fruit.y > HEIGHT + fruit.radius or fruit.is_sliced:
                    if fruit in fruits:
                        fruits.remove(fruit)

            # Update the bombs
            for bomb in bombs[:]:
                bomb.update()
                distance = math.hypot(player_x - bomb.x, player_y - bomb.y)

                if distance < bomb.radius + 15:
                    lives -= 1
                    bombs.remove(bomb)
                    if bomb_sound:
                        bomb_sound.play()
                    combo_count = 0   # Reset combo when hit by bomb
                    combo_timer = 0

                    if lives <= 0:
                        is_game_over = True

                if bomb.y > HEIGHT + bomb.radius:
                    if bomb in bombs:
                        bombs.remove(bomb)

        # Draw
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((40, 30, 30))

        if not is_game_over:
            for fruit in fruits:
                fruit.draw(screen)
            for bomb in bombs:
                bomb.draw(screen)

        if len(trail_positions) > 1:
            pygame.draw.lines(screen, (200, 255, 255), False, trail_positions, 8)

        # Skor
        score_shadow = font_impact.render(f"SKOR: {score}", True, (0, 0, 0))
        score_text   = font_impact.render(f"SKOR: {score}", True, (255, 200, 0))
        screen.blit(score_shadow, (22, 22))
        screen.blit(score_text,   (20, 20))

        # Lives
        draw_lives(screen, lives, heart_image)

        # --- COMBO INDICATOR ---
        if combo_count >= 3 and not is_game_over:
            if combo_count >= 5:
                combo_color = (255, 80, 0)    
                combo_label = f"COMBO x5!  +{10 * 5}"
            else:
                combo_color = (255, 220, 0)   # Sarı — 2x
                combo_label = f"COMBO x{combo_count}!  +{10 * 2}"

            
            pulse_y = int(math.sin(pygame.time.get_ticks() * 0.01) * 6)

            # Shadow
            shadow_surf = combo_font.render(combo_label, True, (0, 0, 0))
            combo_surf  = combo_font.render(combo_label, True, combo_color)

            cx = WIDTH  // 2 - combo_surf.get_width()  // 2
            cy = 40 + pulse_y

            screen.blit(shadow_surf, (cx + 3, cy + 3))
            screen.blit(combo_surf,  (cx,     cy))

            # Combo bar (how much time left)
            bar_w = int((combo_timer / COMBO_RESET_FRAMES) * 200)
            bar_x = WIDTH // 2 - 100
            bar_y = cy + combo_surf.get_height() + 6
            pygame.draw.rect(screen, (60, 60, 60),    (bar_x, bar_y, 200,   8), border_radius=4)
            pygame.draw.rect(screen, combo_color,     (bar_x, bar_y, bar_w, 8), border_radius=4)

        # Pause Screen
        if is_paused and not is_game_over:
            action = pause_menu.draw_and_check(screen, player_x, player_y)
            if action:
                if action == pause_target_action:
                    pause_hover_timer += 1
                    
                    pygame.draw.arc(
                        screen, (255, 255, 255),
                        (int(player_x) - 30, int(player_y) - 30, 60, 60),
                        0, (pause_hover_timer / 60) * (2 * math.pi), 5
                    )
                    
                    if pause_hover_timer > 60:    
                        if action == "continue":
                            is_paused = False
                            pause_hover_timer = 0
                            pause_target_action = None
                        elif action == "restart":
                            # Oyunu sıfırla
                            lives         = 3
                            score         = 0
                            combo_count   = 0
                            combo_timer   = 0
                            fruits        = []
                            bombs         = []
                            player_x, player_y = WIDTH // 2, HEIGHT // 2
                            is_paused     = False
                            pause_hover_timer = 0
                            pause_target_action = None
                        elif action == "menu":
                            return True  # Return the main menu
                else:
                    pause_target_action = action
                    pause_hover_timer   = 0
            else:
                pause_target_action = None
                pause_hover_timer   = 0

        # --- GAME OVER ---
        elif is_game_over:
            action = game_over_ui.draw_and_check(screen, score, player_x, player_y)
            if action:
                if action == target_action:
                    hover_timer += 1
                    pygame.draw.arc(
                        screen, (255, 255, 255),
                        (int(player_x) - 30, int(player_y) - 30, 60, 60),
                        0, (hover_timer / 60) * (2 * math.pi), 5
                    )
                    if hover_timer > 60:
                        if action == "restart":
                            lives         = 3
                            score         = 0
                            combo_count   = 0
                            combo_timer   = 0
                            fruits        = []
                            bombs         = []
                            player_x, player_y = WIDTH // 2, HEIGHT // 2
                            is_game_over  = False
                            hover_timer   = 0
                            target_action = None
                        elif action == "quit":
                            return True
                else:
                    target_action = action
                    hover_timer   = 0
            else:
                target_action = None
                hover_timer   = 0

        pygame.draw.circle(screen, (255, 255, 255), (int(player_x), int(player_y)), 10)
        pygame.display.update()
        clock.tick(60)

    return False