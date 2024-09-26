import asyncio
import pygame
from game import Game


async def main():
    pygame.init()
    game = Game()
    running = True
    while running:
        running = game.run_frame()
        await asyncio.sleep(0)
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
