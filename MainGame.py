import pygame
import random
import time

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 450
LANE_HEIGHT = SCREEN_HEIGHT // 3
FPS = 60

# Colors
NIGHT_SKY = (15, 15, 35)
GRASS_GREEN = (34, 139, 34)
STAR_WHITE = (200, 200, 255)
GOLD = (255, 215, 0)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pterodactyl: Compound Speed")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 22, bold=True)
        # Generate some static stars for the background
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT-30)) for _ in range(50)]
        self.reset_game()

    def reset_game(self):
        self.lane = 1
        self.score = 0.0
        self.obstacles = []
        self.coins = []
        self.start_time = time.time()
        self.coin_bonus = 1.0  # Multiplied by 1.2 per coin
        self.game_over = False
        self.spawn_timer = 0

    def update(self):
        if self.game_over: return

        # 1. TIME MULTIPLIER (1.5x every 30 seconds)
        # 0s: 1.0x | 30s: 1.5x | 60s: 2.25x | 90s: 3.375x
        elapsed = time.time() - self.start_time
        time_mult = 1.5 ** (int(elapsed // 30))

        # 2. MANUAL MULTIPLIER (Arrows)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            manual_speed_mod = 2.0
            manual_point_mod = 3.0
        elif keys[pygame.K_LEFT]:
            manual_speed_mod = 0.5
            manual_point_mod = 1/3
        else:
            manual_speed_mod = 1.0
            manual_point_mod = 1.0

        # 3. COMPOUND CALCULATIONS
        # Speed compounds: Time * Manual
        current_speed = 7 * time_mult * manual_speed_mod
        
        # Scoring compounds: Base * Manual * Coin Multiplier
        # (Note: Time mult makes the game harder/faster, but usually manual/coins drive the score)
        point_gain = (10 / FPS) * manual_point_mod * self.coin_bonus

        # 4. Spawning
        self.spawn_timer += 1
        if self.spawn_timer > max(15, 45 // time_mult): # Spawns faster as time mult goes up
            lane = random.randint(0, 2)
            if random.random() < 0.7:
                self.obstacles.append(pygame.Rect(SCREEN_WIDTH, lane*LANE_HEIGHT + 35, 40, 40))
            else:
                self.coins.append(pygame.Rect(SCREEN_WIDTH, lane*LANE_HEIGHT + 45, 20, 20))
            self.spawn_timer = 0

        # 5. Physics & Collision
        player_rect = pygame.Rect(50, self.lane * LANE_HEIGHT + 35, 50, 40)

        for obs in self.obstacles[:]:
            obs.x -= current_speed
            if player_rect.colliderect(obs): self.game_over = True
            if obs.x < -50: self.obstacles.remove(obs)

        for coin in self.coins[:]:
            coin.x -= current_speed
            if player_rect.colliderect(coin):
                self.coin_bonus *= 1.2
                self.coins.remove(coin)
            elif coin.x < -50: self.coins.remove(coin)

        self.score += point_gain
        self.current_display_speed = time_mult * manual_speed_mod # For the UI

    def draw(self):
        self.screen.fill(NIGHT_SKY)
        for star in self.stars: pygame.draw.circle(self.screen, STAR_WHITE, star, 1)
        pygame.draw.rect(self.screen, GRASS_GREEN, (0, SCREEN_HEIGHT-15, SCREEN_WIDTH, 15))

        # Pterodactyl (Blue)
        pygame.draw.rect(self.screen, (0, 150, 255), (50, self.lane * LANE_HEIGHT + 35, 50, 40))

        for obs in self.obstacles: pygame.draw.rect(self.screen, (200, 50, 50), obs)
        for coin in self.coins: pygame.draw.circle(self.screen, GOLD, coin.center, 10)

        # Multiplier UI
        elapsed = int(time.time() - self.start_time) if not self.game_over else 0
        ui_lines = [
            f"SCORE: {int(self.score)}",
            f"TIME: {elapsed}s",
            f"TOTAL SPEED MULT: {self.current_display_speed:.2f}x",
            f"COIN BONUS: {self.coin_bonus:.2f}x"
        ]
        for i, line in enumerate(ui_lines):
            self.screen.blit(self.font.render(line, True, (255, 255, 255)), (20, 20 + i*25))

        if self.game_over:
            msg = self.font.render("GAME OVER - PRESS 'R' TO RESTART", True, (255, 255, 0))
            self.screen.blit(msg, (SCREEN_WIDTH//2-200, SCREEN_HEIGHT//2))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    if not self.game_over:
                        if event.key == pygame.K_UP: self.lane = max(0, self.lane-1)
                        if event.key == pygame.K_DOWN: self.lane = min(2, self.lane+1)
                    elif event.key == pygame.K_r: self.reset_game()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
