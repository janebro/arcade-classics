import pygame
from constants import *

BARRIER_DESIGN = [
    "    ██████████████    ",
    "  ██████████████████  ",
    " ████████████████████ ",
    "██████████████████████",
    "██████████████████████",
    "██████          ██████",
    "█████            █████",
    "█████            █████",
]


class Barrier:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BARRIER_SIZE[0], BARRIER_SIZE[1])
        self.color = BARRIER_COLOR
        self.pixels = self.create_pixel_array()
        self.pixel_size = BARRIER_SIZE[0] // len(BARRIER_DESIGN[0])

    def create_pixel_array(self):
        return [[1 if pixel == "█" else 0 for pixel in row] for row in BARRIER_DESIGN]

    def draw(self, screen):
        for y, row in enumerate(self.pixels):
            for x, pixel in enumerate(row):
                if pixel:
                    pygame.draw.rect(
                        screen,
                        self.color,
                        (
                            self.rect.x + x * self.pixel_size,
                            self.rect.y + y * self.pixel_size,
                            self.pixel_size,
                            self.pixel_size,
                        ),
                    )

    def check_collision(self, rect):
        collision_occurred = False
        collision_left = max(rect.left - self.rect.left, 0)
        collision_top = max(rect.top - self.rect.top, 0)
        collision_right = min(rect.right - self.rect.left, self.rect.width)
        collision_bottom = min(rect.bottom - self.rect.top, self.rect.height)

        for y in range(
            collision_top // self.pixel_size, collision_bottom // self.pixel_size + 1
        ):
            for x in range(
                collision_left // self.pixel_size,
                collision_right // self.pixel_size + 1,
            ):
                if 0 <= y < len(self.pixels) and 0 <= x < len(self.pixels[0]):
                    if self.pixels[y][x]:
                        self.pixels[y][x] = 0
                        collision_occurred = True

        return collision_occurred

    def is_destroyed(self):
        return all(not any(row) for row in self.pixels)
