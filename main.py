import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.5
FLAP_STRENGTH = -8
PIPE_SPEED = 3
PIPE_WIDTH = 60
PIPE_GAP = 150
GROUND_HEIGHT = 50

# Colors
SKY_COLOR = (113, 197, 207)
GROUND_COLOR = (222, 216, 149)
GROUND_LINE = (115, 191, 46)
BIRD_COLOR = (255, 204, 0)
BIRD_OUTLINE = (0, 0, 0)
WING_COLOR = (255, 255, 255)
BEAK_COLOR = (255, 102, 0)
PIPE_COLOR = (116, 191, 46)
PIPE_OUTLINE = (84, 56, 71)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (220, 80, 80)
BUTTON_HOVER = (255, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")
clock = pygame.time.Clock()

# Try loading fonts safely
try:
    font = pygame.font.SysFont('Arial', 36, bold=True)
    huge_font = pygame.font.SysFont('Arial', 48, bold=True)
except:
    font = pygame.font.Font(None, 36)
    huge_font = pygame.font.Font(None, 48)

class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.vel = 0
        self.radius = 15
        self.wing_dir = 1
        self.wing_angle = 0
        self.alive = True

    def jump(self):
        if self.alive:
            self.vel = FLAP_STRENGTH
            self.wing_angle = -30

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        
        # Wing animation
        if self.alive:
            self.wing_angle += 5 * self.wing_dir
            if self.wing_angle > 30 or self.wing_angle < -30:
                self.wing_dir *= -1
                
        # Ground collision
        if self.y >= HEIGHT - GROUND_HEIGHT - self.radius:
            self.y = HEIGHT - GROUND_HEIGHT - self.radius
            self.alive = False

    def draw(self, surface):
        # Create a surface for the bird to allow rotation
        bird_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        center = (20, 20)
        
        # Body
        pygame.draw.circle(bird_surf, BIRD_COLOR, center, self.radius)
        pygame.draw.circle(bird_surf, BIRD_OUTLINE, center, self.radius, 2)
        
        # Eye
        pygame.draw.circle(bird_surf, WHITE, (25, 15), 5)
        pygame.draw.circle(bird_surf, BLACK, (27, 15), 2)
        
        # Beak
        beak_pts = [(33, 20), (40, 22), (33, 26)]
        pygame.draw.polygon(bird_surf, BEAK_COLOR, beak_pts)
        pygame.draw.polygon(bird_surf, BIRD_OUTLINE, beak_pts, 1)
        
        # Wing
        wing_surf = pygame.Surface((20, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(wing_surf, WING_COLOR, (0, 0, 20, 10))
        pygame.draw.ellipse(wing_surf, BIRD_OUTLINE, (0, 0, 20, 10), 1)
        
        rotated_wing = pygame.transform.rotate(wing_surf, self.wing_angle)
        wing_rect = rotated_wing.get_rect(center=(15, 22))
        bird_surf.blit(rotated_wing, wing_rect)
        
        # Rotate whole bird based on velocity
        angle = max(-90, min(25, -self.vel * 3))
        if not self.alive:
            angle = -90
        
        rotated_bird = pygame.transform.rotate(bird_surf, angle)
        rect = rotated_bird.get_rect(center=(self.x, int(self.y)))
        surface.blit(rotated_bird, rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

class Pipe:
    def __init__(self):
        self.x = WIDTH
        self.gap_y = random.randint(150, HEIGHT - GROUND_HEIGHT - 150)
        self.passed = False
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP // 2)
        self.bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP // 2, PIPE_WIDTH, HEIGHT - (self.gap_y + PIPE_GAP // 2) - GROUND_HEIGHT)

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, surface):
        # Top Pipe
        pygame.draw.rect(surface, PIPE_COLOR, self.top_rect)
        pygame.draw.rect(surface, PIPE_OUTLINE, self.top_rect, 3)
        # Pipe cap top
        cap_rect_top = pygame.Rect(self.x - 4, self.top_rect.bottom - 20, PIPE_WIDTH + 8, 20)
        pygame.draw.rect(surface, PIPE_COLOR, cap_rect_top)
        pygame.draw.rect(surface, PIPE_OUTLINE, cap_rect_top, 3)

        # Bottom Pipe
        pygame.draw.rect(surface, PIPE_COLOR, self.bottom_rect)
        pygame.draw.rect(surface, PIPE_OUTLINE, self.bottom_rect, 3)
        # Pipe cap bottom
        cap_rect_bot = pygame.Rect(self.x - 4, self.bottom_rect.top, PIPE_WIDTH + 8, 20)
        pygame.draw.rect(surface, PIPE_COLOR, cap_rect_bot)
        pygame.draw.rect(surface, PIPE_OUTLINE, cap_rect_bot, 3)

class Background:
    def __init__(self):
        self.bg_x = 0
        # Generate some static clouds
        self.clouds = []
        for i in range(10):
            x = random.randint(0, WIDTH * 2)
            y = random.randint(50, HEIGHT // 2)
            self.clouds.append((x, y))

    def update(self, moving):
        if moving:
            self.bg_x -= 1
            if self.bg_x <= -WIDTH:
                self.bg_x = 0

    def draw(self, surface):
        # Fill sky
        surface.fill(SKY_COLOR)
        
        # Draw clouds
        for cx, cy in self.clouds:
            x_pos = (cx + self.bg_x) % (WIDTH * 2) - 50
            if x_pos < WIDTH + 50:
                pygame.draw.circle(surface, WHITE, (x_pos, cy), 20)
                pygame.draw.circle(surface, WHITE, (x_pos + 15, cy - 10), 25)
                pygame.draw.circle(surface, WHITE, (x_pos + 30, cy), 20)
                
        # Draw ground
        ground_rect = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
        pygame.draw.rect(surface, GROUND_COLOR, ground_rect)
        pygame.draw.rect(surface, GROUND_LINE, (0, HEIGHT - GROUND_HEIGHT, WIDTH, 10))

def draw_text(text, font, color, x, y, outline=True):
    if outline:
        outline_surface = font.render(text, True, BLACK)
        screen.blit(outline_surface, outline_surface.get_rect(center=(x-2, y-2)))
        screen.blit(outline_surface, outline_surface.get_rect(center=(x+2, y-2)))
        screen.blit(outline_surface, outline_surface.get_rect(center=(x-2, y+2)))
        screen.blit(outline_surface, outline_surface.get_rect(center=(x+2, y+2)))
    
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, text_surface.get_rect(center=(x, y)))

def draw_button(x, y, w, h, text, mouse_pos):
    rect = pygame.Rect(x, y, w, h)
    color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 3, border_radius=10)
    
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))
    return rect

