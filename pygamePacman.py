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
player_lives = 5

# Game start variables
game_start = True
game_start_timer = 0
GAME_START_DURATION = 240  # frames, e.g., 2 seconds at 60 FPS
chosen_lvl = None
pygame.mixer.music.load("sounds/Pac-Man starting sound effect.mp3")
play_once = True
init_spawn = True

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

# MIN SCORES FOR LEVEL COMPLETION
lvl1MinScore = 2490
lvl2MinScore = 2370

# --- Functions ---

# Level generation function, randomly picks from one of the layouts
def generate_level():
    """
    Return one of the prebuilt levels at random.
    1 = wall, 0 = path
    """
    global chosen_lvl
    if random.choice(ALL_LEVELS) == LEVEL_1:
        chosen_lvl = 1
        return LEVEL_1
    else:
        chosen_lvl = 2
        return LEVEL_2

# Create the level
level = generate_level()

if chosen_lvl == 1:
    player_x = TILE_SIZE * 13.5
    player_y = TILE_SIZE * 20.5
elif chosen_lvl == 2:
    player_x = TILE_SIZE * 13.5
    player_y = TILE_SIZE * 19.5

# Helper function to return the grid tile position based on x and y pixel locations given to funciton
def get_grid_pos(x, y):
    return int(y // TILE_SIZE), int(x // TILE_SIZE)

# Helper function to return the pixel position based on row and col positions given to function
def get_pixel_pos(row, col):
    x = col * TILE_SIZE + TILE_SIZE // 2
    y = row * TILE_SIZE + TILE_SIZE // 2
    return x, y

# Helper function to stretch text (higher scale = more stretch)
def render_stretched_text(text, color, font, scale_x=2.0, scale_y=1.0):
    # Render normal text
    text_surface = font.render(text, True, color)

    # Original size
    w, h = text_surface.get_size()

    # Compute stretched size
    new_w = int(w * scale_x)
    new_h = int(h * scale_y)

    # Stretch using smoothscale (best quality)
    stretched_surface = pygame.transform.smoothscale(text_surface, (new_w, new_h))

    return stretched_surface

# Helper function to snap Pac-Mans x and y coords into necessary location for move_pacman()
def snap_to_tile_center(x, y):
    grid_row, grid_col = get_grid_pos(x, y)
    center_x = grid_col * TILE_SIZE + TILE_SIZE // 2
    center_y = grid_row * TILE_SIZE + TILE_SIZE // 2
    return center_x, center_y

# Checks if the given tile is walkable (not equal to 1 or 3)
def is_walkable(row, col):
    if 0 <= row < len(level) and 0 <= col < len(level[0]):
        if level[row][col] == 3:
            return False
        else: 
            return level[row][col] != 1
    return False

# Queues a turn and excecutes it once Pac-Man is properly aligned within a tile
def try_turn():
    # Acess global movement and player state variables
    global current_direction, next_direction, player_x, player_y

    # If there is no queued direction (the player is not trying to turn, do nothing)
    if not next_direction:
        return

    # Convert Pac-Man's curent pixel position into grid (row, column) coords
    grid_row, grid_col = get_grid_pos(player_x, player_y)

    # Calculate how far Pac-Man’s current position is offset within his current tile
    # These offsets help us know when Pac-Man is centered enough to allow a clean turn
    offset_x = player_x % TILE_SIZE
    offset_y = player_y % TILE_SIZE


    if next_direction == 'left' and offset_y == TILE_SIZE / 2:
        if is_walkable(grid_row, grid_col - 1):
            current_direction = 'left'
            # Snap Pac-Man to the exact vertical center of the current tile for perfect alignment
            player_y = grid_row * TILE_SIZE + TILE_SIZE / 2
    elif next_direction == 'right' and offset_y == TILE_SIZE / 2:
        if is_walkable(grid_row, grid_col + 1):
            current_direction = 'right'
            # Snap vertically to tile center
            player_y = grid_row * TILE_SIZE + TILE_SIZE / 2
    elif next_direction == 'up' and offset_x == TILE_SIZE / 2:
        if is_walkable(grid_row - 1, grid_col):
            current_direction = 'up'
            # Snap horizontally to tile center
            player_x = grid_col * TILE_SIZE + TILE_SIZE / 2
    elif next_direction == 'down' and offset_x == TILE_SIZE / 2:
        if is_walkable(grid_row + 1, grid_col):
            current_direction = 'down'
            # Snap horizontally to tile center
            player_x = grid_col * TILE_SIZE + TILE_SIZE / 2

# Check if Pac-Man's edge (radius) will hit a wall next frame
def will_hit_wall(x, y, direction):
    row, col = get_grid_pos(x, y)

    if direction == 'left':
        check_x = x - player_radius - player_speed
        check_col = int(check_x // TILE_SIZE)
        return level[row][check_col] == 1
    elif direction == 'right':
        check_x = x + player_radius + player_speed
        check_col = int(check_x // TILE_SIZE)
        try:
            return level[row][check_col] == 1
        except IndexError:
            return False
    elif direction == 'up':
        check_y = y - player_radius - player_speed
        check_row = int(check_y // TILE_SIZE)
        return level[check_row][col] == 1
    elif direction == 'down':
        check_y = y + player_radius + player_speed
        check_row = int(check_y // TILE_SIZE)
        return level[check_row][col] == 1
    return False

# Moves Pac-Man until he hits a wall, then stops him and snaps his position to tile center
def move_pacman():
    global player_x, player_y, current_direction

    if current_direction == 'left':
        if will_hit_wall(player_x, player_y, 'left'):
            player_x, player_y = snap_to_tile_center(player_x, player_y)
            current_direction = None
        else:
            player_x -= player_speed

    elif current_direction == 'right':
        if will_hit_wall(player_x, player_y, 'right'):
            player_x, player_y = snap_to_tile_center(player_x, player_y)
            current_direction = None
        else:
            player_x += player_speed

    elif current_direction == 'up':
        if will_hit_wall(player_x, player_y, 'up'):
            player_x, player_y = snap_to_tile_center(player_x, player_y)
            current_direction = None
        else:
            player_y -= player_speed

    elif current_direction == 'down':
        if will_hit_wall(player_x, player_y, 'down'):
            player_x, player_y = snap_to_tile_center(player_x, player_y)
            current_direction = None
        else:
            player_y += player_speed

# Handles warp functionality, if player leaves left side of screen get sent to right side - 1 tile, if leaves right 
# side get sent to left side + 1 tile
def handle_warp():
    global player_x
    if player_x < 0:
        player_x = (len(level[0]) - 1) * TILE_SIZE + TILE_SIZE / 2
    elif player_x > len(level[0]) * TILE_SIZE:
        player_x = TILE_SIZE / 2

def draw_pacman_frame(surface, mouth_angle, direction):
    global player_radius, player_x, player_y, start, end
    
    offset_x = -player_radius-1  # shift left by radius for centering
    offset_y = -player_radius-1  # shift up by radius for centering
        
    center_x = player_x + TILE_SIZE // 2 + offset_x
    center_y = player_y + TILE_SIZE // 2 + offset_y
    center = (center_x, center_y)

    a = math.radians(mouth_angle)

    # Direction determines mouth orientation
    if direction == "right":
        start = -a
        end = a
    elif direction == "left":
        start = math.pi - a
        end = math.pi + a 
    elif direction == "up":
        start = 1.5 * math.pi - a
        end = 1.5 * math.pi + a
    elif direction == "down":
        start = 0.5 * math.pi - a
        end = 0.5 * math.pi + a

    # Draw full circle
    pygame.draw.circle(surface, YELLOW, center, player_radius)

    # Mouth cutout: approximate wedge with multiple points along the arc
    if mouth_angle > 0:
        num_points = 10
        points = [center]
        for i in range(num_points + 1):
            angle = start + (end - start) * (i / num_points)
            x = center[0] + player_radius * math.cos(angle)
            y = center[1] + player_radius * math.sin(angle)
            points.append((x, y))

        pygame.draw.polygon(surface, BLACK, points)


clock = pygame.time.Clock()

# Checks if the current tile pacman is on is a pellet or not, sets tile to 2, adds to score, and removes 
# pellet if so. Does nothing if not.
def is_current_tile_pellet():
    global player_x, player_y, player_score, waka_flip
    grid_row, grid_col = get_grid_pos(player_x, player_y)

    # Checks if base pellet
    if level[grid_row][grid_col] == 0:
        player_score += 10
        level[grid_row][grid_col] = 2
        waka_sound.play()
        return True
    # Checks if power pellet
    elif level[grid_row][grid_col] == 4:
        player_score += 50
        level[grid_row][grid_col] = 2
        waka_sound.play()
        return True
    return False

# Game loop
running = True
while running:

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Black background
    screen.fill(BLACK)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw level and pellets
    # Get each row in level
    for row in range(len(level)):
	# Get each col in each row
        for col in range(len(level[row])):
	    # Converts the grid coordinates (row, col) into pixel coordinates on the screen (x, y)
	    # Each cell in the grid is a square of size TILE_SIZE so multiplying by TILE_SIZE places each 
	    # cell in the correct spot i.e. 1 = 40, 2 = 80...
            x = col * TILE_SIZE
            y = row * TILE_SIZE

            if level[row][col] == 0:
                # Draw pellet in center of open cell
                pellet_radius = TILE_SIZE // 2 - 12
                pygame.draw.circle(screen, PEACH, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), pellet_radius)
            elif level[row][col] == 1:

                # --- Check corners ---

                # Top-left rounded corner
                if is_walkable(row-1, col) and is_walkable(row, col-1):
                    pygame.draw.rect(screen, WALL_BLUE,(x,y,TILE_SIZE,TILE_SIZE),border_top_left_radius=10,
            border_top_right_radius=0,
            border_bottom_left_radius=0,
            border_bottom_right_radius=0)
                # Top-right rounded corner
                elif is_walkable(row-1, col) and is_walkable(row, col+1):
                    pygame.draw.rect(screen, WALL_BLUE,(x,y,TILE_SIZE,TILE_SIZE),border_top_right_radius=10,
            border_top_left_radius=0,
            border_bottom_left_radius=0,
            border_bottom_right_radius=0)
                # Bottom-left
                elif is_walkable(row+1, col) and is_walkable(row, col-1):
                    pygame.draw.rect(screen, WALL_BLUE,(x,y,TILE_SIZE,TILE_SIZE),border_bottom_left_radius=10,
            border_top_left_radius=0,
            border_top_right_radius=0,
            border_bottom_right_radius=0)
                # Bottom-right
                elif is_walkable(row+1, col) and is_walkable(row, col+1):
                    pygame.draw.rect(screen, WALL_BLUE,(x,y,TILE_SIZE,TILE_SIZE),border_bottom_right_radius=10,
            border_top_left_radius=0,
            border_top_right_radius=0,
            border_bottom_left_radius=0)
                else:
                    # Draw wall with no rounded edges
                    pygame.draw.rect(screen, WALL_BLUE, (x, y, TILE_SIZE, TILE_SIZE))
            elif level[row][col] == 3:
                # Draw Ghost Door
                pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE//4))
            elif level[row][col] == 4:
                # Draw pellet in center of open cell
                power_pellet_radius = TILE_SIZE // 2 - 5
                if power_pellet_flipper:
                    color = PEACH
                else:
                    color = BLACK

                pygame.draw.circle(screen, color,(x + TILE_SIZE // 2, y + TILE_SIZE // 2),power_pellet_radius)

    # Draw Pac-Man lives near bottom of screen
        for life in range(player_lives):
                
            # The circle center you actually draw:
            circle_center = (30 + TILE_SIZE * life, screen_height - 50)
                
            # Draw Pac-Man body
            pygame.draw.circle(screen, YELLOW, circle_center, player_radius)
                
            # Mouth angles (always facing right for lives)
            a = math.radians(40)
            startL = math.pi - a
            endL = math.pi + a
                
            # Build mouth wedge polygon
            num_points = 12
            points = [circle_center]  # start at center of the circle
    
            for i in range(num_points + 1):
                angle = startL + (endL - startL) * (i / num_points)
                x = circle_center[0] + player_radius * math.cos(angle)
                y = circle_center[1] + player_radius * math.sin(angle)
                points.append((x, y))
        
            # Draw the wedge
            pygame.draw.polygon(screen, BLACK, points)

    if game_start:
        if play_once:
            pygame.mixer.music.play()
            play_once = False
        if chosen_lvl == 1:
            game_start_timer += 1
            row, col = get_pixel_pos(13,10)

            if game_start_timer <= 120:
                # "Player One" text
                PLAYER_ONE = render_stretched_text("PLAYER  ONE", CYAN, ready_font, scale_x=1.6)
                player_one_rect = PLAYER_ONE.get_rect(center=(col + TILE_SIZE // 2, row))
                screen.blit(PLAYER_ONE, player_one_rect)
    
                # "READY!" text below
                READY = render_stretched_text("READY!", YELLOW, ready_font, scale_x=1.5)
                offset = TILE_SIZE * 5
                ready_rect = READY.get_rect(center=(col + TILE_SIZE // 2, row + offset))
                screen.blit(READY, ready_rect)  
            elif game_start_timer >= 120:
                # "READY!" text below
                READY = render_stretched_text("READY!", YELLOW, ready_font, scale_x=1.5)
                offset = TILE_SIZE * 5
                ready_rect = READY.get_rect(center=(col + TILE_SIZE // 2, row + offset))
                screen.blit(READY, ready_rect)
                if init_spawn == True:
                    player_lives -= 1
                    init_spawn = False
                # Draw Pac-Man
                draw_pacman_frame(screen, PACMAN_FRAMES[pacman_frame_index], current_direction)
            # After the duration, exit start state
            if game_start_timer >= GAME_START_DURATION:
                game_start = False
        elif chosen_lvl == 2:
            game_start_timer += 1
            row, col = get_pixel_pos(13,10)
            
            if game_start_timer <= 120:
                # "Player One" text   
                PLAYER_ONE = render_stretched_text("PLAYER  ONE", CYAN, ready_font, scale_x=1.6)
                player_one_rect = PLAYER_ONE.get_rect(center=(col + TILE_SIZE // 2, row))
                screen.blit(PLAYER_ONE, player_one_rect)
        
                # "READY!" text below  
                READY = render_stretched_text("READY!", YELLOW, ready_font, scale_x=1.5)
                offset = TILE_SIZE * 6
                ready_rect = READY.get_rect(center=(col + TILE_SIZE // 2, row + offset))
                screen.blit(READY, ready_rect)
            elif game_start_timer >= 120:
                # "READY!" text below
                READY = render_stretched_text("READY!", YELLOW, ready_font, scale_x=1.5)
                offset = TILE_SIZE * 6
                ready_rect = READY.get_rect(center=(col + TILE_SIZE // 2, row + offset))
                screen.blit(READY, ready_rect)
                if init_spawn == True:  
                    player_lives -= 1
                    init_spawn = False
                # Draw Pac-Man   
                draw_pacman_frame(screen, PACMAN_FRAMES[pacman_frame_index], current_direction)
            # After the duration, exit start state
            if game_start_timer >= GAME_START_DURATION:
                game_start = False
    else:

        current_time = pygame.time.get_ticks()

        # Keeps track of time passed and flips power_pellet_flipper to create a "blinking" effect for power pellets
        # Occurs once every 200 milliseconds
        if current_time - last_pellet_blink > POWER_PELLET_BLINK_INTERVAL:
            power_pellet_flipper = not power_pellet_flipper
            last_pellet_blink = current_time

        # Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            next_direction = 'left'
        elif keys[pygame.K_RIGHT]:
            next_direction = 'right'
        elif keys[pygame.K_UP]:
            next_direction = 'up'
        elif keys[pygame.K_DOWN]:
            next_direction = 'down'

        # Check for pellet (base or power)
        is_current_tile_pellet()

        # Movement logic    
        try_turn()
        move_pacman()
        handle_warp()

        # Animate Pac-Man (player)
        if current_direction is not None:
            pacman_frame_tick += 1
            if pacman_frame_tick >= PACMAN_FRAME_DELAY:
                pacman_frame_tick = 0
                pacman_frame_index = (pacman_frame_index + 1) % len(PACMAN_FRAMES)

        # Draw Pac-Man
        draw_pacman_frame(screen, PACMAN_FRAMES[pacman_frame_index], current_direction)

        # Draw Score
        score = score_font.render("Score: " + str(player_score), True, WHITE)

        # Draw Pac-Man lives near bottom of screen
        for life in range(player_lives):
            
            # The circle center you actually draw:
            circle_center = (30 + TILE_SIZE * life, screen_height - 50)  
                    
            # Draw Pac-Man body
            pygame.draw.circle(screen, YELLOW, circle_center, player_radius)
            
            # Mouth angles (always facing right for lives)
            a = math.radians(40)
            startL = math.pi - a
            endL = math.pi + a
            
            # Build mouth wedge polygon 
            num_points = 12
            points = [circle_center]  # start at center of the circle
                    
            for i in range(num_points + 1):
                angle = startL + (endL - startL) * (i / num_points)
                x = circle_center[0] + player_radius * math.cos(angle)
                y = circle_center[1] + player_radius * math.sin(angle)
                points.append((x, y))
                
            # Draw the wedge
            pygame.draw.polygon(screen, BLACK, points)

        screen.blit(score, (20,screen_height-120))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
