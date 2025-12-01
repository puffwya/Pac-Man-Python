import pygame
import sys
import random
import math
from levels import ALL_LEVELS, LEVEL_1, LEVEL_2

# Initialize Pygame
pygame.init()

# Initialize and create a font object
pygame.font.init()
score_font = pygame.font.Font("Grand9K Pixel.ttf", 30)
ready_font = pygame.font.Font("Grand9K Pixel.ttf", 20)
g_eat_font = pygame.font.Font("Grand9K Pixel.ttf", 15)

# Initialize mixer
pygame.mixer.init()

# Screen setup
TILE_SIZE = 30
ROWS = 31
COLS = 28

# Determine screen height and width based on amount of rows, cols and tile size
screen_width = COLS * TILE_SIZE
screen_height = ROWS * TILE_SIZE

screen = pygame.display.set_mode((screen_width, screen_height))

# Lives and Score
player_score = 0 
eaten_pellets = 0
player_lives = 5

# Game start variables
game_start = True
game_start_timer = 0
GAME_START_DURATION = 240  # frames, e.g., 2 seconds at 60 FPS
chosen_lvl = None
pygame.mixer.music.load("sounds/Pac-Man starting sound effect.mp3")
play_once = True
init_spawn = True
g_siren_start = True

# Colors
BLACK = (0, 0, 0)
WALL_BLUE = (25, 25, 166)
POWER_PELLET_GHOST_BLUE = (33, 33, 222)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (255, 184, 255)
PEACH = (222, 161, 133)
CYAN = (0, 255, 255)

# Sound variables
waka_sound = pygame.mixer.Sound("sounds/PacmanWaka.mp3")
eating_ghost = pygame.mixer.Sound("sounds/PacmanEatingGhost.mp3")

# Power Pellet "Blinking" Variables
power_pellet_flipper = True
POWER_PELLET_BLINK_INTERVAL = 200 # milliseconds
last_pellet_blink = pygame.time.get_ticks()

# Player setup so that Pac-Man fits nicely in the path
# TILE_SIZE // 2 - 1 makes the player slightly smaller than the tile but still nicely fit 
player_radius = TILE_SIZE // 2 - 1
current_direction = None
next_direction = None
player_speed = 2

# Pac-Man Mouth state
PACMAN_FRAMES = [0, 20, 50]  # mouth fully closed, partially open, fully open
pacman_frame_index = 0
pacman_frame_tick = 0
PACMAN_FRAME_DELAY = 2  # change frame every 2 game ticks
start = 0
end = 0
startL = 0
endL = 0

# Ghost directional variables
red_direction = "left"          # current movement direction
red_last_dir = "left"           # needed to prevent reversing
    
pink_direction = "down"
pink_last_dir = "down"
        
blue_direction = "up"
blue_last_dir = "up"
        
orange_direction = "up"
orange_last_dir = "up"

# Pacman and Ghost collision
COLLISION_DISTANCE = player_radius

# MIN PELLETS EATEN FOR LEVEL COMPLETION
# LVL1 min score = 2490
lvl1MinEaten = 233
# LVL2 min score = 2370
lvl2MinEaten = 221

# Ghost eaten score (200 at the start of a frightened state and increase by x2 for each ghost eaten)
ghost_eat_score = 200

# Ghost eyes state
rg_eyes = False
bg_eyes = False
pg_eyes = False
og_eyes = False

# Ghost eaten vars
ghost_eaten = False
ghost_eaten_color = None
ghost_eaten_timer = 0
ghost_eaten_duration = 0.6   # seconds

