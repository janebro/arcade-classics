import pygame
import os

# Add this near the top of the file, after the import statements
FONT_PATH = os.path.join("fonts", "retro-gaming.ttf")

# Screen dimensions
WIDTH = 1024
HEIGHT = 768

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game settings
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 8
ENEMY_SPEED = 12
ENEMY_DROP = 40
ENEMY_ROWS = 5
ENEMY_COLS = 11
ENEMY_SPACING_X = 60  # Increased from 60
ENEMY_SPACING_Y = 60  # Increased from 60
ENEMY_START_Y = 110  # Decreased from 120

# Player settings
PLAYER_SHOOT_COOLDOWN = 500  # Time in milliseconds between shots

# Sound effects
pygame.mixer.init()


def load_sound(filename):
    try:
        return pygame.mixer.Sound(os.path.join("sounds", filename))
    except pygame.error:
        print(f"Warning: Unable to load sound file: {filename}")
        return None


SHOOT_SOUND = load_sound("shoot.wav")
if SHOOT_SOUND:
    SHOOT_SOUND.set_volume(0.3)

EXPLOSION_SOUND = load_sound("explosion.wav")
ENEMY_KILLED_SOUND = load_sound("invaderkilled.wav")
ENEMY_MOVE_SOUNDS = [load_sound(f"fastinvader{i}.wav") for i in range(1, 5)]
ENEMY_MOVE_SOUNDS = [sound for sound in ENEMY_MOVE_SOUNDS if sound is not None]

# Add this to the sound effects section
LEVEL_COMPLETE_SOUND = load_sound("level_complete.mp3")

# Level settings
LEVEL_COMPLETE_DELAY = 3000
ENEMY_SPEED_INCREASE = 1.5

# Barrier settings
BARRIER_COLOR = (0, 255, 0)  # Green
NUM_BARRIERS = 4
BARRIER_SIZE = (88, 64)  # Adjusted size based on the new BARRIER_DESIGN

# Bullet settings
BULLET_SIZE = (6, 15)  # Thinner, longer bullets
PLAYER_BULLET_SPEED = 7  # Increased player bullet speed
ENEMY_BULLET_SPEED = 2  # Slightly reduced enemy bullet speed


# Add this function at the end of the file
def set_sfx_volume(volume):
    volume_scale = volume / 10.0
    if SHOOT_SOUND:
        SHOOT_SOUND.set_volume(0.3 * volume_scale)
    if EXPLOSION_SOUND:
        EXPLOSION_SOUND.set_volume(volume_scale)
    if ENEMY_KILLED_SOUND:
        ENEMY_KILLED_SOUND.set_volume(volume_scale)
    for sound in ENEMY_MOVE_SOUNDS:
        if sound:
            sound.set_volume(volume_scale)
    if LEVEL_COMPLETE_SOUND:
        LEVEL_COMPLETE_SOUND.set_volume(volume_scale)
