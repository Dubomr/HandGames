import cv2
import pygame
import math
import os
from game_objects import Paddle, Ball, PowerUp
from ui_manager import PongGameOverScreen, PauseMenu


def run_pong_game(screen, clock, cap, tracker, WIDTH, HEIGHT):
    
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    def load_sound(name):
        path = os.path.join("assets", name)
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
        return None

    paddle_sound = load_sound("pong_paddle.wav")
    point_sound  = load_sound("pong_point.wav")

    cam_w, cam_h = 640, 480
    paddle_w, paddle_h = 20, 100

    left_paddle  = Paddle(30,          HEIGHT // 2 - paddle_h // 2,
                          paddle_w, paddle_h, (50, 255,  50))
    right_paddle = Paddle(WIDTH - 50,  HEIGHT // 2 - paddle_h // 2,
                          paddle_w, paddle_h, (50, 200, 255))
    ball = Ball(WIDTH, HEIGHT)

    score_left    = 0
    score_right   = 0
    target_y_left  = HEIGHT // 2
    target_y_right = HEIGHT // 2

    # --- POWER-UP SYSTEM VARIABLES ---
    power_ups          = []
    power_up_timer     = 0
    POWER_UP_INTERVAL  = 300        # Spawns approximately every 5 seconds (60fps)
    active_effects     = {}         
    original_ball_radius = None     

    effect_font = pygame.font.SysFont("impact", 22)

    # Pause Screen Variables
    pause_menu = PauseMenu(WIDTH, HEIGHT)
    is_paused = False
    pause_hover_timer = 0
    pause_target_action = None

    # Game over  Variables
    is_game_over  = False
    winner_text   = ""
    game_over_ui  = PongGameOverScreen(WIDTH, HEIGHT)
    hover_timer   = 0
    target_action = None
    font = pygame.font.SysFont("impact", 60)

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

        # Camera and hand control
        success, img = cap.read()
        mapped_hands = []

        if success:
            img = cv2.flip(img, 1)
            img, positions = tracker.get_multiple_positions(img)

            if positions:
                for pos in positions:
                    mx = int((pos[0] / cam_w) * WIDTH)
                    my = int((pos[1] / cam_h) * HEIGHT)
                    mapped_hands.append((mx, my))

                if not is_game_over and not is_paused:
                    if len(positions) == 1:
                        pos = positions[0]
                        mapped_y = int((pos[1] / cam_h) * HEIGHT)
                        if pos[0] < cam_w // 2:
                            target_y_left  = mapped_y
                        else:
                            target_y_right = mapped_y
                    elif len(positions) >= 2:
                        target_y_left  = int((positions[0][1] / cam_h) * HEIGHT)
                        target_y_right = int((positions[1][1] / cam_h) * HEIGHT)

        # ---------------------------------------------------------------- #
       # --- GAME LOGIC (Only if not paused and game not finished) ---
        if not is_game_over and not is_paused:
            left_paddle.update(target_y_left,  HEIGHT)
            right_paddle.update(target_y_right, HEIGHT)

            # --- Power-UP SPAWN ---
            power_up_timer += 1
            if power_up_timer >= POWER_UP_INTERVAL:
                power_ups.append(PowerUp(WIDTH, HEIGHT))
                power_up_timer = 0

            # --- UPDATE POWER-UPS & COLLISION ---
            for pu in power_ups[:]:
                pu.update()

                if pu.is_expired():
                    power_ups.remove(pu)
                    continue

                # The ball hitting the power-up
                dist = math.hypot(ball.x - pu.x, ball.y - pu.y)
                if dist < ball.radius + pu.radius:
                    active_effects[pu.kind] = 300   # 5 saniye aktif
                    power_ups.remove(pu)

                    if pu.kind == "big_ball":
                        if original_ball_radius is None:
                            original_ball_radius = ball.radius
                        ball.radius = original_ball_radius * 2

                    elif pu.kind == "fast_ball":
                        ball.speed_x *= 1.5
                        ball.speed_y *= 1.5

                    elif pu.kind == "wide_paddle":
                        left_paddle.rect.height  = int(paddle_h * 1.8)
                        right_paddle.rect.height = int(paddle_h * 1.8)

            # --- REDUCE ACTIVE EFFECTS & UNDO FINISHED EFFECT ---
            for effect in list(active_effects.keys()):
                active_effects[effect] -= 1
                if active_effects[effect] <= 0:
                    del active_effects[effect]

                    if effect == "big_ball" and original_ball_radius is not None:
                        ball.radius          = original_ball_radius
                        original_ball_radius = None

                    elif effect == "fast_ball":
                        spd = math.hypot(ball.speed_x, ball.speed_y)
                        if spd > 0:
                            ball.speed_x = (ball.speed_x / spd) * 8
                            ball.speed_y = (ball.speed_y / spd) * 8

                    elif effect == "wide_paddle":
                        left_paddle.rect.height  = paddle_h
                        right_paddle.rect.height = paddle_h

            # --- TOP Update ----
            ball.update()

            # Racket Collisions
            if (ball.x - ball.radius <= left_paddle.rect.right and
                    left_paddle.rect.top <= ball.y <= left_paddle.rect.bottom):
                ball.x       = left_paddle.rect.right + ball.radius
                ball.speed_x = abs(ball.speed_x)
                hit_pos      = (ball.y - left_paddle.rect.centery) / (left_paddle.rect.height / 2)
                ball.speed_y = hit_pos * 10
                if paddle_sound:
                    paddle_sound.play()

            elif (ball.x + ball.radius >= right_paddle.rect.left and
                      right_paddle.rect.top <= ball.y <= right_paddle.rect.bottom):
                ball.x       = right_paddle.rect.left - ball.radius
                ball.speed_x = -abs(ball.speed_x)
                hit_pos      = (ball.y - right_paddle.rect.centery) / (right_paddle.rect.height / 2)
                ball.speed_y = hit_pos * 10
                if paddle_sound:
                    paddle_sound.play()

            # Skor
            if ball.x < 0:
                score_right += 1
                ball.reset()
                
                _reset_effects(ball, left_paddle, right_paddle,
                               active_effects, original_ball_radius, paddle_h)
                original_ball_radius = None
                active_effects.clear()
                if point_sound:
                    point_sound.play()

            elif ball.x > WIDTH:
                score_left += 1
                ball.reset()
                _reset_effects(ball, left_paddle, right_paddle,
                               active_effects, original_ball_radius, paddle_h)
                original_ball_radius = None
                active_effects.clear()
                if point_sound:
                    point_sound.play()

            if score_left >= 7:
                is_game_over = True
                winner_text  = "SOL OYUNCU KAZANDI!"
            elif score_right >= 7:
                is_game_over = True
                winner_text  = "SAĞ OYUNCU KAZANDI!"

        # ---------------------------------------------------------------- #
        # Draw
        screen.fill((15, 15, 20))

        # Middle line
        for i in range(0, HEIGHT, 40):
            pygame.draw.rect(screen, (40, 40, 50), (WIDTH // 2 - 2, i, 4, 20))

        # Draw power-ups (under the rackets & ball)
        for pu in power_ups:
            pu.draw(screen)

        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # Skors
        score_text_left  = font.render(str(score_left),  True, ( 50, 255,  50))
        score_text_right = font.render(str(score_right), True, ( 50, 200, 255))
        screen.blit(score_text_left,  (WIDTH // 4,      30))
        screen.blit(score_text_right, (WIDTH * 3 // 4,  30))

        # --- ACTIVE EFFECT INDICATOR ---
        for i, (eff, remaining) in enumerate(active_effects.items()):
            label = PowerUp.TYPES[eff]["label"]
            color = PowerUp.TYPES[eff]["color"]
            secs  = remaining // 60 + 1
            txt   = effect_font.render(f"⚡ {label}  {secs}s", True, color)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2,
                              HEIGHT - 40 - i * 28))

        # Pause Screen Menu
        if is_paused and not is_game_over:
            # Use the first hand detected to navigate the menu
            p_x, p_y = WIDTH // 2, HEIGHT // 2
            if mapped_hands:
                p_x, p_y = mapped_hands[0]

            action = pause_menu.draw_and_check(screen, p_x, p_y)
            if action:
                if action == pause_target_action:
                    pause_hover_timer += 1
                    pygame.draw.arc(
                        screen, (255, 255, 255),
                        (p_x - 30, p_y - 30, 60, 60),
                        0, (pause_hover_timer / 60) * (2 * math.pi), 5
                    )
                    
                    if pause_hover_timer > 60:
                        if action == "continue":
                            is_paused = False
                            pause_hover_timer = 0
                            pause_target_action = None
                        elif action == "restart":
                            score_left    = 0
                            score_right   = 0
                            power_ups     = []
                            power_up_timer = 0
                            active_effects.clear()
                            original_ball_radius = None
                            left_paddle.rect.height  = paddle_h
                            right_paddle.rect.height = paddle_h
                            ball.reset()
                            is_paused     = False
                            pause_hover_timer = 0
                            pause_target_action = None
                        elif action == "menu":
                            return True
                else:
                    pause_target_action = action
                    pause_hover_timer   = 0
            else:
                pause_target_action = None
                pause_hover_timer   = 0
            
            pygame.draw.circle(screen, (255, 255, 255), (p_x, p_y), 10)

        # --- GAME OVER ---
        elif is_game_over:
            action, active_hand = game_over_ui.draw_and_check(
                screen, winner_text, mapped_hands)

            if action and active_hand:
                if action == target_action:
                    hover_timer += 1
                    pygame.draw.arc(
                        screen, (255, 255, 255),
                        (active_hand[0] - 30, active_hand[1] - 30, 60, 60),
                        0, (hover_timer / 60) * (2 * math.pi), 5
                    )
                    if hover_timer > 60:
                        if action == "restart":
                            score_left    = 0
                            score_right   = 0
                            power_ups     = []
                            power_up_timer = 0
                            active_effects.clear()
                            original_ball_radius = None
                            left_paddle.rect.height  = paddle_h
                            right_paddle.rect.height = paddle_h
                            ball.reset()
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

        pygame.display.update()
        clock.tick(60)

    return False


# ======================================================================
# Helper: Clear effects when the score is reached.
# ======================================================================
def _reset_effects(ball, left_paddle, right_paddle,
                   active_effects, original_ball_radius, paddle_h):
    if "big_ball" in active_effects and original_ball_radius is not None:
        ball.radius = original_ball_radius

    if "wide_paddle" in active_effects:
        left_paddle.rect.height  = paddle_h
        right_paddle.rect.height = paddle_h