import pygame
import os

class MainMenu:
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont("impact", 70)
        self.font_btn = pygame.font.SysFont("impact", 40)
        
        btn_w, btn_h = 400, 80
        center_x = self.width // 2 - btn_w // 2
        
        self.buttons = [
            {"rect": pygame.Rect(center_x, 200, btn_w, btn_h), "text": "1. Fruit Ninja", "id": "fruit", "color": (200, 70, 70)},
            {"rect": pygame.Rect(center_x, 320, btn_w, btn_h), "text": "2. Pong (2 Hand)", "id": "pong", "color": (70, 150, 200)},
            {"rect": pygame.Rect(center_x, 440, btn_w, btn_h), "text": "3. AI Dodge", "id": "dodge", "color": (150,70,200)}
        ]

    def draw_and_check(self, screen, finger_x, finger_y):
        screen.fill((20, 25, 30))
        title = self.font_title.render("Hand Controlled Game", True, (255, 255, 255))
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
        selected_game = None
        for btn in self.buttons:
            rect = btn["rect"]
            color = btn["color"]
            if rect.collidepoint(finger_x, finger_y):
                color = (100, 255, 100) 
                selected_game = btn["id"]
            pygame.draw.rect(screen, color, rect, border_radius=20)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=20) 
            text = self.font_btn.render(btn["text"], True, (255, 255, 255))
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))
        return selected_game


def draw_lives(screen, lives, heart_image):
    
    margin = 20
    x_pos = screen.get_width() - margin - heart_image.get_width()
    y_pos = margin
    for i in range(lives):
        screen.blit(heart_image, (x_pos - (i * (heart_image.get_width() + 10)), y_pos))

class GameOverScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont("impact", 90)
        self.font_score = pygame.font.SysFont("impact", 50)
        self.font_btn = pygame.font.SysFont("impact", 40)
        
        
        btn_w, btn_h = 300, 70
        center_x = self.width // 2 - btn_w // 2
        
        self.buttons = [
            {"rect": pygame.Rect(center_x, 350, btn_w, btn_h), "text": "Restart", "id": "restart", "color": (70, 180, 70)},
            {"rect": pygame.Rect(center_x, 450, btn_w, btn_h), "text": "Back to Menu", "id": "quit", "color": (180, 70, 70)}
        ]

    def draw_and_check(self, screen, final_score, finger_x, finger_y):
       
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        
        title = self.font_title.render("GAME OVER", True, (255, 50, 50))
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        
        score_text = self.font_score.render(f"Final Score: {final_score}", True, (255, 255, 255))
        screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 220))

        selected_action = None

        for btn in self.buttons:
            rect = btn["rect"]
            color = btn["color"]
            
            if rect.collidepoint(finger_x, finger_y):
                color = (100, 255, 100) # Seçilince yeşil
                selected_action = btn["id"]

            pygame.draw.rect(screen, color, rect, border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=15) 
            
            text = self.font_btn.render(btn["text"], True, (255, 255, 255))
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        return selected_action
    
class PongGameOverScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont("impact", 75)
        self.font_btn = pygame.font.SysFont("impact", 40)
        
        
        btn_w, btn_h = 320, 70
        center_x = self.width // 2 - btn_w // 2
        
        self.buttons = [
            {"rect": pygame.Rect(center_x, 340, btn_w, btn_h), "text": "Restart", "id": "restart", "color": (70, 180, 70)},
            {"rect": pygame.Rect(center_x, 440, btn_w, btn_h), "text": "Back to Menu", "id": "quit", "color": (180, 70, 70)}
        ]

    def draw_and_check(self, screen, winner_text, mapped_hands):
        
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(190)
        overlay.fill((10, 10, 15))
        screen.blit(overlay, (0, 0))
        
        
        title = self.font_title.render(winner_text, True, (255, 215, 0)) 
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 140))

        selected_action = None
        hovered_hand_pos = None

        for btn in self.buttons:
            rect = btn["rect"]
            color = btn["color"]
            
            
            is_hovered = False
            for h_x, h_y in mapped_hands:
                if rect.collidepoint(h_x, h_y):
                    is_hovered = True
                    selected_action = btn["id"]
                    hovered_hand_pos = (h_x, h_y) 
                    break
            
            if is_hovered:
                color = (100, 255, 100) 

            pygame.draw.rect(screen, color, rect, border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=15) 
            
            text = self.font_btn.render(btn["text"], True, (255, 255, 255))
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        
        return selected_action, hovered_hand_pos
class PauseMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont("impact", 80)
        self.font_btn = pygame.font.SysFont("impact", 40)
        
        btn_w, btn_h = 300, 70
        center_x = self.width // 2 - btn_w // 2
        
        # Butonlar: Continue, Restart, Main Menu
        self.buttons = [
            {"rect": pygame.Rect(center_x, 230, btn_w, btn_h), "text": "Continue", "id": "continue", "color": (70, 150, 200)},
            {"rect": pygame.Rect(center_x, 340, btn_w, btn_h), "text": "Restart", "id": "restart", "color": (70, 180, 70)},
            {"rect": pygame.Rect(center_x, 450, btn_w, btn_h), "text": "Main Menu", "id": "menu", "color": (180, 70, 70)}
        ]

    def draw_and_check(self, screen, finger_x, finger_y):
        # Create a translucent surface to slightly darken the background.
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        screen.blit(overlay, (0, 0))
        
        # PAUSED Başlığı
        title = self.font_title.render("PAUSED", True, (255, 255, 255))
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        selected_action = None

        for btn in self.buttons:
            rect = btn["rect"]
            color = btn["color"]
            
            # If your finger is on the button
            if rect.collidepoint(finger_x, finger_y):
                color = (100, 255, 100) # Turns green when you hover over it
                selected_action = btn["id"]

            
            pygame.draw.rect(screen, color, rect, border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=15) 
            
            
            text = self.font_btn.render(btn["text"], True, (255, 255, 255))
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        return selected_action