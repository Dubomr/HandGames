import cv2
import pygame
import math
import os
from hand_tracking import HandTracker
from minigame_fruit import run_fruit_game
from minigame_pong import run_pong_game
from minigame_dodge import run_dodge_game
from ui_manager import MainMenu

def main():
    # Settings
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hand-Game Project")
    clock = pygame.time.Clock()

    cap = cv2.VideoCapture(0)
    cam_w, cam_h = 640, 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)
    tracker = HandTracker()

    pygame.mixer.init()
    """menu_music_path = os.path.join("assets", "menu_background.wav")

    if os.path.exists(menu_music_path):
        pygame.mixer.music.load(menu_music_path)
        pygame.mixer.music.play(-1)"""

    # Create the menu and variables
    menu = MainMenu(WIDTH, HEIGHT)
    player_x, player_y = WIDTH // 2, HEIGHT // 2
    target_x, target_y = WIDTH // 2, HEIGHT // 2
    smooth_factor = 0.25
    
    # Counter for election mechanics
    hover_timer = 0
    target_game = None

    running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
        success,img=cap.read()
        if success:
            img=cv2.flip(img,1)
            img,pos=tracker.get_finger_position(img)

            target_x,target_y=player_x,player_y
            if pos:
                target_x = int((pos[0] / cam_w) * WIDTH)
                target_y = int((pos[1] / cam_h) * HEIGHT)
        
        player_x += (target_x - player_x) * smooth_factor
        player_y += (target_y - player_y) * smooth_factor

        hovered_game = menu.draw_and_check(screen, player_x, player_y)
        if hovered_game:
            if hovered_game == target_game:
                hover_timer += 1
                
                # We draw a white arc around the finger.
                pygame.draw.arc(screen, (255, 255, 255), 
                                (int(player_x)-30, int(player_y)-30, 60, 60), 
                                0, (hover_timer / 60) * (2 * math.pi), 5)
                
                # If it stays on it for 60 frames (approximately 1 second), open the game.
                if hover_timer > 60: 
                    if target_game == "fruit":
                        
                        run_fruit_game(screen, clock, cap, tracker, WIDTH, HEIGHT)
                        
                        
                        player_x, player_y = WIDTH // 2, HEIGHT // 2 
                        hover_timer = 0
                        target_game = None
                    elif target_game == "pong":
                        run_pong_game(screen, clock, cap, tracker, WIDTH, HEIGHT)
                        
                        player_x, player_y = WIDTH // 2, HEIGHT // 2 
                        hover_timer = 0
                        target_game = None
                    elif target_game == "dodge":
                        run_dodge_game(screen, clock, cap, tracker, WIDTH, HEIGHT)
                        
                        player_x, player_y = WIDTH // 2, HEIGHT // 2 
                        hover_timer = 0
                        target_game = None
            else:
                target_game = hovered_game
                hover_timer = 0
        else:
            target_game = None
            hover_timer = 0
        pygame.draw.circle(screen, (0, 255, 100), (int(player_x), int(player_y)), 15)

        pygame.display.update()
        clock.tick(60)
    
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()