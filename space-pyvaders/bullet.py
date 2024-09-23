import pygame
from constants import *


class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x - BULLET_SIZE[0] // 2, y, *BULLET_SIZE)
        self.speed = PLAYER_BULLET_SPEED if direction == -1 else ENEMY_BULLET_SPEED
        self.direction = direction

    def update(self):
        self.rect.y += self.speed * self.direction

    def draw(self, screen):
        color = GREEN if self.direction == -1 else WHITE
        pygame.draw.rect(screen, color, self.rect)
