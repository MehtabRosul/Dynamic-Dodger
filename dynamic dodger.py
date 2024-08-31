import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dynamic Dodger")

# Load and scale assets dynamically
def load_and_scale_image(image_path, target_size):
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, target_size)
    return image

player_image = load_and_scale_image('player.png', (100, 100))
obstacle_image = load_and_scale_image('obstacle.png', (60, 60))
powerup_image = load_and_scale_image('powerup.png', (50, 50))

# Player setup
player_size = 100
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT - 2 * player_size
player_speed = 7

# Obstacle and power-up setup
obstacle_speed = 3  # Initial speed
powerup_speed = 3  # Initial speed
obstacles = []
powerups = []

# Score setup
score = 0
high_score_file = "dodger_high_score.txt"

# Check if the high score file exists
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as file:
        high_score = int(file.read().strip())
else:
    high_score = 0

# Font setup
font = pygame.font.Font(None, 36)

# Particle effects
particles = []

def add_particles(x, y, color, duration=20):
    for _ in range(10):
        particles.append([x, y, random.randint(-3, 3), random.randint(-3, 3), color, duration])

def draw_particles():
    for particle in particles:
        pygame.draw.circle(screen, particle[4], (particle[0], particle[1]), 3)
        particle[0] += particle[2]
        particle[1] += particle[3]
        particle[5] -= 1
    particles[:] = [particle for particle in particles if particle[5] > 0]

def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

# Main game function
def main():
    global player_x, player_y, score, high_score, obstacle_speed, powerup_speed
    clock = pygame.time.Clock()
    running = True
    game_active = False
    game_over = False
    speed_increment_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_active and not game_over:
                        game_active = True
                        score = 0
                        player_x = SCREEN_WIDTH // 2
                        player_y = SCREEN_HEIGHT - 2 * player_size
                        obstacles.clear()
                        powerups.clear()
                        particles.clear()
                        obstacle_speed = 3
                        powerup_speed = 3
                    if game_over:
                        game_over = False
                        game_active = True
                        score = 0
                        player_x = SCREEN_WIDTH // 2
                        player_y = SCREEN_HEIGHT - 2 * player_size
                        obstacles.clear()
                        powerups.clear()
                        particles.clear()
                        obstacle_speed = 3
                        powerup_speed = 3

        if game_active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_size:
                player_x += player_speed

            # Boundary checking
            if player_x < 0:
                player_x = 0
            if player_x > SCREEN_WIDTH - player_size:
                player_x = SCREEN_WIDTH - player_size

            # Gradually increase speed
            speed_increment_timer += 1
            if speed_increment_timer % 500 == 0:  # Increase speed every 500 frames
                obstacle_speed += 0.1
                powerup_speed += 0.1

            # Spawn obstacles
            if random.randint(1, 60) == 1:  # Reduced obstacle spawn frequency
                obstacles.append([random.randint(0, SCREEN_WIDTH - 50), 0, obstacle_speed])

            # Spawn power-ups
            if random.randint(1, 100) == 1:
                powerups.append([random.randint(0, SCREEN_WIDTH - 30), 0, powerup_speed])

            # Move obstacles
            for obstacle in obstacles:
                obstacle[1] += obstacle[2]
                if obstacle[1] > SCREEN_HEIGHT:
                    obstacles.remove(obstacle)

            # Move power-ups
            for powerup in powerups:
                powerup[1] += powerup[2]
                if powerup[1] > SCREEN_HEIGHT:
                    powerups.remove(powerup)

            # Check for collisions
            player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
            for obstacle in obstacles:
                obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], 60, 60)
                if check_collision(player_rect, obstacle_rect):
                    add_particles(player_x, player_y, RED, duration=20)
                    game_active = False
                    game_over = True
                    if score > high_score:
                        high_score = score

            for powerup in powerups:
                powerup_rect = pygame.Rect(powerup[0], powerup[1], 50, 50)
                if check_collision(player_rect, powerup_rect):
                    score += 1
                    add_particles(powerup[0], powerup[1], GREEN, duration=20)
                    powerups.remove(powerup)

            # Ensure power-ups and obstacles don't overlap
            for powerup in powerups:
                powerup_rect = pygame.Rect(powerup[0], powerup[1], 50, 50)
                for obstacle in obstacles:
                    obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], 60, 60)
                    if check_collision(powerup_rect, obstacle_rect):
                        powerups.remove(powerup)
                        break

            # Clear screen
            screen.fill(BLACK)

            # Draw player
            screen.blit(player_image, (player_x, player_y))

            # Draw obstacles
            for obstacle in obstacles:
                screen.blit(obstacle_image, (obstacle[0], obstacle[1]))

            # Draw power-ups
            for powerup in powerups:
                screen.blit(powerup_image, (powerup[0], powerup[1]))

            # Draw particles
            draw_particles()

            # Draw score
            score_text = font.render(f"Score: {score}", True, WHITE)
            high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 10, 10))

        elif game_over:
            screen.fill(BLACK)
            game_over_text = font.render("Game Over! Press SPACE to Restart", True, WHITE)
            score_text = font.render(f"Score: {score}", True, WHITE)
            high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
            screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

        else:
            # Start screen
            screen.fill(BLACK)
            start_text = font.render("Press SPACE to Start", True, WHITE)
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - start_text.get_height() // 2))

        # Update screen
        pygame.display.flip()
        clock.tick(60)

    # Save high score
    with open(high_score_file, "w") as file:
        file.write(str(high_score))

    pygame.quit()

if __name__ == "__main__":
    main()