def main():
    bird = Bird()
    pipes = []
    bg = Background()
    score = 0
    state = "START" # START, PLAYING, GAME_OVER
    
    pipe_timer = 0

    running = True
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if state == "START":
                        state = "PLAYING"
                        bird.jump()
                    elif state == "PLAYING" and bird.alive:
                        bird.jump()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "GAME_OVER":
                    btn_rect = pygame.Rect(WIDTH//2 - 75, HEIGHT//2 + 50, 150, 50)
                    if btn_rect.collidepoint(mouse_pos):
                        # Restart game
                        bird = Bird()
                        pipes = []
                        score = 0
                        state = "PLAYING"
                        bird.jump()

        if state == "PLAYING" and bird.alive:
            bird.update()
            bg.update(True)
            
            pipe_timer += 1
            if pipe_timer >= 90: # Spawn pipe every 1.5 seconds
                pipes.append(Pipe())
                pipe_timer = 0
                
            for pipe in pipes:
                pipe.update()
                
                # Collision detection
                bird_rect = bird.get_rect()
                if bird_rect.colliderect(pipe.top_rect) or bird_rect.colliderect(pipe.bottom_rect):
                    bird.alive = False
                
                # Scoring
                if not pipe.passed and pipe.x < bird.x:
                    score += 1
                    pipe.passed = True
            
            # Remove off-screen pipes
            pipes = [p for p in pipes if p.x + PIPE_WIDTH > 0]
            
            # Ceiling collision
            if bird.y < 0:
                bird.y = 0
                bird.vel = 0
                
        elif state == "PLAYING" and not bird.alive:
            bird.update() # Keep falling
            if bird.y >= HEIGHT - GROUND_HEIGHT - bird.radius:
                state = "GAME_OVER"

        # Rendering
        bg.draw(screen)
        for pipe in pipes:
            pipe.draw(screen)
        bird.draw(screen)
        
        if state == "START":
            draw_text("FLAPPY BIRD", huge_font, WHITE, WIDTH//2, HEIGHT//3)
            draw_text("Press SPACE to Start", font, WHITE, WIDTH//2, HEIGHT//2)
            
        elif state == "PLAYING" or state == "GAME_OVER":
            draw_text(str(score), huge_font, WHITE, WIDTH//2, 50)
            
        if state == "GAME_OVER":
            draw_text("GAME OVER", huge_font, BUTTON_COLOR, WIDTH//2, HEIGHT//3)
            draw_button(WIDTH//2 - 75, HEIGHT//2 + 50, 150, 50, "Restart", mouse_pos)
            
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
