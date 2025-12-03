from settings import *

# Global Frightened State
frightened_mode = False  
frightened_timer = 0.0
FRIGHTENED_DURATION = 7.0  # seconds
FRIGHTENED_FLASH_INTERVAL = 200  # seconds before frightened ends
#FLASH_INTERVAL = 0.3  # seconds per color switch
flashing_frightened_flipper = True
last_ghost_flash = pygame.time.get_ticks()

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
        return copy.deepcopy(LEVEL_1)
    else:
        chosen_lvl = 2
        return copy.deepcopy(LEVEL_2)

def count_pellets(level_grid):
    count = 0
    for row in level_grid:
        for tile in row:
            if tile == 0:   # pellet tile
                count += 1
    return count

# Create the level
level = generate_level()

if chosen_lvl == 1:
    player_x = TILE_SIZE * 13.5
    player_y = TILE_SIZE * 20.5
    # print(count_pellets(level))
elif chosen_lvl == 2:
    player_x = TILE_SIZE * 13.5
    player_y = TILE_SIZE * 19.5
    # print(count_pellets(level))

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

# Checks if the current tile pacman is on is a pellet or not, sets tile to 2, adds to score, and removes 
# pellet if so. Does nothing if not.
def is_current_tile_pellet():
    global player_x, player_y, player_radius, player_score, waka_flip, eaten_pellets, red_direction, pink_direction, blue_direction, orange_direction, frightened_mode, frightened_timer, p_one_up, pickup_x, pickup_y, pickup_frame, pickup_for_level, item_score_timer, pickup_score, p_one_up
    grid_row, grid_col = get_grid_pos(player_x, player_y)

    item_row, item_col = get_grid_pos(pickup_x, pickup_y)

    # Checks for item pickup
    if grid_row == item_row and grid_col == item_col:
        if pickup_frame == 0 and not pickup_for_level:
            item_pickup.play()
            player_score += 100
            pickup_score = 100
            p_one_up += 100
            pickup_frame += 1
            pickup_for_level = True
            item_score_timer = 0
        elif pickup_frame == 1 and not pickup_for_level:
            item_pickup.play()
            player_score += 300
            pickup_score = 300
            p_one_up += 300
            pickup_frame += 1
            pickup_for_level = True
            item_score_timer = 0
        elif pickup_frame == 2 and not pickup_for_level:
            item_pickup.play()
            player_score += 500
            pickup_score = 500
            p_one_up += 500
            pickup_frame += 1
            pickup_for_level = True
            item_score_timer = 0
        elif pickup_frame == 3 and not pickup_for_level:
            item_pickup.play()
            player_score += 700
            pickup_score = 700
            p_one_up += 700
            pickup_frame += 1
            pickup_for_level = True
            item_score_timer = 0
        elif pickup_frame == 4 and not pickup_for_level:
            item_pickup.play()
            player_score += 1000
            pickup_score = 1000
            p_one_up += 1000
            pickup_frame += 1
            pickup_for_level = True
            item_score_timer = 0
        elif pickup_frame == 5 and not pickup_for_level:
            item_pickup.play()
            player_score += 2000
            pickup_score = 2000
            p_one_up += 2000
            pickup_frame += 1
            pickup_for_level = True
            item_score_timer = 0
        elif pickup_frame == 6 and not pickup_for_level:
            item_pickup.play()
            player_score += 3000
            pickup_score = 3000
            p_one_up += 3000
            pickup_frame += 1
            pickup_for_level = True
            item_score_timer = 0
        elif pickup_frame == 7 and not pickup_for_level:
            item_pickup.play()
            player_score += 5000
            pickup_score = 5000
            p_one_up += 5000
            pickup_frame += 1
            pickup_for_level = True
            item_score_timer = 0

    # Checks if base pellet
    if level[grid_row][grid_col] == 0:
        player_score += 10
        p_one_up += 10
        eaten_pellets += 1
        level[grid_row][grid_col] = 2
        waka_sound.play()
        return True
    # Checks if power pellet
    elif level[grid_row][grid_col] == 4:
        player_score += 50
        p_one_up += 50
        eaten_pellets += 1
        level[grid_row][grid_col] = 2
        waka_sound.play()

        # Activate frightened mode
        frightened_mode = True
        frightened_timer = 0.0

        # Reverse ghost directions immediately
        red_direction = {"up":"down","down":"up","left":"right","right":"left"}[red_direction]
        pink_direction = {"up":"down","down":"up","left":"right","right":"left"}[pink_direction]
        blue_direction = {"up":"down","down":"up","left":"right","right":"left"}[blue_direction]
        orange_direction = {"up":"down","down":"up","left":"right","right":"left"}[orange_direction]

        return True

    return False

# --- Fruits/Pickups Setup ---
scale_factor = TILE_SIZE // 12 - 0.1
pickup_frames = []

