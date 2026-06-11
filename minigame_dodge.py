import cv2
import pygame
import pickle
import pandas as pd
import random
import os
import math
from ui_manager import GameOverScreen, PauseMenu

def run_dodge_game(screen, clock, cap, tracker, WIDTH, HEIGHT):
    with open("gesture_model.pkl", "rb") as f:
        model = pickle.load(f)

    feature_columns = []
    for i in range(21):
        feature_columns.extend([f'x{i}', f'y{i}'])

    player_x = WIDTH // 2
    player_y = HEIGHT - 100
    player_radius = 25
    player_hp = 100
    score = 0
    
    shield_energy = 100
    dash_cooldown = 0
    invincible_frames = 0
    obstacles = []
    obstacle_spawn_timer = 0
    current_gesture = None
    
    gesture_names = {
        '0': 'FIST (Shield)', 
        '1': 'OPEN HAND (Ineffective State)', 
        '2': 'ONE FINGER (Dash Activated!)'
    }
    
   # --- PAUSE AND END-GAME VARIABLES ---
    is_game_over = False
    game_over_ui = GameOverScreen(WIDTH, HEIGHT)
    hover_timer = 0
    target_action = None

    pause_menu = PauseMenu(WIDTH, HEIGHT)
    is_paused = False
    pause_hover_timer = 0
    pause_target_action = None

    cursor_x, cursor_y = WIDTH // 2, HEIGHT // 2

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    def load_sound(name):
        path = os.path.join("assets", name)
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
        return None

    # Meteor sounds added
    meteor_sound = load_sound("dodge_meteor.wav")
    
    font_large = pygame.font.SysFont("impact", 50)
    font_small = pygame.font.SysFont("impact", 30)

    # Load Image
    def load_image(name):
        path = os.path.join("assets", name)
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
        return None

    # Background image
    bg_image = load_image("space.png")
    if bg_image:
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    # Space fighter image
    fighter_img_base = load_image("fighter.png")
    if fighter_img_base:
        fighter_img = pygame.transform.scale(fighter_img_base, (player_radius * 2, player_radius * 2))
    else:
        fighter_img = None

    meteor_img_base = load_image("meteor.png")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return True
                # PAUSE/RESUME WITH THE Q KEY
                if event.key == pygame.K_q and not is_game_over:
                    is_paused = not is_paused

        # --- CAMERA AND HAND TRACKING (Works to navigate the menu even when the game is paused) ---
        success, img = cap.read()
        if success:
            img = cv2.flip(img, 1)
            img_skeleton, wrist_x, wrist_y, ml_landmarks = tracker.get_dodge_data(img.copy())
            
            if wrist_x is not None and wrist_y is not None:
                cursor_x = int(wrist_x * WIDTH)
                cursor_y = int(wrist_y * HEIGHT)
                
       # --- GAME LOGIC (Only works if the game is not paused and has not ended) ---
        if not is_game_over and not is_paused:
            
            # Player moves
            player_x += (cursor_x - player_x) * 0.25
            player_x = max(player_radius, min(WIDTH - player_radius, player_x))

            # Motion Recognition (Machine Learning)
            if ml_landmarks:
                input_data = pd.DataFrame([ml_landmarks], columns=feature_columns)
                current_gesture = str(model.predict(input_data)[0])
            else:
                current_gesture = None

            # Shield Mechanics
            is_shield_active = False
            if current_gesture == '0' and shield_energy > 5:
                is_shield_active = True
                shield_energy -= 1.5
            else:
                shield_energy = min(100, shield_energy + 0.5)

            # Dash Mechanics
            if dash_cooldown > 0: dash_cooldown -= 1
            if invincible_frames > 0: invincible_frames -= 1

            if current_gesture == '2' and dash_cooldown == 0:
                invincible_frames = 20
                dash_cooldown = 90

            # Creating Barriers
            obstacle_spawn_timer += 1
            spawn_rate = max(10, 30 - (score // 10))
            if obstacle_spawn_timer >= spawn_rate:
                obs_size = random.randint(20, 45)
                
                # Adjust the image according to the size of each meteor.
                scaled_meteor = None
                if meteor_img_base:
                    scaled_meteor = pygame.transform.scale(meteor_img_base, (obs_size * 2, obs_size * 2))

                obstacles.append({
                    'x': random.randint(obs_size, WIDTH - obs_size),
                    'y': -obs_size,
                    'speed': random.randint(5, 10) + (score // 20),
                    'size': obs_size,
                    'img': scaled_meteor 
                })
                obstacle_spawn_timer = 0

            # Obstacle Movement and Collision Control
            for obs in obstacles[:]:
                obs['y'] += obs['speed']
                
                if obs['y'] > HEIGHT + obs['size']:
                    obstacles.remove(obs)
                    score += 1
                    continue

                dist = math.hypot(player_x - obs['x'], player_y - obs['y'])
                if dist < player_radius + obs['size']:
                    if invincible_frames > 0:
                        pass
                    elif is_shield_active:
                        obstacles.remove(obs)
                    else:
                        player_hp -= 20
                        obstacles.remove(obs)
                        if meteor_sound:
                            meteor_sound.play()

            player_hp = max(0, player_hp)
            if player_hp <= 0:
                is_game_over = True

        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((20, 20, 30))

        # Meteor drawings
        for obs in obstacles:
            if obs.get('img'):
                screen.blit(obs['img'], (int(obs['x'] - obs['size']), int(obs['y'] - obs['size'])))
            else:
                pygame.draw.circle(screen, (255, 60, 60), (int(obs['x']), int(obs['y'])), obs['size'])
                pygame.draw.circle(screen, (150, 0, 0), (int(obs['x']), int(obs['y'])), obs['size'], 3)

        # OFighter drawing
        if player_hp > 0:
            if fighter_img:
                # A slight flicker or blink for the invincible effect.
                if invincible_frames > 0 and invincible_frames % 2 == 0:
                    pass # Dash instant flashing effect
                else:
                    screen.blit(fighter_img, (int(player_x - player_radius), int(player_y - player_radius)))
            else:
                if invincible_frames > 0:
                    pygame.draw.circle(screen, (255, 255, 255), (int(player_x), int(player_y)), player_radius)
                else:
                    pygame.draw.circle(screen, (0, 255, 150), (int(player_x), int(player_y)), player_radius)
                    pygame.draw.circle(screen, (255, 255, 255), (int(player_x), int(player_y)), player_radius, 3)

            #If the shield is open, we continue drawing a blue energetic sphere around it. 
            # It's good to see the player's current state even if it's paused.
            if not is_game_over:
                if current_gesture == '0' and shield_energy > 5 and not is_paused:
                    pygame.draw.circle(screen, (0, 180, 255), (int(player_x), int(player_y)), player_radius + 15, 4)
                elif hasattr(locals(), 'is_shield_active') and is_shield_active:
                     pygame.draw.circle(screen, (0, 180, 255), (int(player_x), int(player_y)), player_radius + 15, 4)

        # UI Bar and Skors
        if not is_game_over:
            pygame.draw.rect(screen, (100, 20, 20), (30, 30, 200, 20), border_radius=5)
            pygame.draw.rect(screen, (0, 255, 100), (30, 30, player_hp * 2, 20), border_radius=5)
            
            pygame.draw.rect(screen, (40, 40, 60), (30, 60, 200, 10), border_radius=3)
            pygame.draw.rect(screen, (0, 150, 255), (30, 60, shield_energy * 2, 10), border_radius=3)

            score_text = font_large.render(f"SKOR: {score}", True, (255, 215, 0))
            screen.blit(score_text, (WIDTH - score_text.get_width() - 30, 20))

            if current_gesture:
                txt = font_small.render(gesture_names.get(current_gesture, ""), True, (255, 255, 255))
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT - 50))

        # Pause screen
        if is_paused and not is_game_over:
            action = pause_menu.draw_and_check(screen, cursor_x, cursor_y)
            if action:
                if action == pause_target_action:
                    pause_hover_timer += 1
                    pygame.draw.arc(screen, (255, 255, 255), 
                                    (cursor_x - 30, cursor_y - 30, 60, 60), 
                                    0, (pause_hover_timer / 60) * (2 * math.pi), 5)
                    
                    if pause_hover_timer > 60:
                        if action == "continue":
                            is_paused = False
                            pause_hover_timer = 0
                            pause_target_action = None
                        elif action == "restart":
                            player_hp = 100
                            score = 0
                            shield_energy = 100
                            dash_cooldown = 0
                            invincible_frames = 0
                            obstacles = []
                            player_x = WIDTH // 2
                            is_paused = False
                            pause_hover_timer = 0
                            pause_target_action = None
                        elif action == "menu":
                            return True
                else:
                    pause_target_action = action
                    pause_hover_timer = 0
            else:
                pause_target_action = None
                pause_hover_timer = 0
            
            # Draw the cursor in the pause menu
            pygame.draw.circle(screen, (255, 255, 255), (cursor_x, cursor_y), 10)

        #game over screem
        elif is_game_over:
            action = game_over_ui.draw_and_check(screen, score, cursor_x, cursor_y)
            if action:
                if action == target_action:
                    hover_timer += 1
                    pygame.draw.arc(screen, (255, 255, 255), 
                                    (cursor_x - 30, cursor_y - 30, 60, 60), 
                                    0, (hover_timer / 60) * (2 * math.pi), 5)
                    
                    if hover_timer > 60: 
                        if action == "restart":
                            player_hp = 100
                            score = 0
                            shield_energy = 100
                            dash_cooldown = 0
                            invincible_frames = 0
                            obstacles = []
                            player_x = WIDTH // 2
                            is_game_over = False
                            hover_timer = 0
                            target_action = None
                        elif action == "quit":
                            return True
                else:
                    target_action = action
                    hover_timer = 0
            else:
                target_action = None
                hover_timer = 0

            pygame.draw.circle(screen, (255, 255, 255), (cursor_x, cursor_y), 10)

        pygame.display.update()
        clock.tick(60)
        
    return False