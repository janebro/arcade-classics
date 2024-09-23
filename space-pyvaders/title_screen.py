import pygame
from constants import *


class TitleScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, 36)
        self.big_font = pygame.font.Font(FONT_PATH, 72)
        self.small_font = pygame.font.Font(
            FONT_PATH, 24
        )  # Add this line for the smaller font
        self.menu_items = ["1 PLAYER GAME", "2 PLAYER GAME", "OPTIONS", "QUIT"]
        self.selected_item = 0
        self.sfx_volume = 5

    def draw_3d_text(self, text, x, y, color, shadow_color, offset=4):
        shadow_surf = self.big_font.render(text, True, shadow_color)
        text_surf = self.big_font.render(text, True, color)
        self.screen.blit(shadow_surf, (x + offset, y + offset))
        self.screen.blit(text_surf, (x, y))

    def draw(self):
        self.screen.fill(BLACK)

        # Draw 3D title
        self.draw_3d_text("SPACE", WIDTH // 2 - 150, 50, GREEN, (0, 100, 0))
        self.draw_3d_text("INVADERS", WIDTH // 2 - 200, 130, GREEN, (0, 100, 0))

        # Draw menu items
        for i, item in enumerate(self.menu_items):
            color = YELLOW if i == self.selected_item else WHITE
            text = self.font.render(item, True, color)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 300 + i * 60))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                elif event.key == pygame.K_DOWN:
                    self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                elif event.key == pygame.K_RETURN:
                    if self.menu_items[self.selected_item] == "1 PLAYER GAME":
                        return "START_GAME"
                    elif self.menu_items[self.selected_item] == "OPTIONS":
                        return "OPTIONS"
                    elif self.menu_items[self.selected_item] == "QUIT":
                        return "QUIT"
        return None

    def run_options(self):
        running = True
        while running:
            self.screen.fill(BLACK)
            title = self.font.render("OPTIONS", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

            # Add the "PRESS ESC TO RETURN" text
            return_text = self.small_font.render("PRESS ESC TO RETURN", True, WHITE)
            self.screen.blit(
                return_text, (WIDTH // 2 - return_text.get_width() // 2, 150)
            )

            volume_text = self.font.render(
                f"SFX Volume: {self.sfx_volume}", True, WHITE
            )
            self.screen.blit(
                volume_text, (WIDTH // 2 - volume_text.get_width() // 2, 300)
            )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_LEFT:
                        self.sfx_volume = max(1, self.sfx_volume - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.sfx_volume = min(10, self.sfx_volume + 1)

        return None

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            self.draw()
            action = self.handle_events()
            if action == "QUIT":
                return "QUIT"
            elif action == "START_GAME":
                return "START_GAME"
            elif action == "OPTIONS":
                options_result = self.run_options()
                if options_result == "QUIT":
                    return "QUIT"
            clock.tick(60)