for i in range(8):
    img = pygame.image.load(f"sprites/pacman-pickup-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    pickup_frames.append(img)

# --- Scaled Pickups for display on right side of screen ---
scaled_pickups = []
scale_factor = TILE_SIZE // 12 - 0.7

for img in pickup_frames:
    w, h = img.get_size()
    scaled = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    scaled_pickups.append(scaled)

# --- Start screen pacman right sprites setup ---
scale_factor = TILE_SIZE // 12 - 0.1
pacman_start_screen_right_frames = []

for i in range(3):
    img = pygame.image.load(f"sprites/pacman-start-screen-right-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    pacman_start_screen_right_frames.append(img)

# --- Intermission sprites setup ---
scale_factor = TILE_SIZE // 12 - 0.1
pacman_intermission_frames = []
            
for i in range(3):
    img = pygame.image.load(f"sprites/pacman-intermission-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    pacman_intermission_frames.append(img)

scale_factor = TILE_SIZE // 12 - 0.1
pacman_intermission_frames_big = []
            
for i in range(3):
    img = pygame.image.load(f"sprites/pacman-intermission-big-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    pacman_intermission_frames_big.append(img)

# --- Pacman Death Frames Setup ---
scale_factor = TILE_SIZE // 12 - 0.1
pacman_death_frames = []  
    
for i in range(11): 
    img = pygame.image.load(f"sprites/pacman-death-frame-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    pacman_death_frames.append(img)

# --- Ghost Setup ---

num_frames = 2  # number of frames in the ghost animation
scale_factor = TILE_SIZE // 12 - 0.1

# --- Ghost State Variables ---

# Red ghost starting position
red_ghost_x = TILE_SIZE * 13 + TILE_SIZE/2
red_ghost_y = TILE_SIZE * 10 + TILE_SIZE/2

# Pink ghost starting position
pink_ghost_x = TILE_SIZE * 13 + TILE_SIZE/2
pink_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2

# Blue ghost starting position   
blue_ghost_x = TILE_SIZE * 12 + TILE_SIZE/2
blue_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2

# Orange ghost starting positions
orange_ghost_x = TILE_SIZE * 14 + TILE_SIZE/2
orange_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2

# Ghost movement speed vars
r_ghost_speed = 1.0
b_ghost_speed = 1.0
p_ghost_speed = 1.0
o_ghost_speed = 1.0

# mode management
ghost_mode = "scatter"            # can be "scatter", or "chase"
ghost_mode_timer = 0
ghost_mode_index = 0
MODE_CYCLE = [
    ("scatter", 7),
    ("chase", 20)
]

# Load ghost frames into a list

# Red ghost sprites
red_ghost_up = []
red_ghost_down = []
red_ghost_left = []
red_ghost_right = []

for i in range(num_frames):
    img = pygame.image.load(f"sprites/red-ghost-up-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    red_ghost_up.append(img)
    img = pygame.image.load(f"sprites/red-ghost-down-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    red_ghost_down.append(img)
    img = pygame.image.load(f"sprites/red-ghost-left-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    red_ghost_left.append(img)
    img = pygame.image.load(f"sprites/red-ghost-right-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    red_ghost_right.append(img)


red_ghost_sprites = {
    "up": red_ghost_up,
    "down": red_ghost_down,
    "left": red_ghost_left,
    "right": red_ghost_right
}

# Blue ghost sprites
blue_ghost_up = []
blue_ghost_down = []
blue_ghost_left = []
blue_ghost_right = []

for i in range(num_frames):
    img = pygame.image.load(f"sprites/blue-ghost-up-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    blue_ghost_up.append(img)
    img = pygame.image.load(f"sprites/blue-ghost-down-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    blue_ghost_down.append(img)
    img = pygame.image.load(f"sprites/blue-ghost-left-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    blue_ghost_left.append(img)
    img = pygame.image.load(f"sprites/blue-ghost-right-{i}.png").convert_alpha()
    w, h = img.get_size()  
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    blue_ghost_right.append(img)
    
                    
blue_ghost_sprites = {
    "up": blue_ghost_up,
    "down": blue_ghost_down,
    "left": blue_ghost_left,
    "right": blue_ghost_right
}
    
# Pink ghost sprites
pink_ghost_up = []
pink_ghost_down = []
pink_ghost_left = []
pink_ghost_right = []

for i in range(num_frames):
    img = pygame.image.load(f"sprites/pink-ghost-up-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    pink_ghost_up.append(img)
    img = pygame.image.load(f"sprites/pink-ghost-down-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    pink_ghost_down.append(img)
    img = pygame.image.load(f"sprites/pink-ghost-left-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    pink_ghost_left.append(img)
    img = pygame.image.load(f"sprites/pink-ghost-right-{i}.png").convert_alpha()
    w, h = img.get_size()   
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    pink_ghost_right.append(img)
    

pink_ghost_sprites = {
    "up": pink_ghost_up,
    "down": pink_ghost_down,
    "left": pink_ghost_left,
    "right": pink_ghost_right
}
    
# Orange ghost sprites
orange_ghost_up = []
orange_ghost_down = []
orange_ghost_left = []
orange_ghost_right = []

for i in range(num_frames):
    img = pygame.image.load(f"sprites/orange-ghost-up-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    orange_ghost_up.append(img)
    img = pygame.image.load(f"sprites/orange-ghost-down-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    orange_ghost_down.append(img)
    img = pygame.image.load(f"sprites/orange-ghost-left-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    orange_ghost_left.append(img)
    img = pygame.image.load(f"sprites/orange-ghost-right-{i}.png").convert_alpha()
    w, h = img.get_size()  
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    orange_ghost_right.append(img)

orange_ghost_sprites = {
    "up": orange_ghost_up,  
    "down": orange_ghost_down, 
    "left": orange_ghost_left,
    "right": orange_ghost_right
}

# Scared (power pellet) ghost sprites
scared_ghost = []

for i in range(num_frames):
    img = pygame.image.load(f"sprites/scared-ghost-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    scared_ghost.append(img)

# White scared (power pellet) ghost sprites
white_scared_ghost = []
    
for i in range(num_frames):
    img = pygame.image.load(f"sprites/white-scared-ghost-{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * scale_factor), int(h * scale_factor)))
    white_scared_ghost.append(img)

# Eaten ghost eyes sprites
ghost_eyes_up = pygame.image.load(f"sprites/ghost-eyes-up.png").convert_alpha()
w, h = ghost_eyes_up.get_size()
ghost_eyes_up = pygame.transform.smoothscale(ghost_eyes_up, (int(w * scale_factor), int(h * scale_factor)))

ghost_eyes_down = pygame.image.load(f"sprites/ghost-eyes-down.png").convert_alpha()
w, h = ghost_eyes_down.get_size()
ghost_eyes_down = pygame.transform.smoothscale(ghost_eyes_down, (int(w * scale_factor), int(h * scale_factor)))

ghost_eyes_left = pygame.image.load(f"sprites/ghost-eyes-left.png").convert_alpha()
w, h = ghost_eyes_left.get_size()
ghost_eyes_left = pygame.transform.smoothscale(ghost_eyes_left, (int(w * scale_factor), int(h * scale_factor)))

ghost_eyes_right = pygame.image.load(f"sprites/ghost-eyes-right.png").convert_alpha()
w, h = ghost_eyes_right.get_size()
ghost_eyes_right = pygame.transform.smoothscale(ghost_eyes_right, (int(w * scale_factor), int(h * scale_factor)))

# Ghost animation control
ghost_frame_index = 0
GHOST_FRAME_DELAY = 5  # update every 5 game ticks
ghost_frame_tick = 0

# tolerance for float comparisons (pixels)
CENTER_EPS = 0.001

# Helper to check if the ghost is centered
def is_ghost_centered(pixel_coord):
    """Return True if the ghost is (nearly) in the tile center on that axis.
       Expect tile centers to be at TILE_SIZE * n + TILE_SIZE/2.
    """
    return abs((pixel_coord % TILE_SIZE) - (TILE_SIZE / 2)) < CENTER_EPS

# Helper to snap ghost back to tile center
def snap_ghost_to_center(px, py):
    """Snap given pixel coords to exact tile center and return (x, y)."""
    r, c = get_grid_pos(px, py)
    cx = c * TILE_SIZE + TILE_SIZE / 2
    cy = r * TILE_SIZE + TILE_SIZE / 2
    return cx, cy

# Helper to get next tile in ghost_current_direction
def get_next_tile(row, col, direction):
    if direction == "up":
        return (row - 1, col)
    elif direction == "down":
        return (row + 1, col)
    elif direction == "left":
        return (row, col - 1)
    elif direction == "right":
        return (row, col + 1)

# Helper to check if next tile is walkable for ghosts
def is_direction_walkable(row, col, direction):
    nr, nc = get_next_tile(row, col, direction)
    if 0 <= nr < len(level) and 0 <= nc < len(level[0]):
        return level[nr][nc] != 1
    return False

# Gets Blinky's target tile
def get_red_target(rg_eyes):
    global player_x, player_y, red_ghost_x, red_ghost_y

    # Convert ghost pixel positions into grid coords
    r_row, r_col = get_grid_pos(red_ghost_x, red_ghost_y) 

    if near_center_reg(r_row, r_col) and not rg_eyes:
        r_ghost_speed = 1 
        return (8, 13)
    elif rg_eyes:
        r_ghost_speed = 3
        center_row = len(level) // 2
        center_col = len(level[0]) // 2
        return (center_row, center_col)
    elif ghost_mode == "chase":
        r_ghost_speed = 1
        pac_r, pac_c = get_grid_pos(player_x, player_y)
        return (pac_r, pac_c)
    elif ghost_mode == "scatter":
        r_ghost_speed = 1
        return (0, COLS-1)

# Gets Pinky's target tile
def get_pink_target(pg_eyes):
    global current_direction, player_x, player_y, pink_ghost_x, pink_ghost_y
    pac_r, pac_c = get_grid_pos(player_x, player_y)

    # Pac-Man's facing direction
    d = current_direction  # "up", "down", "left", "right"

    # Convert ghost pixel positions into grid coords
    p_row, p_col = get_grid_pos(pink_ghost_x, pink_ghost_y)

    if near_center_reg(p_row, p_col) and not pg_eyes:
        p_ghost_speed = 1
        return (8, 14)
    elif pg_eyes:
        p_ghost_speed = 3
        center_row = len(level) // 2   
        center_col = len(level[0]) // 2
        return (center_row, center_col)
    elif ghost_mode == "chase":
        p_ghost_speed = 1
        # Offset according to original behavior
        if d == "up":
            return (pac_r - 4, pac_c - 4)
        elif d == "down":
            return (pac_r + 4, pac_c)
        elif d == "left":
            return (pac_r, pac_c - 4)
        elif d == "right":
            return (pac_r, pac_c + 4)
        # fallback
        return (pac_r, pac_c)
    elif ghost_mode == "scatter":
        p_ghost_speed = 1
        return (0, 0)

# Gets Inky's target tile
def get_blue_target(blinky_x, blinky_y, bg_eyes):
    global current_direction, player_x, player_y, blue_ghost_x, blue_ghost_y

    # Convert ghost pixel positions into grid coords
    b_row, b_col = get_grid_pos(blue_ghost_x, blue_ghost_y)

    if near_center_reg(b_row, b_col) and not bg_eyes:
        b_ghost_speed = 1
        return(8, 14)
    elif bg_eyes:
        b_ghost_speed = 3
        center_row = len(level) // 2   
        center_col = len(level[0]) // 2
        return (center_row, center_col)
    elif ghost_mode == "chase":
        b_ghost_speed = 1
        # Step 1: Pac-Man's offset tile (2 ahead)
        pac_r, pac_c = get_grid_pos(player_x, player_y)
        d = current_direction

        if d == "up":
            target_r = pac_r - 2
            target_c = pac_c - 2  # ORIGINAL BUG — includes left shift
        elif d == "down":
            target_r = pac_r + 2
            target_c = pac_c
        elif d == "left":
            target_r = pac_r
            target_c = pac_c - 2
        else:
            target_r = pac_r
            target_c = pac_c + 2

        # Step 2: Blinky’s tile
        bl_r, bl_c = get_grid_pos(blinky_x, blinky_y)

        # Step 3: Vector from Blinky to the offset tile
        vec_r = target_r - bl_r
        vec_c = target_c - bl_c

        # Step 4: Double it
        final_r = bl_r + 2 * vec_r
        final_c = bl_c + 2 * vec_c

        return (final_r, final_c)
    elif ghost_mode == "scatter":
        b_ghost_speed = 1
        return(ROWS-1, COLS-1)


def get_orange_target(clyde_x, clyde_y, og_eyes):
    global player_x, player_y
    pac_r, pac_c = get_grid_pos(player_x, player_y)
    cy_r, cy_c = get_grid_pos(clyde_x, clyde_y)

    dist_sq = (pac_r - cy_r)**2 + (pac_c - cy_c)**2

    # Convert ghost pixel positions into grid coords
    o_row, o_col = get_grid_pos(orange_ghost_x, orange_ghost_y)

    if near_center_reg(o_row, o_col) and not og_eyes:
        o_ghost_speed = 1
        return (8, 13)
    elif og_eyes:
        o_ghost_speed = 3
        center_row = len(level) // 2   
        center_col = len(level[0]) // 2
        return (center_row, center_col)
    elif dist_sq >= 64:  # 8 tiles squared
        o_ghost_speed = 1
        return (pac_r, pac_c)  # chase
    else:
        o_ghost_speed = 1
        return (ROWS-1, 0)     # scatter corner

def target_frightened(ghost_x, ghost_y, ghost_eyes):
    global r_ghost_speed, b_ghost_speed, p_ghost_speed, o_ghost_speed
    # If in "eyes" mode target center tile and set speed to 3
    if ghost_eyes:
        if ghost_eyes == rg_eyes:
            r_ghost_speed = 3
        if ghost_eyes == bg_eyes:
            b_ghost_speed = 3
        if ghost_eyes == pg_eyes:
            p_ghost_speed = 3
        if ghost_eyes == og_eyes:
            o_ghost_speed = 3
        center_row = len(level) // 2
        center_col = len(level[0]) // 2
        return (center_row, center_col)
    # If not in "eyes" mode but still frightened set speed to 1 (to be safe) and target random tile
    else:
        if ghost_eyes == rg_eyes:
            r_ghost_speed = 1
        elif ghost_eyes == bg_eyes:
            b_ghost_speed = 1
        elif ghost_eyes == pg_eyes:
            p_ghost_speed = 1
        elif ghost_eyes == og_eyes:
            o_ghost_speed = 1
        row, col = get_grid_pos(ghost_x, ghost_y)
        possible = []

        for d in ["up","left","down","right"]:
            if is_direction_walkable(row, col, d):
                possible.append(d)
    
        if possible:
            return get_next_tile(row, col, random.choice(possible))
        else:
            return (row, col)

# Chooses ghosts direction based on their specific target tile
def choose_ghost_direction(ghost_x, ghost_y, ghost_current_direction, target):
    # ensure we have a valid starting direction
    if ghost_current_direction is None:
        ghost_current_direction = "left"  # or any sensible default

    row, col = get_grid_pos(ghost_x, ghost_y)
    opposite = {"up":"down", "down":"up", "left":"right", "right":"left"}

    possible = []
    for d in ["up", "left", "down", "right"]:   # tie-break order (Up, Left, Down, Right)
        # avoid reversing unless it's the only option
        if d == opposite.get(ghost_current_direction):
            continue
        if is_direction_walkable(row, col, d):
            possible.append(d)

    # if no possible moves (dead end), allow reverse
    if not possible:
        rev = opposite.get(ghost_current_direction)
        if rev and is_direction_walkable(row, col, rev):
            return rev
        # if still nothing, just keep current (should not happen)
        return ghost_current_direction

    # choose direction minimizing distance to target (squared distance)
    best_dir = ghost_current_direction
    best_dist = float("inf")
    for d in possible:
        nr, nc = get_next_tile(row, col, d)
        dist = (nr - target[0])**2 + (nc - target[1])**2
        if dist < best_dist:
            best_dist = dist
            best_dir = d

    return best_dir

def is_ghost_collision(px, py, gx, gy):
    dx = px - gx
    dy = py - gy
    dist_sq = dx*dx + dy*dy
    if dist_sq < COLLISION_DISTANCE * COLLISION_DISTANCE:
        return True

def eat_ghost(color):
    global ghost_eaten, ghost_eaten_color, ghost_eaten_timer, player_score, ghost_eat_score, p_one_up

    ghost_eaten = True
    ghost_eaten_color = color
    ghost_eaten_timer = 0

    # play sound
    eating_ghost.play()

    player_score += ghost_eat_score
    p_one_up += ghost_eat_score

def restart_game():
    global game_start, player_lives, game_start_timer, player_x, player_y, red_ghost_x, red_ghost_y, blue_ghost_x, blue_ghost_y, pink_ghost_x, pink_ghost_y, orange_ghost_x, orange_ghost_y, current_direction,pacman_frame_index, next_direction, pacman_frame_tick, red_direction, red_last_dir, pink_direction, pink_last_dir, blue_direction, blue_last_dir, orange_direction, orange_last_dir, r_ghost_speed, b_ghost_speed, p_ghost_speed, o_ghost_speed, rg_eyes, bg_eyes, pg_eyes, og_eyes, player_speed, play_once
    game_start = True
    game_start_timer = 120
    player_lives -= 1
    player_speed = 2
    play_once = False

    # Reset red ghost starting position and speed
    red_ghost_x = TILE_SIZE * 13 + TILE_SIZE/2
    red_ghost_y = TILE_SIZE * 10 + TILE_SIZE/2
    r_ghost_speed = 1
    rg_eyes = False
    
    # Reset pink ghost starting position and speed
    pink_ghost_x = TILE_SIZE * 13 + TILE_SIZE/2
    pink_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2
    p_ghost_speed = 1
    pg_eyes = False    

    # Reset blue ghost starting position and speed
    blue_ghost_x = TILE_SIZE * 12 + TILE_SIZE/2
    blue_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2
    b_ghost_speed = 1
    bg_eyes = False
     
    # Reset orange ghost starting positions and speed
    orange_ghost_x = TILE_SIZE * 14 + TILE_SIZE/2
    orange_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2
    o_ghost_speed = 1
    og_eyes = False

    # Ghost directional variables
    red_direction = "left"          # current movement direction
    red_last_dir = "left"           # needed to prevent reversing
    
    pink_direction = "down"
    pink_last_dir = "down"
    
    blue_direction = "up"
    blue_last_dir = "up"
   
    orange_direction = "up"
    orange_last_dir = "up"

    # Reset player position and mouth angle
    pacman_frame_index = 0
    pacman_frame_tick = 0
    current_direction = None
    next_direction = None
    if chosen_lvl == 1:
        player_x = TILE_SIZE * 13.5
        player_y = TILE_SIZE * 20.5
    elif chosen_lvl == 2:
        player_x = TILE_SIZE * 13.5
        player_y = TILE_SIZE * 19.5

# Tolerance: within 1 tile of the center to let ghosts turn back into ghosts from eyes
def near_center(gr, gc):
    center_row = len(level) // 2
    center_col = len(level[0]) // 2
    return abs(gr - center_row) <= 1 and abs(gc - center_col) <= 1

# Tolerance: within 4 tiles of the center to make the ghosts leave their house
def near_center_reg(gr, gc):
    center_row = len(level) // 2
    center_col = len(level[0]) // 2
    return abs(gr - center_row) <= 4 and abs(gc - center_col) <= 4

def check_center_tile():
    global red_ghost_x, red_ghost_y, pink_ghost_x, pink_ghost_y, blue_ghost_x, blue_ghost_y, orange_ghost_x, orange_ghost_y, rg_eyes, bg_eyes, pg_eyes, og_eyes, r_ghost_speed, b_ghost_speed, p_ghost_speed, o_ghost_speed

    center_row = len(level) // 2
    center_col = len(level[0]) // 2

    # Convert ghost pixel positions into grid coords
    r_row, r_col = get_grid_pos(red_ghost_x, red_ghost_y)
    b_row, b_col = get_grid_pos(blue_ghost_x, blue_ghost_y)
    p_row, p_col = get_grid_pos(pink_ghost_x, pink_ghost_y)
    o_row, o_col = get_grid_pos(orange_ghost_x, orange_ghost_y)

    if rg_eyes and near_center(r_row, r_col):
        rg_eyes = False
        r_ghost_speed = 1

    if bg_eyes and near_center(b_row, b_col):
        bg_eyes = False
        b_ghost_speed = 1

    if pg_eyes and near_center(p_row, p_col):
        pg_eyes = False
        p_ghost_speed = 1

    if og_eyes and near_center(o_row, o_col):
        og_eyes = False
        o_ghost_speed = 1

def check_if_off_screen():
    global red_ghost_x, red_ghost_y, pink_ghost_x, pink_ghost_y, blue_ghost_x, blue_ghost_y, orange_ghost_x, orange_ghost_y, screen_width, screen_height

    if red_ghost_x < -TILE_SIZE or red_ghost_x > screen_width + TILE_SIZE or red_ghost_y < -TILE_SIZE or red_ghost_y > screen_height + TILE_SIZE:
        red_ghost_x = TILE_SIZE * 13 + TILE_SIZE/2
        red_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2
    if pink_ghost_x < -TILE_SIZE or pink_ghost_x > screen_width + TILE_SIZE or pink_ghost_y < -TILE_SIZE or pink_ghost_y > screen_height + TILE_SIZE:
        pink_ghost_x = TILE_SIZE * 13 + TILE_SIZE/2
        pink_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2
    if blue_ghost_x < -TILE_SIZE or blue_ghost_x > screen_width + TILE_SIZE or blue_ghost_y < -TILE_SIZE or blue_ghost_y > screen_height + TILE_SIZE:
        blue_ghost_x = TILE_SIZE * 12 + TILE_SIZE/2
        blue_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2
    if orange_ghost_x < -TILE_SIZE or orange_ghost_x > screen_width + TILE_SIZE or orange_ghost_y < -TILE_SIZE or orange_ghost_y > screen_height + TILE_SIZE:
        orange_ghost_x = TILE_SIZE * 14 + TILE_SIZE/2
        orange_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2

def reset_game_vars():
    global player_x, player_y, player_score, p_one_up, eaten_pellets, player_lives, game_start, game_start_timer, play_once, init_spawn, g_siren_start, power_pellet_flipper, current_direction, next_direction, player_speed, pacman_frame_index, pacman_frame_tick, start, end, endL, startL, red_ghost_direction, red_last_dir, pink_ghost_direction, pink_last_dir, blue_ghost_direction, blue_last_dir, orange_ghost_direction, orange_last_dir, ghost_eat_score, rg_eyes, pg_eyes, bg_eyes, og_eyes, ghost_eaten, ghost_eaten_color, ghost_eaten_timer, pickup_frame, pickup_x, pickup_y, pickup_for_level, item_score_timer, pickup_score, red_ghost_x, red_ghost_y, pink_ghost_x, pink_ghost_y, blue_ghost_x, blue_ghost_y, orange_ghost_x, orange_ghost_y, r_ghost_speed, p_ghost_speed, b_ghost_speed, o_ghost_speed, start_timer, power_pellet_flipper_start_screen, start_chase_timer, start_screen_pac_x, start_screen_pac_y, start_screen_draw_x_red, start_screen_draw_x_pink, start_screen_draw_x_blue, start_screen_draw_x_orange, start_screen_draw_y, eaten_start_power_pellet, pacman_start_screen_right_frame, start_eaten_pause, start_eaten_red, start_eaten_pink, start_eaten_blue, start_eaten_orange, start_screen_ghost_eat_score, start_screen_ghost_eaten_timer

    pygame.mixer.music.load("sounds/Pac-Man starting sound effect.mp3")

    # Reset start sequence vars
    power_pellet_flipper_start_screen = True
    start_chase_timer = 0.0
    start_screen_pac_x = screen_width + 30
    start_screen_pac_y = screen_height//2-10
    start_screen_draw_x_red = screen_width + 75
    start_screen_draw_x_pink = screen_width + 110
    start_screen_draw_x_blue = screen_width + 145
    start_screen_draw_x_orange = screen_width + 180
    start_screen_draw_y = screen_height//2-10
    eaten_start_power_pellet = False
    pacman_start_screen_right_frame = 0
    start_eaten_pause = False
    start_eaten_red = False
    start_eaten_pink = False
    start_eaten_blue = False
    start_eaten_orange = False
    start_screen_ghost_eat_score = 200
    start_screen_ghost_eaten_timer = 0

    # Reset player and ghost positions and speeds
    if chosen_lvl == 1:
        player_x = TILE_SIZE * 13.5
        player_y = TILE_SIZE * 20.5
    elif chosen_lvl == 2:
        player_x = TILE_SIZE * 13.5
        player_y = TILE_SIZE * 19.5

    # Reset red ghost starting position and speed
    red_ghost_x = TILE_SIZE * 13 + TILE_SIZE/2
    red_ghost_y = TILE_SIZE * 10 + TILE_SIZE/2
    r_ghost_speed = 1

    # Reset pink ghost starting position and speed
    pink_ghost_x = TILE_SIZE * 13 + TILE_SIZE/2
    pink_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2
    p_ghost_speed = 1

    # Reset blue ghost starting position and speed
    blue_ghost_x = TILE_SIZE * 12 + TILE_SIZE/2
    blue_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2
    b_ghost_speed = 1

    # Reset orange ghost starting position and speed
    orange_ghost_x = TILE_SIZE * 14 + TILE_SIZE/2
    orange_ghost_y = TILE_SIZE * 13 + TILE_SIZE/2
    o_ghost_speed = 1

    start_timer = 0.0

    # Lives and Score
    player_score = 0
    p_one_up = 0
    eaten_pellets = 0
    player_lives = 3

    # Game start variables
    game_start = True
    game_start_timer = 0
    play_once = True
    init_spawn = True
    g_siren_start = True

    # Power Pellet "Blinking" Variables
    power_pellet_flipper = True

    current_direction = None
    next_direction = None
    player_speed = 2

    pacman_frame_index = 0
    pacman_frame_tick = 0

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

    # Fruits/Pickups vars
    pickup_frame = 0
    pickup_x = 0
    pickup_y = 0
    pickup_for_level = False
    item_score_timer = 0
    pickup_score = 0
    

clock = pygame.time.Clock()

# Game loop
running = True
while running:

    # Black background
    screen.fill(BLACK)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Starting screen
    if game_state == "START_SCREEN":

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            credit_sound.play()
            game_state = "PRESS_PLAY"

        dt = clock.get_time() / 1000.0  # convert ms → seconds

        if start_timer <= 23.0:
            PRESS_ENTER = render_stretched_text("PRESS  ENTER  OR  RETURN", WHITE, ready_font, scale_x=1.3)
            p_e_rect = PRESS_ENTER.get_rect(center=(screen_width//2, screen_height//2-425))
            screen.blit(PRESS_ENTER, p_e_rect)

            CHARACTER_NICKNAME = render_stretched_text("CHARACTER   /   NICKNAME", WHITE, ready_font, scale_x=1.3)
            c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2, screen_height//2-350))
            screen.blit(CHARACTER_NICKNAME, c_n_rect)

        start_timer += dt

        # Draw red ghost + info
        if start_timer >= 1.5 and start_timer <= 23.0:
            # --- draw Red Ghost ---
            ghost_img = red_ghost_sprites["right"][0]
            screen.blit(ghost_img, (185, 140))
            if start_timer >= 2.0 and start_timer <= 23.0:
                CHARACTER_NICKNAME = render_stretched_text("- SHADOW", (255, 0, 0), ready_font, scale_x=1.3)
                c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2-110, screen_height//2-313))
                screen.blit(CHARACTER_NICKNAME, c_n_rect)
            if start_timer >= 2.5 and start_timer <= 23.0:
                CHARACTER_NICKNAME = render_stretched_text('"BLINKY"', (255, 0, 0), ready_font, scale_x=1.3)
                c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2+100, screen_height//2-313))
                screen.blit(CHARACTER_NICKNAME, c_n_rect)

        # Draw pink ghost + info
        if start_timer >= 3.5 and start_timer <= 23.0:
            # --- draw Pink Ghost ---
            ghost_img = pink_ghost_sprites["right"][0]
            screen.blit(ghost_img, (185, 200))
            if start_timer >= 4.0 and start_timer <= 23.0:
                CHARACTER_NICKNAME = render_stretched_text("- SPEEDY", (255, 184, 255), ready_font, scale_x=1.3)
                c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2-113, screen_height//2-253))
                screen.blit(CHARACTER_NICKNAME, c_n_rect)
            if start_timer >= 4.5 and start_timer <= 23.0:
                CHARACTER_NICKNAME = render_stretched_text('"PINKY"', (255, 184, 255), ready_font, scale_x=1.3)
                c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2+90, screen_height//2-253))
                screen.blit(CHARACTER_NICKNAME, c_n_rect)

        # Draw blue ghost + info
        if start_timer >= 5.5 and start_timer <= 23.0:
            # --- draw Blue Ghost ---
            ghost_img = blue_ghost_sprites["right"][0]
            screen.blit(ghost_img, (185, 260))
            if start_timer >= 6.0 and start_timer <= 23.0:   
                CHARACTER_NICKNAME = render_stretched_text("- BASHFUL", CYAN, ready_font, scale_x=1.3)
                c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2-102, screen_height//2-193))
                screen.blit(CHARACTER_NICKNAME, c_n_rect)
            if start_timer >= 6.5 and start_timer <= 23.0:  
                CHARACTER_NICKNAME = render_stretched_text('"INKY"', CYAN, ready_font, scale_x=1.3)
                c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2+80, screen_height//2-193))
                screen.blit(CHARACTER_NICKNAME, c_n_rect)

        # Draw orange ghost + info
        if start_timer >= 7.5 and start_timer <= 23.0:
            # --- draw Orange Ghost ---
            ghost_img = orange_ghost_sprites["right"][0]
            screen.blit(ghost_img, (185, 320))
            if start_timer >= 8.0 and start_timer <= 23.0:
                CHARACTER_NICKNAME = render_stretched_text("- POKEY", (255, 184, 82), ready_font, scale_x=1.3)
                c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2-121, screen_height//2-133))
                screen.blit(CHARACTER_NICKNAME, c_n_rect)
            if start_timer >= 8.5 and start_timer <= 23.0:
                CHARACTER_NICKNAME = render_stretched_text('"CLYDE"', (255, 184, 82), ready_font, scale_x=1.3)
                c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2+94, screen_height//2-133))
                screen.blit(CHARACTER_NICKNAME, c_n_rect)

        # Draw pellets info
        if start_timer >= 9.5 and start_timer <= 23.0:
            # Draw base pellet + info
            pygame.draw.circle(screen, PEACH, (screen_width//2-100, screen_height//2+100), TILE_SIZE // 2 - 12)
            CHARACTER_NICKNAME = render_stretched_text("10", WHITE, ready_font, scale_x=1.3)
            c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2-50, screen_height//2+98))
            screen.blit(CHARACTER_NICKNAME, c_n_rect)
            CHARACTER_NICKNAME = render_stretched_text("PTS", WHITE, g_eat_font, scale_x=1.6)
            c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2+10, screen_height//2+100))
            screen.blit(CHARACTER_NICKNAME, c_n_rect)

            # Draw power pellet + info
            if power_pellet_flipper_start_screen:
                power_color = PEACH
            else:
                power_color = BLACK
            pygame.draw.circle(screen, power_color, (screen_width//2-100, screen_height//2+140), TILE_SIZE // 2 - 5)
            CHARACTER_NICKNAME = render_stretched_text("50", WHITE, ready_font, scale_x=1.3)
            c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2-50, screen_height//2+138))
            screen.blit(CHARACTER_NICKNAME, c_n_rect)
            CHARACTER_NICKNAME = render_stretched_text("PTS", WHITE, g_eat_font, scale_x=1.6)
            c_n_rect = CHARACTER_NICKNAME.get_rect(center=(screen_width//2+10, screen_height//2+140))
            screen.blit(CHARACTER_NICKNAME, c_n_rect)

        # Demo power pellet
        if start_timer >= 10.5 and start_timer <= 23.0:
            if not eaten_start_power_pellet:
                # Draw power pellet for pacman to eat
                if power_pellet_flipper_start_screen:
                    power_color = PEACH
                else:
                    power_color = BLACK
                pygame.draw.circle(screen, power_color, (185, screen_height//2), TILE_SIZE // 2 - 5)

        # Begin "blinking" power pellet and pacman ghost sequence
        if start_timer >= 11.5 and start_timer <= 23.0:
            current_start_screen_time = pygame.time.get_ticks()

            start_chase_timer += dt
            FRAME_SPEED = 0.04
            PAC_MOVE_SPEED = 175
            GHOST_MOVE_SPEED = 179

            # Ghosts chasing pacman
            if (not abs(start_screen_pac_x - 185) < 2) and (not eaten_start_power_pellet):

                # --- advance animation frames ---   
                if start_chase_timer >= FRAME_SPEED:
                    start_chase_timer = 0
                
                    # Pac-Man anim
                    pacman_intermission_frame = (pacman_intermission_frame + 2) % len(pacman_intermission_frames)
                
                    # Ghost anim
                    ghost_intermission_index = (ghost_intermission_index + 1) % len(red_ghost_sprites["left"])

                # --- move sprites ---
                start_screen_pac_x -= PAC_MOVE_SPEED * dt
                start_screen_draw_x_red -= GHOST_MOVE_SPEED * dt
                start_screen_draw_x_pink -= GHOST_MOVE_SPEED * dt
                start_screen_draw_x_blue -= GHOST_MOVE_SPEED * dt
                start_screen_draw_x_orange -= GHOST_MOVE_SPEED * dt
                
                # --- draw Pac-Man ---
                pac_img = pacman_intermission_frames[pacman_intermission_frame]
                screen.blit(pac_img, (start_screen_pac_x, start_screen_pac_y))
        
                # --- draw Red Ghost --- 
                ghost_img = red_ghost_sprites["left"][ghost_intermission_index]
                screen.blit(ghost_img, (start_screen_draw_x_red, start_screen_draw_y))

                # --- draw Pink Ghost ---
                ghost_img = pink_ghost_sprites["left"][ghost_intermission_index]
                screen.blit(ghost_img, (start_screen_draw_x_pink, start_screen_draw_y))

                # --- draw Blue Ghost ---
                ghost_img = blue_ghost_sprites["left"][ghost_intermission_index]
                screen.blit(ghost_img, (start_screen_draw_x_blue, start_screen_draw_y))
            
                # --- draw Orange Ghost ---
                ghost_img = orange_ghost_sprites["left"][ghost_intermission_index]
                screen.blit(ghost_img, (start_screen_draw_x_orange, start_screen_draw_y))

            # Pacman chasing ghosts
            else:
                eaten_start_power_pellet = True
                PAC_MOVE_SPEED = 190
                GHOST_MOVE_SPEED = 145

                if not start_eaten_pause:

                    # --- advance animation frames ---
                    if start_chase_timer >= FRAME_SPEED:
                        start_chase_timer = 0
                
                        # Pac-Man anim
                        pacman_start_screen_right_frame = (pacman_start_screen_right_frame + 1) % len(pacman_start_screen_right_frames)
                
                        # Ghost anim
                        ghost_intermission_index = (ghost_intermission_index + 1) % len(red_ghost_sprites["right"])

                    # --- move sprites ---   
                    start_screen_pac_x += PAC_MOVE_SPEED * dt
                    start_screen_draw_x_red += GHOST_MOVE_SPEED * dt
                    start_screen_draw_x_pink += GHOST_MOVE_SPEED * dt
                    start_screen_draw_x_blue += GHOST_MOVE_SPEED * dt
                    start_screen_draw_x_orange += GHOST_MOVE_SPEED * dt
                    
                    # --- draw Pac-Man ---
                    pac_img = pacman_start_screen_right_frames[pacman_start_screen_right_frame]
                    screen.blit(pac_img, (start_screen_pac_x, start_screen_pac_y))

                    ghost_img = scared_ghost[ghost_intermission_index]

                    if abs(start_screen_pac_x - start_screen_draw_x_red) < 6:
                        start_eaten_pause = True
                        start_eaten_red = True
                        start_screen_draw_x_red = 0            
                    if abs(start_screen_pac_x - start_screen_draw_x_pink) < 6:
                        start_eaten_pause = True
                        start_eaten_pink = True
                        start_screen_draw_x_pink = 0
                    if abs(start_screen_pac_x - start_screen_draw_x_blue) < 6:
                        start_eaten_pause = True
                        start_eaten_blue = True
                        start_screen_draw_x_blue = 0
                    if abs(start_screen_pac_x - start_screen_draw_x_orange) < 6:
                        start_eaten_pause = True
                        start_eaten_orange = True
                        start_screen_draw_x_orange = 0

                    if not start_eaten_red:
                        # --- draw Red Ghost ---
                        screen.blit(ghost_img, (start_screen_draw_x_red, start_screen_draw_y))
    
                    if not start_eaten_pink:
                        # --- draw Pink Ghost ---
                        screen.blit(ghost_img, (start_screen_draw_x_pink, start_screen_draw_y))
            
                    if not start_eaten_blue:
                        # --- draw Blue Ghost ---
                        screen.blit(ghost_img, (start_screen_draw_x_blue, start_screen_draw_y))

                    if not start_eaten_orange:
                        # --- draw Orange Ghost ---
                        screen.blit(ghost_img, (start_screen_draw_x_orange, start_screen_draw_y))

                # Eaten pause sequence
                else:
                    start_screen_ghost_eaten_timer += dt
                    PAC_MOVE_SPEED = 0
                    GHOST_MOVE_SPEED = 0

                    if not start_eaten_red:
                        # --- draw Red Ghost ---
                        screen.blit(scared_ghost[0], (start_screen_draw_x_red, start_screen_draw_y))
                        
                    if not start_eaten_pink:
                        # --- draw Pink Ghost ---
                        screen.blit(scared_ghost[0], (start_screen_draw_x_pink, start_screen_draw_y))
                    
                    if not start_eaten_blue:
                        # --- draw Blue Ghost ---
                        screen.blit(scared_ghost[0], (start_screen_draw_x_blue, start_screen_draw_y))

                    if not start_eaten_orange:
                        # --- draw Orange Ghost ---
                        screen.blit(scared_ghost[0], (start_screen_draw_x_orange, start_screen_draw_y))

                    # Eaten score
                    EATEN_SCORE = g_eat_font.render(str(start_screen_ghost_eat_score), True, CYAN)
                    eaten_score_rect = EATEN_SCORE.get_rect(center=(start_screen_pac_x+20, start_screen_pac_y+10))
                    screen.blit(EATEN_SCORE, eaten_score_rect)

                    if start_screen_ghost_eaten_timer >= ghost_eaten_duration:
                        start_eaten_pause = False
                        start_screen_ghost_eaten_timer = 0
                        start_screen_ghost_eat_score *= 2

            # Keeps track of time passed and flips power_pellet_flipper_start_screen to create a "blinking" effect for power pellets
            # Occurs once every 200 milliseconds
            if current_start_screen_time - last_pellet_blink_start_screen > POWER_PELLET_BLINK_INTERVAL:
                power_pellet_flipper_start_screen = not power_pellet_flipper_start_screen
                last_pellet_blink_start_screen = current_start_screen_time

        if start_timer > 23.0:
            # Starting Screen vars
            start_timer = 0.0
            power_pellet_flipper_start_screen = True
            start_chase_timer = 0.0
            start_screen_pac_x = screen_width + 30
            start_screen_pac_y = screen_height//2-10
            start_screen_draw_x_red = screen_width + 75
            start_screen_draw_x_pink = screen_width + 110
            start_screen_draw_x_blue = screen_width + 145
            start_screen_draw_x_orange = screen_width + 180
            start_screen_draw_y = screen_height//2-10
            eaten_start_power_pellet = False
            pacman_start_screen_right_frame = 0
            start_eaten_pause = False
            start_eaten_red = False
            start_eaten_pink = False
            start_eaten_blue = False
            start_eaten_orange = False
            start_screen_ghost_eat_score = 200
            start_screen_ghost_eaten_timer = 0

    # Draws press play screen (would be after inserting token in arcade machine)
    elif game_state == "PRESS_PLAY":

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = "GAME_PLAY"

        PUSH_BUTTON = render_stretched_text("PUSH  SPACE  BUTTON", (255, 184, 82), ready_font, scale_x=1.3)
        p_b_rect = PUSH_BUTTON.get_rect(center=(screen_width//2, screen_height//2-210))
        screen.blit(PUSH_BUTTON, p_b_rect)

        ONE_PLAYER = render_stretched_text("1  PLAYER  ONLY", CYAN, ready_font, scale_x=1.3)
        o_p_rect = ONE_PLAYER.get_rect(center=(screen_width//2, screen_height//2-110))
        screen.blit(ONE_PLAYER, o_p_rect)

        BONUS_PAC = render_stretched_text("BONUS  PAC-MAN  FOR  10000", PEACH, ready_font, scale_x=1.3)
        p_b_rect = BONUS_PAC.get_rect(center=(screen_width//2-30, screen_height//2-10))
        screen.blit(BONUS_PAC, p_b_rect)

        PTS = render_stretched_text("PTS", PEACH, g_eat_font, scale_x=1.6)
        p_t_rect = PTS.get_rect(center=(screen_width//2+217, screen_height//2-8))
        screen.blit(PTS, p_t_rect)

    # Intermission #1
    elif game_state == "INTERMISSION":

        if not intermission_play_song_once:
            intermission_song.play()
            intermission_play_song_once = True

        dt = clock.get_time() / 1000.0  # convert ms → seconds

        if INTERMISSION_PHASE == 1:

            # --- update timers ---
            intermission_timer += dt
            FRAME_SPEED = 0.04     # seconds per frame
            PAC_MOVE_SPEED = 175        # pixels per second
            GHOST_MOVE_SPEED = 181        # pixels per second

            # --- advance animation frames ---
            if intermission_timer >= FRAME_SPEED:
                intermission_timer = 0

                # Pac-Man anim
                pacman_intermission_frame = (pacman_intermission_frame + 1) % len(pacman_intermission_frames)

                # Ghost anim
                ghost_intermission_index = (ghost_intermission_index + 1) % len(red_ghost_sprites["left"])

            # --- move sprites ---
            intermission_pac_x -= PAC_MOVE_SPEED * dt
            g_intermission_draw_x -= GHOST_MOVE_SPEED * dt

            # --- draw Pac-Man ---
            pac_img = pacman_intermission_frames[pacman_intermission_frame]
            screen.blit(pac_img, (intermission_pac_x, intermission_pac_y))

            # --- draw Red Ghost ---
            ghost_img = red_ghost_sprites["left"][ghost_intermission_index]
            screen.blit(ghost_img, (g_intermission_draw_x, g_intermission_draw_y))

        # ---- PHASE SWITCH ----
        if g_intermission_draw_x < -40:
            # Flip directions
            INTERMISSION_PHASE = 2

            # reposition for phase 2
            intermission_pac_x = -175    # pacman now starts farther on the left
            intermission_pac_y = screen_height // 2 - 35 # Need to adjust for big pacman
            g_intermission_draw_x = -35   # ghost comes in from the left

            # reset frames for right-facing movement
            pacman_intermission_frame = 0
            ghost_intermission_index = 0

        elif INTERMISSION_PHASE == 2:
            intermission_timer += dt
            FRAME_SPEED = 0.06
            PAC_MOVE_SPEED = 191       # pac-man is *faster* now
            GHOST_MOVE_SPEED = 175     # ghost slower (he’s scared)

            if intermission_timer >= FRAME_SPEED:
                intermission_timer = 0
                pacman_intermission_frame = (pacman_intermission_frame + 1) % len(pacman_intermission_frames_big)
                ghost_intermission_index = (ghost_intermission_index + 1) % len(scared_ghost)

            # move RIGHT
            intermission_pac_x += PAC_MOVE_SPEED * dt
            g_intermission_draw_x += GHOST_MOVE_SPEED * dt

            # draw right-facing sprites
            pac_img = pacman_intermission_frames_big[pacman_intermission_frame]
            ghost_img = scared_ghost[ghost_intermission_index]

            screen.blit(pac_img, (intermission_pac_x, intermission_pac_y))
            screen.blit(ghost_img, (g_intermission_draw_x, g_intermission_draw_y))

            # ---- END OF INTERMISSION ----
            if intermission_pac_x > screen_width + 80:
                game_state = "GAMEPLAY"
                # reset for next time
                INTERMISSION_PHASE = 1
                intermission_play_song_once = False 
                restart_game()


    else:

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

            # Draw Items picked-up in bottom right of screen
            SPACING = 8
            item_w = scaled_pickups[0].get_width()
            start_x = screen_width - item_w - 10
            y = screen_height - item_w - 10

            for i in range(pickup_frame):
                x = start_x - i * (item_w + SPACING)
                screen.blit(scaled_pickups[i], (x, y))

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

                    # Draw Ghosts
                    r_ghost_frames = red_ghost_sprites[red_direction]
                    frame = r_ghost_frames[ghost_frame_index] 
                    draw_x = red_ghost_x - frame.get_width()/2 
                    draw_y = red_ghost_y - frame.get_height()/2
                    screen.blit(frame, (draw_x, draw_y))
                
                    b_ghost_frames = blue_ghost_sprites[blue_direction]
                    frame = b_ghost_frames[ghost_frame_index]   
                    draw_x = blue_ghost_x - frame.get_width()/2 
                    draw_y = blue_ghost_y - frame.get_height()/2
                    screen.blit(frame, (draw_x, draw_y))
                
                    p_ghost_frames = pink_ghost_sprites[pink_direction]
                    frame = p_ghost_frames[ghost_frame_index]   
                    draw_x = pink_ghost_x - frame.get_width()/2 
                    draw_y = pink_ghost_y - frame.get_height()/2
                    screen.blit(frame, (draw_x, draw_y))
                
                    o_ghost_frames = orange_ghost_sprites[orange_direction]
                    frame = o_ghost_frames[ghost_frame_index]
                    draw_x = orange_ghost_x - frame.get_width()/2 
                    draw_y = orange_ghost_y - frame.get_height()/2
                    screen.blit(frame, (draw_x, draw_y))

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

                    # Draw Ghosts
                    r_ghost_frames = red_ghost_sprites[red_direction]
                    frame = r_ghost_frames[ghost_frame_index]
                    draw_x = red_ghost_x - frame.get_width()/2
                    draw_y = red_ghost_y - frame.get_height()/2
                    screen.blit(frame, (draw_x, draw_y))

                    b_ghost_frames = blue_ghost_sprites[blue_direction]
                    frame = b_ghost_frames[ghost_frame_index]
                    draw_x = blue_ghost_x - frame.get_width()/2 
                    draw_y = blue_ghost_y - frame.get_height()/2
                    screen.blit(frame, (draw_x, draw_y))

                    p_ghost_frames = pink_ghost_sprites[pink_direction]
                    frame = p_ghost_frames[ghost_frame_index]
                    draw_x = pink_ghost_x - frame.get_width()/2 
                    draw_y = pink_ghost_y - frame.get_height()/2
                    screen.blit(frame, (draw_x, draw_y))

                    o_ghost_frames = orange_ghost_sprites[orange_direction]
                    frame = o_ghost_frames[ghost_frame_index]
                    draw_x = orange_ghost_x - frame.get_width()/2 
                    draw_y = orange_ghost_y - frame.get_height()/2
                    screen.blit(frame, (draw_x, draw_y))

                # After the duration, exit start state
                if game_start_timer >= GAME_START_DURATION:
                    game_start = False
        # If not in "Game Intro" state, run the following
        else:

            if p_one_up >= 10000:
                one_up.play()
                player_lives += 1
                p_one_up = 0

            # Check if a ghost went off screen, reset to starting position if so
            check_if_off_screen()
  
            if frightened_mode:

                # Spawn item pickup in frightened mode if needed
                if eaten_pellets >= 100 and eaten_pellets < 150:
                
                    # Spawn item pickup
                    if not pickup_for_level:
                        if chosen_lvl == 1:
                            pickup_x = TILE_SIZE * 13.5
                            pickup_y = TILE_SIZE * 20.5 - 13
                        elif chosen_lvl == 2:
                            pickup_x = TILE_SIZE * 13.5
                            pickup_y = TILE_SIZE * 19.5 - 13
                        screen.blit(pickup_frames[pickup_frame], (pickup_x, pickup_y))
                    if item_score_timer <= 1 and pickup_for_level:
                        PICKUP_SCORE = g_eat_font.render(str(pickup_score), True, CYAN)
                        pickup_score_rect = PICKUP_SCORE.get_rect(center=(pickup_x+TILE_SIZE//2, pickup_y+TILE_SIZE//2 - 2))
                        screen.blit(PICKUP_SCORE, pickup_score_rect)
                        item_score_timer += dt
                else:
                    pickup_x = 0
                    pickup_y = 0

                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load("sounds/frightenedMode.mp3")
                    pygame.mixer.music.play()

                # Check for level completion and reset level if so (case of completing level in frightened state)
                if eaten_pellets == lvl1MinEaten and chosen_lvl == 1:
                    level = generate_level()
                    eaten_pellets = 0
                    player_lives += 1
                    frightened_mode = False
                    pickup_for_level = False
                    completed_lvls += 1
                    if completed_lvls == 2:
                        game_state = "INTERMISSION"
                    else:
                        restart_game()
                elif eaten_pellets == lvl2MinEaten and chosen_lvl == 2:
                    level = generate_level()
                    eaten_pellets = 0
                    player_lives += 1
                    frightened_mode = False
                    pickup_for_level = False
                    completed_lvls += 1
                    if completed_lvls == 2:
                        game_state = "INTERMISSION"
                    else:
                        restart_game()
                
            else:
                if not pacman_dying:
                    # Plays ghost siren only once so it does not keep playing
                    if eaten_pellets < 50:
                        pickup_x = 0
                        pickup_y = 0
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.load("sounds/ghost_siren1.mp3")
                            pygame.mixer.music.play()
                    elif eaten_pellets >= 50 and eaten_pellets < 100:
                        pickup_x = 0
                        pickup_y = 0
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.load("sounds/ghost_siren2.mp3")
                            pygame.mixer.music.play()
                    elif eaten_pellets >= 100 and eaten_pellets < 150:

                        # Spawn item pickup
                        if not pickup_for_level:
                            if chosen_lvl == 1:
                                pickup_x = TILE_SIZE * 13.5
                                pickup_y = TILE_SIZE * 20.5 - 13
                            elif chosen_lvl == 2:
                                pickup_x = TILE_SIZE * 13.5
                                pickup_y = TILE_SIZE * 19.5 - 13
                            screen.blit(pickup_frames[pickup_frame], (pickup_x, pickup_y))
                        if item_score_timer <= 1 and pickup_for_level:
                            PICKUP_SCORE = g_eat_font.render(str(pickup_score), True, CYAN)
                            pickup_score_rect = PICKUP_SCORE.get_rect(center=(pickup_x+TILE_SIZE//2, pickup_y+TILE_SIZE//2 - 2))
                            screen.blit(PICKUP_SCORE, pickup_score_rect)
                            item_score_timer += dt

                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.load("sounds/ghost_siren3.mp3")
                            pygame.mixer.music.play()
                    elif eaten_pellets >= 150 and eaten_pellets < 200:
                        pickup_x = 0
                        pickup_y = 0
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.load("sounds/ghost_siren4.mp3")
                            pygame.mixer.music.play()
                    elif eaten_pellets >= 200 and eaten_pellets < 233:
                        pickup_x = 0
                        pickup_y = 0
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.load("sounds/ghost_siren5.mp3")
                            pygame.mixer.music.play()
                # Check for level completion and reset level if so
                if eaten_pellets == lvl1MinEaten and chosen_lvl == 1:
                    level = generate_level()
                    eaten_pellets = 0
                    frightened_mode = False
                    player_lives += 1
                    pickup_for_level = False
                    completed_lvls += 1
                    restart_game()
                    if completed_lvls == 2:
                        game_state = "INTERMISSION"
                elif eaten_pellets == lvl2MinEaten and chosen_lvl == 2:
                    level = generate_level()
                    eaten_pellets = 0
                    frightened_mode = False
                    player_lives += 1
                    pickup_for_level = False
                    completed_lvls += 1
                    restart_game()
                    if completed_lvls == 2:
                        game_state = "INTERMISSION"

            current_time = pygame.time.get_ticks()        

            # Keeps track of time passed and flips power_pellet_flipper to create a "blinking" effect for power pellets
            # Occurs once every 200 milliseconds
            if current_time - last_pellet_blink > POWER_PELLET_BLINK_INTERVAL:
                power_pellet_flipper = not power_pellet_flipper
                last_pellet_blink = current_time

            # Keeps track of time passed and flips flashing_frightened_flipper to create a "flashing" effect for ghosts
            # Occurs once every 300 milliseconds
            if current_time - last_ghost_flash > FRIGHTENED_FLASH_INTERVAL:
                flashing_frightened_flipper = not flashing_frightened_flipper
                last_ghost_flash = current_time

            if not pacman_dying:

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
            score = score_font.render("1UP: " + str(player_score), True, WHITE)

            # Draw Pac-Man lives near bottom of screen
            for life in range(player_lives):
            
                # Pacman center:
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

            # --- Ghost mode timer ---
            dt = clock.get_time() / 1000.0  # convert ms → seconds

            if frightened_mode:
                frightened_timer += dt

                check_center_tile()

                # Check for ghost collision when in frightened mode
                if is_ghost_collision(player_x, player_y, red_ghost_x, red_ghost_y) and rg_eyes == False:
                    eat_ghost("red")
                elif is_ghost_collision(player_x, player_y, blue_ghost_x, blue_ghost_y) and bg_eyes == False:
                    eat_ghost("blue")   
                elif is_ghost_collision(player_x, player_y, pink_ghost_x, pink_ghost_y) and pg_eyes == False:
                    eat_ghost("pink")
                elif is_ghost_collision(player_x, player_y, orange_ghost_x, orange_ghost_y) and og_eyes == False:
                    eat_ghost("orange")

                if ghost_eaten:
                    ghost_eaten_timer += dt
                    player_speed = 0
                    r_ghost_speed = 0
                    b_ghost_speed = 0
                    p_ghost_speed = 0
                    o_ghost_speed = 0

                    # Draw black circles covering Pac-Man + ghost
                    pygame.draw.circle(screen, BLACK, (player_x, player_y), player_radius)

                    EATEN_SCORE = g_eat_font.render(str(ghost_eat_score), True, CYAN)
                    if ghost_eaten_color == "red":
                        pygame.draw.circle(screen, BLACK, (red_ghost_x, red_ghost_y), player_radius)
                        # Eaten score
                        eaten_score_rect = EATEN_SCORE.get_rect(center=(red_ghost_x, red_ghost_y))
                        screen.blit(EATEN_SCORE, eaten_score_rect)
                        rg_eyes = True

                        # Draw Ghosts
                        frame = scared_ghost[ghost_frame_index]

                        draw_x = blue_ghost_x - frame.get_width()/2
                        draw_y = blue_ghost_y - frame.get_height()/2
                        if bg_eyes:
                            if blue_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif blue_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif blue_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif blue_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = pink_ghost_x - frame.get_width()/2
                        draw_y = pink_ghost_y - frame.get_height()/2
                        if pg_eyes:
                            if pink_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif pink_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif pink_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif pink_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = orange_ghost_x - frame.get_width()/2 
                        draw_y = orange_ghost_y - frame.get_height()/2
                        if og_eyes:
                            if orange_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif orange_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif orange_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif orange_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))


                    elif ghost_eaten_color == "blue":
                        pygame.draw.circle(screen, BLACK, (blue_ghost_x, blue_ghost_y), player_radius)
                        # Eaten score      
                        eaten_score_rect = EATEN_SCORE.get_rect(center=(blue_ghost_x, blue_ghost_y))
                        screen.blit(EATEN_SCORE, eaten_score_rect)
                        bg_eyes = True

                        # Draw Ghosts
                        frame = scared_ghost[ghost_frame_index]
                
                        draw_x = red_ghost_x - frame.get_width()/2
                        draw_y = red_ghost_y - frame.get_height()/2
                        if rg_eyes:
                            if red_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif red_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif red_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif red_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
                    
                        draw_x = pink_ghost_x - frame.get_width()/2
                        draw_y = pink_ghost_y - frame.get_height()/2
                        if pg_eyes:
                            if pink_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif pink_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif pink_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif pink_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = orange_ghost_x - frame.get_width()/2
                        draw_y = orange_ghost_y - frame.get_height()/2
                        if og_eyes:
                            if orange_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif orange_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif orange_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif orange_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))

                    elif ghost_eaten_color == "pink":
                        pygame.draw.circle(screen, BLACK, (pink_ghost_x, pink_ghost_y), player_radius)
                        # Eaten score      
                        eaten_score_rect = EATEN_SCORE.get_rect(center=(pink_ghost_x, pink_ghost_y))
                        screen.blit(EATEN_SCORE, eaten_score_rect)
                        pg_eyes = True

                        # Draw Ghosts
                        frame = scared_ghost[ghost_frame_index]
                
                        draw_x = blue_ghost_x - frame.get_width()/2
                        draw_y = blue_ghost_y - frame.get_height()/2
                        if bg_eyes:
                            if blue_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif blue_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif blue_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif blue_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
                    
                        draw_x = red_ghost_x - frame.get_width()/2
                        draw_y = red_ghost_y - frame.get_height()/2
                        if rg_eyes:
                            if red_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif red_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif red_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif red_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = orange_ghost_x - frame.get_width()/2
                        draw_y = orange_ghost_y - frame.get_height()/2
                        if og_eyes:
                            if orange_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif orange_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif orange_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif orange_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))

                    elif ghost_eaten_color == "orange":
                        pygame.draw.circle(screen, BLACK, (orange_ghost_x, orange_ghost_y), player_radius)
                        # Eaten score      
                        eaten_score_rect = EATEN_SCORE.get_rect(center=(orange_ghost_x, orange_ghost_y))
                        screen.blit(EATEN_SCORE, eaten_score_rect)
                        og_eyes = True

                        # Draw Ghosts
                        frame = scared_ghost[ghost_frame_index]
                
                        draw_x = blue_ghost_x - frame.get_width()/2
                        draw_y = blue_ghost_y - frame.get_height()/2
                        if bg_eyes:
                            if blue_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif blue_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif blue_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif blue_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
                    
                        draw_x = pink_ghost_x - frame.get_width()/2
                        draw_y = pink_ghost_y - frame.get_height()/2
                        if pg_eyes:
                            if pink_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif pink_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif pink_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif pink_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = red_ghost_x - frame.get_width()/2
                        draw_y = red_ghost_y - frame.get_height()/2
                        if rg_eyes:
                            if red_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x, draw_y))
                            elif red_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x, draw_y))
                            elif red_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x, draw_y))
                            elif red_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x, draw_y))
                        else:
                            screen.blit(frame, (draw_x, draw_y))

                    # After pause ends
                    if ghost_eaten_timer >= ghost_eaten_duration:
                        ghost_eaten = False
                        player_speed = 2
                        r_ghost_speed = 1
                        b_ghost_speed = 1
                        p_ghost_speed = 1
                        o_ghost_speed = 1
                        ghost_eat_score *= 2
            
                else:            

                    # --- Red Ghost Movement ---
                    if is_ghost_centered(red_ghost_x) and is_ghost_centered(red_ghost_y):
                        # SNAP to center so rounding errors don't build up
                        red_ghost_x, red_ghost_y = snap_ghost_to_center(red_ghost_x, red_ghost_y)
                
                        target = target_frightened(red_ghost_x, red_ghost_y, rg_eyes)
                        red_direction = choose_ghost_direction(red_ghost_x, red_ghost_y, red_direction, target)
        
                    # Move ghost by direction
                    if red_direction == "up":
                        red_ghost_y -= r_ghost_speed
                    elif red_direction == "down":
                        red_ghost_y += r_ghost_speed
                    elif red_direction == "left":
                        red_ghost_x -= r_ghost_speed
                    elif red_direction == "right":
                        red_ghost_x += r_ghost_speed  
                
                
                    # After moving, if ghost is now very close to the target tile center, snap to exact center
                    if is_ghost_centered(red_ghost_x) and is_ghost_centered(red_ghost_y):
                        red_ghost_x, red_ghost_y = snap_ghost_to_center(red_ghost_x, red_ghost_y)

                    # --- Blue Ghost Movement ---
                    if is_ghost_centered(blue_ghost_x) and is_ghost_centered(blue_ghost_y):
                        # SNAP to center so rounding errors don't build up
                        blue_ghost_x, blue_ghost_y = snap_ghost_to_center(blue_ghost_x, blue_ghost_y)
                
                        target = target_frightened(blue_ghost_x, blue_ghost_y, bg_eyes)
                        blue_direction = choose_ghost_direction(blue_ghost_x, blue_ghost_y, blue_direction, target)
                
                    # Move ghost by direction
                    if blue_direction == "up":
                        blue_ghost_y -= b_ghost_speed
                    elif blue_direction == "down":
                        blue_ghost_y += b_ghost_speed
                    elif blue_direction == "left":
                        blue_ghost_x -= b_ghost_speed
                    elif blue_direction == "right":
                        blue_ghost_x += b_ghost_speed  
                
                
                    # After moving, if ghost is now very close to the target tile center, snap to exact center
                    if is_ghost_centered(blue_ghost_x) and is_ghost_centered(blue_ghost_y):
                        blue_ghost_x, blue_ghost_y = snap_ghost_to_center(blue_ghost_x, blue_ghost_y)

                    # --- Pink Ghost Movement ---
                    if is_ghost_centered(pink_ghost_x) and is_ghost_centered(pink_ghost_y):
                        # SNAP to center so rounding errors don't build up
                        pink_ghost_x, pink_ghost_y = snap_ghost_to_center(pink_ghost_x, pink_ghost_y)
                
                        target = target_frightened(pink_ghost_x, pink_ghost_y, pg_eyes)
                        pink_direction = choose_ghost_direction(pink_ghost_x, pink_ghost_y, pink_direction, target)
                
                    # Move ghost by direction
                    if pink_direction == "up":
                        pink_ghost_y -= p_ghost_speed
                    elif pink_direction == "down":
                        pink_ghost_y += p_ghost_speed
                    elif pink_direction == "left":
                        pink_ghost_x -= p_ghost_speed
                    elif pink_direction == "right":
                        pink_ghost_x += p_ghost_speed  
                
                
                    # After moving, if ghost is now very close to the target tile center, snap to exact center
                    if is_ghost_centered(pink_ghost_x) and is_ghost_centered(pink_ghost_y):
                        pink_ghost_x, pink_ghost_y = snap_ghost_to_center(pink_ghost_x, pink_ghost_y)

                    # --- Orange Ghost Movement ---
                    if is_ghost_centered(orange_ghost_x) and is_ghost_centered(orange_ghost_y):
                        # SNAP to center so rounding errors don't build up
                        orange_ghost_x, orange_ghost_y = snap_ghost_to_center(orange_ghost_x, orange_ghost_y)
                
                        target = target_frightened(orange_ghost_x, orange_ghost_y, og_eyes)
                        orange_direction = choose_ghost_direction(orange_ghost_x, orange_ghost_y, orange_direction, target)
                
                    # Move ghost by direction
                    if orange_direction == "up":
                        orange_ghost_y -= o_ghost_speed
                    elif orange_direction == "down":
                        orange_ghost_y += o_ghost_speed
                    elif orange_direction == "left":
                        orange_ghost_x -= o_ghost_speed
                    elif orange_direction == "right":
                        orange_ghost_x += o_ghost_speed  
                
                
                    # After moving, if ghost is now very close to the target tile center, snap to exact center
                    if is_ghost_centered(orange_ghost_x) and is_ghost_centered(orange_ghost_y):
                        orange_ghost_x, orange_ghost_y = snap_ghost_to_center(orange_ghost_x, orange_ghost_y)            

                    if frightened_timer < 4:
                        # Draws normal frightened mode unless in eyes mode
                        frame = scared_ghost[ghost_frame_index]
                        draw_x = red_ghost_x - frame.get_width()/2
                        draw_y = red_ghost_y - frame.get_height()/2
                        if rg_eyes:
                            if red_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif red_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif red_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif red_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = blue_ghost_x - frame.get_width()/2
                        draw_y = blue_ghost_y - frame.get_height()/2
                        if bg_eyes:
                            if blue_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif blue_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif blue_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif blue_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = pink_ghost_x - frame.get_width()/2
                        draw_y = pink_ghost_y - frame.get_height()/2
                        if pg_eyes:
                            if pink_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif pink_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif pink_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif pink_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = orange_ghost_x - frame.get_width()/2 
                        draw_y = orange_ghost_y - frame.get_height()/2
                        if og_eyes:
                            if orange_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif orange_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif orange_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif orange_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))

                    elif frightened_timer >= 4 and flashing_frightened_flipper:
                        # Draws white ghost unless in eyes mode
                        frame = white_scared_ghost[ghost_frame_index]
                        draw_x = red_ghost_x - frame.get_width()/2
                        draw_y = red_ghost_y - frame.get_height()/2
                        if rg_eyes:
                            if red_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif red_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif red_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif red_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = blue_ghost_x - frame.get_width()/2
                        draw_y = blue_ghost_y - frame.get_height()/2
                        if bg_eyes:
                            if blue_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif blue_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif blue_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif blue_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
                
                        draw_x = pink_ghost_x - frame.get_width()/2
                        draw_y = pink_ghost_y - frame.get_height()/2
                        if pg_eyes:
                            if pink_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif pink_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif pink_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif pink_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = orange_ghost_x - frame.get_width()/2
                        draw_y = orange_ghost_y - frame.get_height()/2
                        if og_eyes:
                            if orange_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif orange_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif orange_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif orange_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
                    elif frightened_timer >= 4 and not flashing_frightened_flipper:
                        # Draws blue ghost unless in eyes mode
                        frame = scared_ghost[ghost_frame_index]
                        draw_x = red_ghost_x - frame.get_width()/2
                        draw_y = red_ghost_y - frame.get_height()/2
                        if rg_eyes:
                            if red_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif red_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif red_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif red_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = blue_ghost_x - frame.get_width()/2
                        draw_y = blue_ghost_y - frame.get_height()/2
                        if bg_eyes:
                            if blue_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif blue_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif blue_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif blue_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = pink_ghost_x - frame.get_width()/2
                        draw_y = pink_ghost_y - frame.get_height()/2
                        if pg_eyes:
                            if pink_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif pink_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif pink_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif pink_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))
            
                        draw_x = orange_ghost_x - frame.get_width()/2
                        draw_y = orange_ghost_y - frame.get_height()/2
                        if og_eyes:
                            if orange_direction == "up":
                                screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                            elif orange_direction == "down":
                                screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                            elif orange_direction == "left":
                                screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                            elif orange_direction == "right":
                                screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                        else:
                            screen.blit(frame, (draw_x, draw_y))

                    if frightened_timer >= FRIGHTENED_DURATION:
                        frightened_mode = False
                        frightened_timer = 0.0
                        # resume normal scatter/chase mode
                        ghost_mode_timer = 0

            else:

            
                # Check for ghost collision when not in frightened mode
                if is_ghost_collision(player_x, player_y, red_ghost_x, red_ghost_y) and not rg_eyes:
                    pacman_dying = True
                elif is_ghost_collision(player_x, player_y, blue_ghost_x, blue_ghost_y) and not bg_eyes:
                    pacman_dying = True
                elif is_ghost_collision(player_x, player_y, pink_ghost_x, pink_ghost_y) and not pg_eyes:
                    pacman_dying = True
                elif is_ghost_collision(player_x, player_y, orange_ghost_x, orange_ghost_y) and not og_eyes:
                    pacman_dying = True

                if pacman_dying:

                    player_speed = 0
                    r_ghost_speed = 0
                    b_ghost_speed = 0
                    p_ghost_speed = 0
                    o_ghost_speed = 0

                    # Freeze ghosts + player movement

                    # --- Initialize animation state once ---
                    if "death_started" not in globals():
                        death_started = True
                        death_timer = 0.0
                        death_frame = 0
                        DEATH_ANIM_SPEED = 0.12  # seconds per frame

                    # Draw halted positions
                    if death_timer < 1.0:
                        r_ghost_frames = red_ghost_sprites[red_direction]
                        frame = r_ghost_frames[ghost_frame_index]
                        draw_x = red_ghost_x - frame.get_width()/2
                        draw_y = red_ghost_y - frame.get_height()/2
                        screen.blit(frame, (draw_x, draw_y))

                        b_ghost_frames = blue_ghost_sprites[blue_direction]
                        frame = b_ghost_frames[ghost_frame_index]
                        draw_x = blue_ghost_x - frame.get_width()/2 
                        draw_y = blue_ghost_y - frame.get_height()/2
                        screen.blit(frame, (draw_x, draw_y))

                        p_ghost_frames = pink_ghost_sprites[pink_direction]
                        frame = p_ghost_frames[ghost_frame_index]
                        draw_x = pink_ghost_x - frame.get_width()/2 
                        draw_y = pink_ghost_y - frame.get_height()/2
                        screen.blit(frame, (draw_x, draw_y))

                        o_ghost_frames = orange_ghost_sprites[orange_direction]
                        frame = o_ghost_frames[ghost_frame_index]
                        draw_x = orange_ghost_x - frame.get_width()/2 
                        draw_y = orange_ghost_y - frame.get_height()/2
                        screen.blit(frame, (draw_x, draw_y))

                    # ---- Animation window ----
                    elif death_timer >= 1.0 and death_timer < 4.0:

                        if not death_sound_once:
                            pacman_fail.play()
                            death_sound_once = True

                        # Draw black circle covering Pac-Man
                        pygame.draw.circle(screen, BLACK, (player_x, player_y), player_radius)

                        # ---- Play death animation frames ----
                        # start animation time AFTER the 1 second freeze
                        anim_time = death_timer - 1.0
                        death_frame = int(anim_time / DEATH_ANIM_SPEED)

                        if death_frame < len(pacman_death_frames):
                            frame = pacman_death_frames[death_frame]
                            frame_rect = frame.get_rect(center=(player_x - TILE_SIZE//6+5, player_y - TILE_SIZE//6+5))
                            screen.blit(frame, frame_rect)
                            pygame.display.flip()
                    death_timer += dt

                    if death_timer < 4.0 and death_timer >= 3.0 and player_lives <= 0:
                        if chosen_lvl == 1:
                            GAME_OVER_TXT = render_stretched_text("GAME      OVER", (255, 0, 0), ready_font, scale_x=1.5)
                            offset = TILE_SIZE * 5
                            row, col = get_pixel_pos(13,10)
                            game_over_rect = GAME_OVER_TXT.get_rect(center=(col + TILE_SIZE // 2, row + offset))
                            screen.blit(GAME_OVER_TXT, game_over_rect)
                        elif chosen_lvl == 2:
                            GAME_OVER_TXT = render_stretched_text("GAME      OVER", (255, 0, 0), ready_font, scale_x=1.5)
                            offset = TILE_SIZE * 6
                            row, col = get_pixel_pos(13,10)
                            game_over_rect = GAME_OVER_TXT.get_rect(center=(col + TILE_SIZE // 2, row + offset))
                            screen.blit(GAME_OVER_TXT, game_over_rect)

                    if death_timer >= 4.0:
                        # ---- Animation finished: clean up & restart game ----
                        del death_started
                        pacman_dying = False
                        death_sound_once = False
                        if player_lives <= 0:
                            game_state = "START_SCREEN"
                            reset_game_vars()
                        else:
                            restart_game()

                else:

                    ghost_mode_timer += dt
            
                    # Reset ghost_eat_score back to 200
                    ghost_eat_score = 200

                    # Check if a ghost is at the center tile
                    check_center_tile()

                    # Get current mode + duration
                    ghost_mode, duration = MODE_CYCLE[ghost_mode_index]

                    # Check for mode switch
                    if ghost_mode_timer >= duration:
                        ghost_mode_timer = 0

                        # Advance to next mode
                        ghost_mode_index += 1

                        # Loop back to 0 if we reached the end
                        if ghost_mode_index >= len(MODE_CYCLE):
                            ghost_mode_index = 0
                
                        # Update active mode
                        ghost_mode, _ = MODE_CYCLE[ghost_mode_index]


                    # --- Red Ghost Movement ---
                    if is_ghost_centered(red_ghost_x) and is_ghost_centered(red_ghost_y):
                        # SNAP to center so rounding errors don't build up
                        red_ghost_x, red_ghost_y = snap_ghost_to_center(red_ghost_x, red_ghost_y)

                        target = get_red_target(rg_eyes)
                        red_direction = choose_ghost_direction(red_ghost_x, red_ghost_y, red_direction, target)

                    # Move ghost by direction
                    if red_direction == "up":
                        red_ghost_y -= r_ghost_speed
                    elif red_direction == "down":
                        red_ghost_y += r_ghost_speed
                    elif red_direction == "left":
                        red_ghost_x -= r_ghost_speed
                    elif red_direction == "right":
                        red_ghost_x += r_ghost_speed


                    # After moving, if ghost is now very close to the target tile center, snap to exact center
                    if is_ghost_centered(red_ghost_x) and is_ghost_centered(red_ghost_y):
                        red_ghost_x, red_ghost_y = snap_ghost_to_center(red_ghost_x, red_ghost_y)

                    # --- Pink Ghost Movement ---
                    if is_ghost_centered(pink_ghost_x) and is_ghost_centered(pink_ghost_y):
                        # SNAP to center so rounding errors don't build up
                        pink_ghost_x, pink_ghost_y = snap_ghost_to_center(pink_ghost_x, pink_ghost_y)
            
                        target = get_pink_target(pg_eyes)
                        pink_direction = choose_ghost_direction(pink_ghost_x, pink_ghost_y, pink_direction, target)
        
                    # Move ghost by direction 
                    if pink_direction == "up":
                        pink_ghost_y -= p_ghost_speed
                    elif pink_direction == "down":
                        pink_ghost_y += p_ghost_speed
                    elif pink_direction == "left":
                        pink_ghost_x -= p_ghost_speed
                    elif pink_direction == "right":
                        pink_ghost_x += p_ghost_speed  
            
    
                    # After moving, if ghost is now very close to the target tile center, snap to exact center
                    if is_ghost_centered(pink_ghost_x) and is_ghost_centered(pink_ghost_y):
                        pink_ghost_x, pink_ghost_y = snap_ghost_to_center(pink_ghost_x, pink_ghost_y)

                    # --- Blue Ghost Movement ---
                    if is_ghost_centered(blue_ghost_x) and is_ghost_centered(blue_ghost_y):
                        # SNAP to center so rounding errors don't build up
                        blue_ghost_x, blue_ghost_y = snap_ghost_to_center(blue_ghost_x, blue_ghost_y)
        
                        target = get_blue_target(red_ghost_x, red_ghost_y, bg_eyes)
                        blue_direction = choose_ghost_direction(blue_ghost_x, blue_ghost_y, blue_direction, target)
        
                    # Move ghost by direction
                    if blue_direction == "up":
                        blue_ghost_y -= b_ghost_speed
                    elif blue_direction == "down":
                        blue_ghost_y += b_ghost_speed
                    elif blue_direction == "left":
                        blue_ghost_x -= b_ghost_speed
                    elif blue_direction == "right":
                        blue_ghost_x += b_ghost_speed
        
        
                    # After moving, if ghost is now very close to the target tile center, snap to exact center
                    if is_ghost_centered(blue_ghost_x) and is_ghost_centered(blue_ghost_y):
                        blue_ghost_x, blue_ghost_y = snap_ghost_to_center(blue_ghost_x, blue_ghost_y)


                    # --- Orange Ghost Movement ---
                    if is_ghost_centered(orange_ghost_x) and is_ghost_centered(orange_ghost_y):
                        # SNAP to center so rounding errors don't build up
                        orange_ghost_x, orange_ghost_y = snap_ghost_to_center(orange_ghost_x, orange_ghost_y)
        
                        target = get_orange_target(orange_ghost_x, orange_ghost_y, og_eyes)
                        orange_direction = choose_ghost_direction(orange_ghost_x, orange_ghost_y, orange_direction, target)
        
                    # Move ghost by direction
                    if orange_direction == "up":
                        orange_ghost_y -= o_ghost_speed
                    elif orange_direction == "down":
                        orange_ghost_y += o_ghost_speed
                    elif orange_direction == "left":
                        orange_ghost_x -= o_ghost_speed
                    elif orange_direction == "right":
                        orange_ghost_x += o_ghost_speed
            
            
                    # After moving, if ghost is now very close to the target tile center, snap to exact center
                    if is_ghost_centered(orange_ghost_x) and is_ghost_centered(orange_ghost_y):
                        orange_ghost_x, orange_ghost_y = snap_ghost_to_center(orange_ghost_x, orange_ghost_y)

                    # Draw normally unless in eyes mode
                    # --- Draw red ghost ---
                    r_ghost_frames = red_ghost_sprites[red_direction]
                    frame = r_ghost_frames[ghost_frame_index]
                    draw_x = red_ghost_x - frame.get_width()/2
                    draw_y = red_ghost_y - frame.get_height()/2
                    if rg_eyes:
                        if red_direction == "up":
                            screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                        elif red_direction == "down":
                            screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                        elif red_direction == "left":
                            screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                        elif red_direction == "right":
                            screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                    else:
                        screen.blit(frame, (draw_x, draw_y))
                
                    # --- Draw blue ghost ---
                    b_ghost_frames = blue_ghost_sprites[blue_direction]   
                    frame = b_ghost_frames[ghost_frame_index]
                    draw_x = blue_ghost_x - frame.get_width()/2
                    draw_y = blue_ghost_y - frame.get_height()/2
                    if bg_eyes:
                        if blue_direction == "up":
                            screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                        elif blue_direction == "down":
                            screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                        elif blue_direction == "left":
                            screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                        elif blue_direction == "right":
                            screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                    else:
                        screen.blit(frame, (draw_x, draw_y))
                
                    # --- Draw pink ghost ---
                    p_ghost_frames = pink_ghost_sprites[pink_direction]
                    frame = p_ghost_frames[ghost_frame_index]
                    draw_x = pink_ghost_x - frame.get_width()/2
                    draw_y = pink_ghost_y - frame.get_height()/2
                    if pg_eyes:
                        if pink_direction == "up":
                            screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                        elif pink_direction == "down":
                            screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                        elif pink_direction == "left":
                            screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                        elif pink_direction == "right":
                            screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                    else:
                        screen.blit(frame, (draw_x, draw_y))
                
                    # --- Draw Orange ghost ---
                    o_ghost_frames = orange_ghost_sprites[orange_direction]
                    frame = o_ghost_frames[ghost_frame_index]
                    draw_x = orange_ghost_x - frame.get_width()/2
                    draw_y = orange_ghost_y - frame.get_height()/2
                    if og_eyes:
                        if orange_direction == "up":
                            screen.blit(ghost_eyes_up, (draw_x+5, draw_y+5))
                        elif orange_direction == "down":
                            screen.blit(ghost_eyes_down, (draw_x+5, draw_y+5))
                        elif orange_direction == "left":
                            screen.blit(ghost_eyes_left, (draw_x+5, draw_y+5))
                        elif orange_direction == "right":
                            screen.blit(ghost_eyes_right, (draw_x+5, draw_y+5))
                    else:
                        screen.blit(frame, (draw_x, draw_y))

            # --- Update ghost animations ---
            ghost_frame_tick += 1
            if ghost_frame_tick >= GHOST_FRAME_DELAY:
                ghost_frame_tick = 0
                ghost_frame_index = (ghost_frame_index + 1) % 2

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
