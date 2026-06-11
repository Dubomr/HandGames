import pygame
import random
import math


# ======================================================================
# FRUIT NINJA — Game Objects
# ======================================================================

class Fruit:
    def __init__(self, WIDTH, HEIGHT, fruit_images):
        self.kind   = random.choice(list(fruit_images.keys()))
        self.image  = fruit_images[self.kind]
        self.radius = self.image.get_width() // 2
        
        # We start from the bottom of the screen (invisible area). 
        # We start 150 pixels from the inside to prevent it from overflowing too much.
        self.x      = random.randint(150, WIDTH - 150)
        self.y      = HEIGHT + self.radius
        
        # --- NEW PHYSICS SYSTEM ---
        # Upward launch velocity (Negative values ​​move upwards on the Y-axis)
        self.speed_y = random.uniform(-15, -22) 
        
        # If the object is on the left side of the screen, curve it slightly to the right; if it's on the right side, curve it slightly to the left.
        if self.x < WIDTH // 2:
            self.speed_x = random.uniform(1, 4)
        else:
            self.speed_x = random.uniform(-4, -1)
            
        self.gravity = 0.4 # Gravity slows it down and makes it fall in each frame.
        self.is_sliced = False

    def update(self):
        # Update positions based on X and Y velocities
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Add gravity to the speed (slows the upward movement, then slows it down)
        self.speed_y += self.gravity

    def draw(self, screen):
        if not self.is_sliced:
            screen.blit(self.image,
                        (int(self.x - self.radius), int(self.y - self.radius)))


class Bomb:
    def __init__(self, WIDTH, HEIGHT, bomb_image):
        self.image  = bomb_image
        self.radius = bomb_image.get_width() // 2
        
       # We also launch the bombs from the bottom of the screen.
        self.x      = random.randint(150, WIDTH - 150)
        self.y      = HEIGHT + self.radius
        
        
        self.speed_y = random.uniform(-15, -22)
        
        if self.x < WIDTH // 2:
            self.speed_x = random.uniform(1, 4)
        else:
            self.speed_x = random.uniform(-4, -1)
            
        self.gravity = 0.4

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity

    def draw(self, screen):
        screen.blit(self.image,
                    (int(self.x - self.radius), int(self.y - self.radius)))
# ======================================================================
# PONG — Game Objects
# ======================================================================

class Paddle:
    def __init__(self, x, y, width, height, color):
        self.rect  = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 10

    def update(self, target_y, HEIGHT):
        self.rect.centery += (target_y - self.rect.centery) * 0.15
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=8)


class Ball:
    def __init__(self, WIDTH, HEIGHT):
        self.WIDTH  = WIDTH
        self.HEIGHT = HEIGHT
        self.radius = 12
        self.reset()

    def reset(self):
        self.x       = self.WIDTH  // 2
        self.y       = self.HEIGHT // 2
        self.speed_x = random.choice([-8,8])
        self.speed_y = random.choice([-8,8])

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Üst / alt duvar
        if self.y - self.radius <= 0:
            self.y       = self.radius
            self.speed_y = abs(self.speed_y)
        elif self.y + self.radius >= self.HEIGHT:
            self.y       = self.HEIGHT - self.radius
            self.speed_y = -abs(self.speed_y)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (200, 200, 200),
                           (int(self.x), int(self.y)), self.radius, 2)


# ======================================================================
# PONG — Power Up Parts
# ======================================================================

class PowerUp:
    """A power-up object that appears randomly on the screen and disappears when its time expires."""

    TYPES = {
        "big_ball":    {"color": (255, 120,  40), "label": "THE BALL IS GROWING",   "desc": "It makes the ball bigger."},
        "fast_ball":   {"color": (255,  50,  50), "label": "FAST BALL",   "desc": "It speeds up the ball."},
        "wide_paddle": {"color": ( 50, 200, 255), "label": "WIDE RACKET", "desc": "It extends the rackets"},
    }

    def __init__(self, WIDTH, HEIGHT):
        self.kind     = random.choice(list(self.TYPES.keys()))
        self.x        = random.randint(120, WIDTH  - 120)
        self.y        = random.randint(80,  HEIGHT - 80)
        self.radius   = 20
        self.lifetime = 300          # 5 seconds 60 fps
        self.color    = self.TYPES[self.kind]["color"]
        self.label    = self.TYPES[self.kind]["label"]
        self._font    = None         # Lazy init (pygame is ready)

    # ------------------------------------------------------------------ #
    def _get_font(self):
        if self._font is None:
            self._font = pygame.font.SysFont("impact", 14)
        return self._font

    def update(self):
        self.lifetime -= 1

    def is_expired(self):
        return self.lifetime <= 0

    def draw(self, screen):
        # Blinks in the last 60 frames
        if self.lifetime < 60 and (self.lifetime // 8) % 2 == 0:
            return

        # Pulse effect
        pulse  = 1.0 + 0.18 * math.sin(pygame.time.get_ticks() * 0.006)
        radius = int(self.radius * pulse)

        # Outer glitter ring
        glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 60),
                           (radius * 2, radius * 2), radius + 8)
        screen.blit(glow_surf,
                    (self.x - radius * 2, self.y - radius * 2))

        # Main circle
        pygame.draw.circle(screen, self.color,        (self.x, self.y), radius)
        pygame.draw.circle(screen, (255, 255, 255),   (self.x, self.y), radius, 3)

        
        font = self._get_font()
        txt  = font.render(self.label, True, (255, 255, 255))
        screen.blit(txt, (self.x - txt.get_width() // 2,
                          self.y + radius + 5))

        # Remaining time bar (below the circle)
        bar_w_full = self.radius * 3
        bar_w      = int((self.lifetime / 300) * bar_w_full)
        bar_x      = self.x - bar_w_full // 2
        bar_y      = self.y + radius + 22
        pygame.draw.rect(screen, (60, 60, 60),  (bar_x, bar_y, bar_w_full, 5), border_radius=3)
        pygame.draw.rect(screen, self.color,    (bar_x, bar_y, bar_w,      5), border_radius=3)        