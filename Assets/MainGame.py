import pygame
import random
import time
import os
import sys

# --- Configuration ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 450
LANE_HEIGHT = SCREEN_HEIGHT // 3
FPS = 60

# Colors
NIGHT_SKY = (10, 10, 30)
GRASS_GREEN = (34, 139, 34)
STAR_WHITE = (220, 220, 255)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pterodactyl Lane Runner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 22, bold=True)
        
        # 1. ROBUST ASSET LOADING
        # This determines the absolute path to the folder where this script is saved
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        assets_path = os.path.join(base_path, "Assets")
        
        try:
            # Loading your specific filenames
            ptero_path = os.path.join(assets_path, "Pterodactyl.png")
            coin_path = os.path.join(assets_path, "single-gold-coin.png")
            
            self.ptero_img = pygame.image.load(ptero_path).convert_alpha()
            self.ptero_img = pygame.transform.scale(self.ptero_img, (70, 50))
            
            self.coin_img = pygame.image.load(coin_path).convert_alpha()
            self.coin_img = pygame.transform.scale(self.coin_img, (30, 30))
            
        except Exception as e:
            print(f"\n--- FILE LOADING ERROR ---")
            print(f"Error: {e}")
            print(f"Path searched: {assets_path}")
            print(f"Required files: 'Pterodactyl.png' and 'single-gold-coin.png'")
            pygame.quit()
            sys.exit()

        self.reset_game()

    def reset_game(self):
        self.lane = 1  # 0, 1, or 2
        self.score = 0.0
        self.obstacles = []
        self.coins = []
        self.start_time = time.time()
        self.coin_bonus = 1.0  # Multiplied by 1.2 per coin
        self.game_over = False
        self.spawn_timer = 0
        # Background stars
        self.stars = [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT-30)] for _ in range(50)]

    def update(self):
        if self.game_over: return

        # 2. CALCULATE MULTIPLIERS
        # Time Mult: 1.5x every 30s
        elapsed = time.time() - self.start_time
        time_mult = 1.5 ** (int(elapsed // 30))

        # Manual Mult: Arrows
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            m_speed, m_points = 2.0, 3.0
        elif keys[pygame.K_LEFT]:
            m_speed, m_points = 0.5, 1/3
        else:
            m_speed, m_points = 1.0, 1.0

        # Compounding Speed and Display Multiplier
        current_speed = 7 * time_mult * m_speed
        self.display_total_speed = time_mult * m_speed

        # 3. PHYSICS & MOVEMENT
        # Move Stars
        for star in self.stars:
            star[0] -= current_speed * 0.1
            if star[0] < 0: star[0] = SCREEN_WIDTH

        # Spawning Logic
        self.spawn_timer += 1
        if self.spawn_timer > max(12, 45 // time_mult):
            lane = random.randint(0, 2)
            if random.random() < 0.75:
                self.obstacles.append(pygame.Rect(SCREEN_WIDTH, lane*LANE_HEIGHT + 35, 50, 40))
            else:
                self.coins.append(pygame.Rect(SCREEN_WIDTH, lane*LANE_HEIGHT + 45, 30, 30))
            self.spawn_timer = 0

        # Collision & Rect Handling
        ptero_rect = pygame.Rect(50, self.lane * LANE_HEIGHT + 35, 65, 45)

        for obs in self.obstacles[:]:
            obs.x -= current_speed
            if ptero_rect.colliderect(obs):
                self.game_over = True
            if obs.x < -100: self.obstacles.remove(obs)

        for c in self.coins[:]:
            c.x -= current_speed
            if ptero_rect.colliderect(c):
                self.coin_bonus *= 1.2
                self.coins.remove(c)
            elif c.x < -100: self.coins.remove(c)

        # 4. SCORING
        self.score += (10 / FPS) * m_points * self.coin_bonus

    def draw(self):
        # Draw Background
        self.screen.fill(NIGHT_SKY)
        for star in self.stars:
            pygame.draw.circle(self.screen, STAR_WHITE, (int(star[0]), int(star[1])), 1)
        pygame.draw.rect(self.screen, GRASS_GREEN, (0, SCREEN_HEIGHT-20, SCREEN_WIDTH, 20))

        # Draw Entities
        self.screen.blit(self.ptero_img, (50, self.lane * LANE_HEIGHT + 35))
        
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, (220, 50, 50), obs)
            
        for c in self.coins:
            self.screen.blit(self.coin_img, (c.x, c.y))

        # Draw UI
        ui_stats = [
            f"SCORE: {int(self.score)}",
            f"SPEED MULT: {self.display_total_speed:.2f}x",
            f"COIN BONUS: {self.coin_bonus:.2f}x"
        ]
        for i, text in enumerate(ui_stats):
            surf = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surf, (20, 20 + i*28))

        if self.game_over:
            msg = self.font.render("CRASHED! PRESS 'R' TO RESTART", True, (255, 255, 0))
            self.screen.blit(msg, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if not self.game_over:
                        if event.key == pygame.K_UP: self.lane = max(0, self.lane-1)
                        if event.key == pygame.K_DOWN: self.lane = min(2, self.lane+1)
                    elif event.key == pygame.K_r:
                        self.reset_game()
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    Game().run()

