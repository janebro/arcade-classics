import pygame
from player import Player
from enemy import EnemyFleet
from bullet import Bullet
from constants import *
from barrier import Barrier
from title_screen import TitleScreen


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, 24)
        self.big_font = pygame.font.Font(FONT_PATH, 64)
        self.reset_game()
        self.flash_timer = 0
        self.flash_interval = 500  # Flash every 500ms
        self.flash_count = 0
        self.max_flashes = 5
        self.create_barriers()
        self.player_destroyed = False
        self.title_screen = TitleScreen(self.screen)
        self.death_animation_delay = 1000  # 1 second delay after death animation
        self.death_animation_end_time = 0  # Time when death animation ends
        self.game_state = "TITLE"  # Add this line

    def create_barriers(self):
        self.barriers = []
        barrier_y = HEIGHT - 150  # Adjust this value to position barriers higher
        barrier_width = BARRIER_SIZE[0]
        gap_between_barriers = 100  # Increased from 50 to 100 (or any desired value)
        total_width = (
            NUM_BARRIERS * barrier_width + (NUM_BARRIERS - 1) * gap_between_barriers
        )
        start_x = (WIDTH - total_width) // 2

        for i in range(NUM_BARRIERS):
            x = start_x + i * (barrier_width + gap_between_barriers)
            self.barriers.append(Barrier(x, barrier_y))

    def reset_game(self):
        self.player = Player()
        self.level = 1
        self.create_enemy_fleet()
        self.bullets = []
        self.score = 0
        self.game_over = False
        self.level_complete = False
        self.level_complete_time = 0
        self.flash_count = 0
        self.create_barriers()
        self.player_destroyed = False
        self.player.lives = INITIAL_LIVES

    def create_enemy_fleet(self):
        self.enemy_fleet = EnemyFleet(self.level)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = "TITLE"
                    return True
                if (
                    event.key == pygame.K_SPACE
                    and not self.game_over
                    and not self.level_complete
                    and self.player
                    and self.player.can_shoot()
                ):
                    self.bullets.append(
                        Bullet(self.player.rect.centerx, self.player.rect.top, -1)
                    )
                    self.player.shoot()
                    if SHOOT_SOUND:
                        SHOOT_SOUND.play()
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                    return True
                # Debug: Kill almost all enemies when 'W' is pressed
                if event.key == pygame.K_F10:
                    self.debug_kill_enemies()
        return True

    def debug_kill_enemies(self):
        if len(self.enemy_fleet.enemies) > 1:
            self.enemy_fleet.remove_all_but_one()
            self.score += 10 * (
                ENEMY_ROWS * ENEMY_COLS - 1
            )  # Add score for killed enemies

    def update(self):
        if self.game_state == "TITLE":
            return

        if self.level_complete:
            self.clear_bullets()
            return

        if self.player.is_dying:
            if self.player.update(self.barriers):
                self.death_animation_end_time = (
                    pygame.time.get_ticks()
                )  # Record the end time
                self.player.death_animation_complete = True  # Set the flag
            return

        if self.player.death_animation_complete:
            current_time = pygame.time.get_ticks()
            if (
                current_time - self.death_animation_end_time
                > self.death_animation_delay
            ):
                self.handle_player_death()
            return

        self.player.update(self.barriers)
        self.enemy_fleet.update(self.barriers)
        self.update_bullets()
        self.check_collisions()

        # Check for game over conditions first
        if self.enemy_fleet.has_reached_bottom() or self.enemy_fleet.has_hit_player(
            self.player
        ):
            self.trigger_game_over()
            return  # Exit the update method early if game over

        # Only check for level completion if the game is not over
        if len(self.enemy_fleet.enemies) == 0 and not self.game_over:
            self.level_complete = True
            self.level_complete_time = pygame.time.get_ticks()
            if LEVEL_COMPLETE_SOUND:
                LEVEL_COMPLETE_SOUND.play()
            self.clear_bullets()  # Clear bullets when level is complete

    def clear_bullets(self):
        self.bullets.clear()
        self.enemy_fleet.bullets.clear()

    def update_bullets(self):
        # Player bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
            else:
                for barrier in self.barriers[:]:
                    if barrier.check_collision(bullet.rect):
                        self.bullets.remove(bullet)
                        if barrier.is_destroyed():
                            self.barriers.remove(barrier)
                        break
                else:
                    if self.enemy_fleet.check_collision(bullet.rect):
                        self.bullets.remove(bullet)
                        self.score += 10
                        if ENEMY_KILLED_SOUND:
                            ENEMY_KILLED_SOUND.play()

        # Enemy bullets
        for bullet in self.enemy_fleet.bullets[:]:
            bullet.update()
            if bullet.rect.top > HEIGHT:
                self.enemy_fleet.bullets.remove(bullet)
            else:
                for barrier in self.barriers[:]:
                    if barrier.check_collision(bullet.rect):
                        self.enemy_fleet.bullets.remove(bullet)
                        if barrier.is_destroyed():
                            self.barriers.remove(barrier)
                        break
                else:
                    if self.player.rect.colliderect(bullet.rect):
                        self.enemy_fleet.bullets.remove(bullet)
                        self.trigger_game_over()

    def check_collisions(self):
        # Player bullets hitting enemies
        for bullet in self.bullets[:]:
            if self.enemy_fleet.check_collision(bullet.rect):
                self.bullets.remove(bullet)
                self.score += 10
                if ENEMY_KILLED_SOUND:
                    ENEMY_KILLED_SOUND.play()

        # Enemy bullets hitting player
        for bullet in self.enemy_fleet.bullets[:]:
            if self.player.rect.colliderect(bullet.rect):
                self.enemy_fleet.bullets.remove(bullet)
                self.trigger_game_over()

        # Check for enemies hitting barriers
        self.enemy_fleet.check_barrier_collisions(self.barriers)

    def trigger_game_over(self):
        if not self.game_over and not self.player.is_dying:
            self.player.hit()

    def handle_player_death(self):
        if self.player.lose_life():
            # Player still has lives left
            self.player.reset()
            self.enemy_fleet.clear_all_enemies()
            self.bullets.clear()
            self.enemy_fleet.bullets.clear()
            self.create_enemy_fleet()
            self.player.death_animation_complete = False  # Reset the flag
        else:
            # No lives left, game over
            self.game_over = True
            self.player.death_animation_complete = False  # Reset the flag
            self.enemy_fleet.clear_all_enemies()
            self.bullets.clear()
            self.enemy_fleet.bullets.clear()

    def clear_screen(self):
        self.enemy_fleet.enemies.clear()
        self.bullets.clear()
        self.enemy_fleet.bullets.clear()

    def draw(self):
        self.screen.fill(BLACK)

        self.enemy_fleet.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for bullet in self.enemy_fleet.bullets:
            bullet.draw(self.screen)
        for barrier in self.barriers:
            barrier.draw(self.screen)

        if self.player:
            self.player.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw lives just below the score
        lives_text = self.font.render(f"LIVES: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 40))  # 40 pixels below the score

        # Draw level
        level_text = self.font.render(f"LEVEL: {self.level}", True, WHITE)
        self.screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        if self.game_over:
            self.draw_game_over_text()

        if self.level_complete:
            level_complete_text = self.big_font.render("LEVEL COMPLETE", True, GREEN)
            self.screen.blit(
                level_complete_text,
                (WIDTH // 2 - level_complete_text.get_width() // 2, HEIGHT // 2 - 50),
            )

        pygame.display.flip()

    def draw_game_over_text(self):
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        restart_text = self.font.render("PRESS R TO RESTART", True, WHITE)
        self.screen.blit(
            game_over_text,
            (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50),
        )
        self.screen.blit(
            restart_text,
            (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50),
        )

    def update_sfx_volume(self):
        set_sfx_volume(self.title_screen.sfx_volume)

    def run_frame(self):
        if self.game_state == "TITLE":
            action = self.title_screen.run_frame()
            if action == "QUIT":
                return False  # This will signal the main loop to exit
            elif action == "START_GAME":
                self.update_sfx_volume()
                self.reset_game()
                self.game_state = "PLAYING"
            elif action == "OPTIONS":
                self.game_state = "OPTIONS"
        elif self.game_state == "OPTIONS":
            action = self.title_screen.run_options_frame()
            if action == "RETURN":
                self.game_state = "TITLE"
            elif action == "QUIT":
                return False  # This will signal the main loop to exit
        elif self.game_state == "PLAYING":
            if not self.handle_events():
                return False
            self.update()
            self.draw()

            if not self.game_over and self.level_complete:
                current_time = pygame.time.get_ticks()
                if current_time - self.level_complete_time > LEVEL_COMPLETE_DELAY:
                    self.level += 1
                    self.create_enemy_fleet()
                    self.player.reset_position()
                    self.level_complete = False
                    self.clear_bullets()

        self.clock.tick(FPS)
        return True


if __name__ == "__main__":
    game = Game()
    game.run()
