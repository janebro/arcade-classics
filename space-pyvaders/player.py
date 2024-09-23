import pygame
import random  # Add this import
from constants import WIDTH, HEIGHT, GREEN, PLAYER_SPEED, PLAYER_SHOOT_COOLDOWN


class Player:
    PLAYER_DESIGN = [
        "   ▄█▄   ",
        "  █████  ",
        "█████████",
        "█████████",
    ]
    PLAYER_COLOR = GREEN
    PLAYER_SIZE = (len(PLAYER_DESIGN[0]) * 5, len(PLAYER_DESIGN) * 5)

    def __init__(self):
        self.image = self.create_player_image()
        self.rect = self.image.get_rect()
        self.reset_position()
        self.speed = PLAYER_SPEED
        self.last_shot_time = 0
        self.is_dying = False
        self.death_frame = 0
        self.max_death_frames = 8  # Adjust for longer/shorter animation

    def create_player_image(self):
        pixel_size = self.PLAYER_SIZE[0] // len(self.PLAYER_DESIGN[0])
        image = pygame.Surface(self.PLAYER_SIZE, pygame.SRCALPHA)
        for y, row in enumerate(self.PLAYER_DESIGN):
            for x, pixel in enumerate(row):
                if pixel != " ":
                    pygame.draw.rect(
                        image,
                        self.PLAYER_COLOR,
                        (x * pixel_size, y * pixel_size, pixel_size, pixel_size),
                    )
        return image

    def reset_position(self):
        self.rect.midbottom = (WIDTH // 2, HEIGHT - 10)

    def create_death_frame(self, frame):
        image = pygame.Surface(self.PLAYER_SIZE, pygame.SRCALPHA)
        pixel_size = self.PLAYER_SIZE[0] // len(self.PLAYER_DESIGN[0])
        for y, row in enumerate(self.PLAYER_DESIGN):
            for x, pixel in enumerate(row):
                if pixel != " ":
                    if random.random() > frame / self.max_death_frames:
                        pygame.draw.rect(
                            image,
                            self.PLAYER_COLOR,
                            (x * pixel_size, y * pixel_size, pixel_size, pixel_size),
                        )
        return image

    def update(self, barriers):
        if self.is_dying:
            self.death_frame += 1
            if self.death_frame >= self.max_death_frames:
                return True  # Player is fully destroyed
            self.image = self.create_death_frame(self.death_frame)
            return False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

        # Check collision with barriers
        for barrier in barriers:
            if self.rect.colliderect(barrier.rect):
                if keys[pygame.K_LEFT]:
                    self.rect.left = barrier.rect.right
                elif keys[pygame.K_RIGHT]:
                    self.rect.right = barrier.rect.left

        return False

    def hit(self):
        self.is_dying = True

    def can_shoot(self):
        return pygame.time.get_ticks() - self.last_shot_time > PLAYER_SHOOT_COOLDOWN

    def shoot(self):
        self.last_shot_time = pygame.time.get_ticks()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
