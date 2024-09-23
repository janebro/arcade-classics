import pygame
import random
from constants import (
    WIDTH,
    HEIGHT,
    WHITE,
    ENEMY_SPEED,
    ENEMY_SPEED_INCREASE,
    ENEMY_DROP,
    ENEMY_ROWS,
    ENEMY_COLS,
    ENEMY_SPACING_X,
    ENEMY_SPACING_Y,
    ENEMY_START_Y,
    ENEMY_MOVE_SOUNDS,
)
from bullet import Bullet


class Enemy:
    ENEMY_DESIGNS = {
        "small": [
            [
                "   ▄█▄   ",
                "  █████  ",
                " ██ █ ██ ",
                " ███████ ",
            ],
            [
                "   ▄█▄   ",
                "  █████  ",
                " ██ █ ██ ",
                " █ ███ █ ",
            ],
        ],
        "medium": [
            [
                " ▄███▄ ",
                "███████",
                "█ ███ █",
                "█ █ █ █",
                "  █ █  ",
            ],
            [
                " ▄███▄ ",
                "███████",
                "█ ███ █",
                "  █ █  ",
                " █   █ ",
            ],
        ],
        "large": [
            [
                "  ▄██▄  ",
                " ██████ ",
                "███  ███",
                "████████",
                "██ ██ ██",
                "█ █  █ █",
            ],
            [
                "  ▄██▄  ",
                " ██████ ",
                "███  ███",
                "████████",
                "██    ██",
                "██ ██ ██",
            ],
        ],
    }

    ENEMY_COLORS = {
        "small": WHITE,
        "medium": WHITE,
        "large": WHITE,
    }

    def __init__(self, x, y, enemy_type):
        self.enemy_type = enemy_type
        self.designs = self.ENEMY_DESIGNS[enemy_type]
        self.color = self.ENEMY_COLORS[enemy_type]
        self.current_design = 0
        # Calculate ENEMY_SIZE based on the design
        self.ENEMY_SIZE = (len(self.designs[0][0]) * 5, len(self.designs[0]) * 5)
        self.image = self.create_enemy_image()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_dying = False
        self.death_frame = 0
        self.max_death_frames = 8

    def create_enemy_image(self):
        design = self.designs[self.current_design]
        image = pygame.Surface(self.ENEMY_SIZE, pygame.SRCALPHA)
        pixel_size = self.ENEMY_SIZE[0] // len(design[0])

        for y, row in enumerate(design):
            for x, pixel in enumerate(row):
                if pixel != " ":
                    pygame.draw.rect(
                        image,
                        self.color,
                        (x * pixel_size, y * pixel_size, pixel_size, pixel_size),
                    )
        return image

    def create_death_frame(self, frame):
        image = pygame.Surface(self.ENEMY_SIZE, pygame.SRCALPHA)
        pixel_size = self.ENEMY_SIZE[0] // len(self.designs[0][0])
        for y, row in enumerate(self.designs[self.current_design]):
            for x, pixel in enumerate(row):
                if pixel != " ":
                    if random.random() > frame / self.max_death_frames:
                        pygame.draw.rect(
                            image,
                            self.color,
                            (x * pixel_size, y * pixel_size, pixel_size, pixel_size),
                        )
        return image

    def update(self):
        if self.is_dying:
            self.death_frame += 1
            if self.death_frame >= self.max_death_frames:
                return True  # Enemy is fully destroyed
            self.image = self.create_death_frame(self.death_frame)
        return False

    def animate(self):
        if not self.is_dying:
            self.current_design = (self.current_design + 1) % len(self.designs)
            self.image = self.create_enemy_image()

    def hit(self):
        self.is_dying = True

    def move(self, dx, dy):
        if not self.is_dying:
            self.rect.move_ip(dx, dy)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class EnemyFleet:
    def __init__(self, level):
        self.rows = []
        self.direction = 1
        self.move_time = 0
        self.move_delay = max(100, 500 - (level - 1) * 50)
        self.speed = ENEMY_SPEED + (level - 1) * ENEMY_SPEED_INCREASE
        self.create_fleet()
        self.bullets = []
        self.shoot_delay = 1000
        self.last_shot = pygame.time.get_ticks()
        self.animation_time = 0
        self.animation_delay = 500
        self.current_moving_row = 0
        self.row_move_delay = 100  # Delay between row movements in milliseconds

    def create_fleet(self):
        enemy_types = ["small", "medium", "large"]
        row_types = random.choices(
            enemy_types, k=ENEMY_ROWS
        )  # Randomly choose types for each row

        self.rows = []
        for row, enemy_type in enumerate(row_types):
            row_enemies = []
            for col in range(ENEMY_COLS):
                x = col * ENEMY_SPACING_X + (WIDTH - ENEMY_COLS * ENEMY_SPACING_X) // 2
                y = row * ENEMY_SPACING_Y + ENEMY_START_Y
                row_enemies.append(Enemy(x, y, enemy_type))
            self.rows.append(row_enemies)

    def update(self, barriers):
        current_time = pygame.time.get_ticks()
        self.move(barriers)

        if current_time - self.animation_time > self.animation_delay:
            self.animation_time = current_time
            self.animate_enemies()

        self.shoot()
        self.update_bullets(barriers)

        # Update dying enemies and remove them if fully destroyed
        for row in self.rows:
            for enemy in row[:]:
                if enemy.is_dying:
                    if enemy.update():
                        row.remove(enemy)

    def animate_enemies(self):
        for row in self.rows:
            for enemy in row:
                enemy.animate()

    def move(self, barriers):
        current_time = pygame.time.get_ticks()
        if current_time - self.move_time > self.move_delay:
            self.move_time = current_time
            if self.rows:  # Only move if there are rows
                self.move_row(self.current_moving_row, barriers)
                self.current_moving_row = (self.current_moving_row + 1) % len(self.rows)
            self.play_move_sound()

    def move_row(self, row_index, barriers):
        if not self.rows or row_index >= len(self.rows):  # Check if row_index is valid
            return

        if not self.rows[row_index]:  # Skip empty rows
            return

        move_down = False
        row_direction = self.direction
        row_speed = self.speed

        # Check if the row needs to change direction
        if (
            max(enemy.rect.right for enemy in self.rows[row_index]) >= WIDTH - 10
            and row_direction > 0
        ) or (
            min(enemy.rect.left for enemy in self.rows[row_index]) <= 10
            and row_direction < 0
        ):
            move_down = True
            self.direction *= -1
            row_direction = self.direction

        # Move the row horizontally
        for enemy in self.rows[row_index]:
            enemy.move(row_speed * row_direction, 0)

        if move_down:
            for row in self.rows:
                for enemy in row:
                    enemy.move(0, ENEMY_DROP)

        # Check collisions with barriers
        for enemy in self.rows[row_index]:
            for barrier in barriers:
                barrier.check_collision(enemy.rect)

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            if self.enemies:
                shooting_enemy = random.choice(self.enemies)
                self.bullets.append(
                    Bullet(shooting_enemy.rect.centerx, shooting_enemy.rect.bottom, 1)
                )
                self.last_shot = current_time

    def update_bullets(self, barriers):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.top > HEIGHT:
                self.bullets.remove(bullet)
            else:
                for barrier in barriers:
                    if barrier.check_collision(bullet.rect):
                        self.bullets.remove(bullet)
                        break

    def draw(self, screen):
        for row in self.rows:
            for enemy in row:
                enemy.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)

    def check_collision(self, bullet_rect):
        for row in self.rows:
            for enemy in row:
                if enemy.rect.colliderect(bullet_rect) and not enemy.is_dying:
                    enemy.hit()
                    return True
        return False

    def has_reached_bottom(self):
        return any(enemy.rect.bottom >= HEIGHT - 50 for enemy in self.enemies)

    def has_hit_player(self, player):
        return any(enemy.rect.colliderect(player.rect) for enemy in self.enemies)

    def play_move_sound(self):
        sound = random.choice(ENEMY_MOVE_SOUNDS)
        sound.play()

    def check_barrier_collisions(self, barriers):
        for enemy in self.enemies:
            for barrier in barriers:
                barrier.check_collision(enemy.rect)

    def remove_all_but_one(self):
        if self.enemies:
            last_enemy = self.enemies[-1]
            self.rows = [[last_enemy]]
            self.current_moving_row = 0  # Reset current_moving_row

    @property
    def enemies(self):
        return [enemy for row in self.rows for enemy in row]

    def clear_all_enemies(self):
        self.rows = []
        self.bullets = []
        self.current_moving_row = 0
