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

# Checks if the current tile pacman is on is a pellet or not, sets tile to 2, adds to score, and removes 
# pellet if so. Does nothing if not.
def is_current_tile_pellet():
    global player_x, player_y, player_score, waka_flip, eaten_pellets, red_direction, pink_direction, blue_direction, orange_direction, frightened_mode, frightened_timer
    grid_row, grid_col = get_grid_pos(player_x, player_y)

    # Checks if base pellet
    if level[grid_row][grid_col] == 0:
        player_score += 10
        eaten_pellets += 1
        level[grid_row][grid_col] = 2
        waka_sound.play()
        return True
    # Checks if power pellet
    elif level[grid_row][grid_col] == 4:
        player_score += 50
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

# movement speed
ghost_speed = 1.0

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
orange_direction = 'up'

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
def get_red_target():
    global player_x, player_y
    if ghost_mode == "chase":
        pac_r, pac_c = get_grid_pos(player_x, player_y)
        return (pac_r, pac_c)
    elif ghost_mode == "scatter":
        return (0, COLS-1)

# Gets Pinky's target tile
def get_pink_target():
    global current_direction, player_x, player_y
    pac_r, pac_c = get_grid_pos(player_x, player_y)

    # Pac-Man's facing direction
    d = current_direction  # "up", "down", "left", "right"

    if ghost_mode == "chase":
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
        return (0, 0)

# Gets Inky's target tile
def get_blue_target(blinky_x, blinky_y):
    global current_direction, player_x, player_y
    if ghost_mode == "chase":
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
        return(ROWS-1, COLS-1)


def get_orange_target(clyde_x, clyde_y):
    global player_x, player_y
    pac_r, pac_c = get_grid_pos(player_x, player_y)
    cy_r, cy_c = get_grid_pos(clyde_x, clyde_y)

    dist_sq = (pac_r - cy_r)**2 + (pac_c - cy_c)**2

    if dist_sq >= 64:  # 8 tiles squared
        return (pac_r, pac_c)  # chase
    else:
        return (ROWS-1, 0)     # scatter corner

def target_frightened(ghost_x, ghost_y):
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
    # If not in "Game Intro" state, run the following
    else:
  
        if frightened_mode:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("sounds/frightenedMode.mp3")
                pygame.mixer.music.play()
        else:
            # Plays ghost siren only once so it does not keep playing
            if player_score < 800:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load("sounds/ghost_siren1.mp3")
                    pygame.mixer.music.play()
            elif eaten_pellets >= 50 and eaten_pellets < 100:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load("sounds/ghost_siren2.mp3")
                    pygame.mixer.music.play()
            elif eaten_pellets >= 100 and eaten_pellets < 150:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load("sounds/ghost_siren3.mp3")
                    pygame.mixer.music.play()
            elif eaten_pellets >= 150 and eaten_pellets < 200:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load("sounds/ghost_siren4.mp3")
                    pygame.mixer.music.play()
            elif eaten_pellets >= 200 and eaten_pellets < 235:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load("sounds/ghost_siren5.mp3")
                    pygame.mixer.music.play()

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

        # --- Ghost mode timer ---
        dt = clock.get_time() / 1000.0  # convert ms → seconds

        if frightened_mode:
            frightened_timer += dt
            
            # --- Red Ghost Movement ---
            if is_ghost_centered(red_ghost_x) and is_ghost_centered(red_ghost_y):
                # SNAP to center so rounding errors don't build up
                red_ghost_x, red_ghost_y = snap_ghost_to_center(red_ghost_x, red_ghost_y)
                
                target = target_frightened(red_ghost_x, red_ghost_y)
                red_direction = choose_ghost_direction(red_ghost_x, red_ghost_y, red_direction, target)
                
            # Move ghost by direction
            if red_direction == "up":
                red_ghost_y -= ghost_speed
            elif red_direction == "down":
                red_ghost_y += ghost_speed
            elif red_direction == "left":
                red_ghost_x -= ghost_speed
            elif red_direction == "right":
                red_ghost_x += ghost_speed  
                
                
            # After moving, if ghost is now very close to the target tile center, snap to exact center
            if is_ghost_centered(red_ghost_x) and is_ghost_centered(red_ghost_y):
                red_ghost_x, red_ghost_y = snap_ghost_to_center(red_ghost_x, red_ghost_y)

            # --- Blue Ghost Movement ---
            if is_ghost_centered(blue_ghost_x) and is_ghost_centered(blue_ghost_y):
                # SNAP to center so rounding errors don't build up
                blue_ghost_x, blue_ghost_y = snap_ghost_to_center(blue_ghost_x, blue_ghost_y)
                
                target = target_frightened(blue_ghost_x, blue_ghost_y)
                blue_direction = choose_ghost_direction(blue_ghost_x, blue_ghost_y, blue_direction, target)
                
            # Move ghost by direction
            if blue_direction == "up":
                blue_ghost_y -= ghost_speed
            elif blue_direction == "down":
                blue_ghost_y += ghost_speed
            elif blue_direction == "left":
                blue_ghost_x -= ghost_speed
            elif blue_direction == "right":
                blue_ghost_x += ghost_speed  
                
                
            # After moving, if ghost is now very close to the target tile center, snap to exact center
            if is_ghost_centered(blue_ghost_x) and is_ghost_centered(blue_ghost_y):
                blue_ghost_x, blue_ghost_y = snap_ghost_to_center(blue_ghost_x, blue_ghost_y)

            # --- Pink Ghost Movement ---
            if is_ghost_centered(pink_ghost_x) and is_ghost_centered(pink_ghost_y):
                # SNAP to center so rounding errors don't build up
                pink_ghost_x, pink_ghost_y = snap_ghost_to_center(pink_ghost_x, pink_ghost_y)
                
                target = target_frightened(pink_ghost_x, pink_ghost_y)
                pink_direction = choose_ghost_direction(pink_ghost_x, pink_ghost_y, pink_direction, target)
                
            # Move ghost by direction
            if pink_direction == "up":
                pink_ghost_y -= ghost_speed
            elif pink_direction == "down":
                pink_ghost_y += ghost_speed
            elif pink_direction == "left":
                pink_ghost_x -= ghost_speed
            elif pink_direction == "right":
                pink_ghost_x += ghost_speed  
                
                
            # After moving, if ghost is now very close to the target tile center, snap to exact center
            if is_ghost_centered(pink_ghost_x) and is_ghost_centered(pink_ghost_y):
                pink_ghost_x, pink_ghost_y = snap_ghost_to_center(pink_ghost_x, pink_ghost_y)

            # --- Orange Ghost Movement ---
            if is_ghost_centered(orange_ghost_x) and is_ghost_centered(orange_ghost_y):
                # SNAP to center so rounding errors don't build up
                orange_ghost_x, orange_ghost_y = snap_ghost_to_center(orange_ghost_x, orange_ghost_y)
                
                target = target_frightened(orange_ghost_x, orange_ghost_y)
                orange_direction = choose_ghost_direction(orange_ghost_x, orange_ghost_y, orange_direction, target)
                
            # Move ghost by direction
            if orange_direction == "up":
                orange_ghost_y -= ghost_speed
            elif orange_direction == "down":
                orange_ghost_y += ghost_speed
            elif orange_direction == "left":
                orange_ghost_x -= ghost_speed
            elif orange_direction == "right":
                orange_ghost_x += ghost_speed  
                
                
            # After moving, if ghost is now very close to the target tile center, snap to exact center
            if is_ghost_centered(orange_ghost_x) and is_ghost_centered(orange_ghost_y):
                orange_ghost_x, orange_ghost_y = snap_ghost_to_center(orange_ghost_x, orange_ghost_y)            

            if frightened_timer < 4:
                # Draws normal frightened mode
                frame = scared_ghost[ghost_frame_index]
                draw_x = red_ghost_x - frame.get_width()/2
                draw_y = red_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            
                draw_x = blue_ghost_x - frame.get_width()/2
                draw_y = blue_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            
                draw_x = pink_ghost_x - frame.get_width()/2
                draw_y = pink_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            
                draw_x = orange_ghost_x - frame.get_width()/2 
                draw_y = orange_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            elif frightened_timer >= 4 and flashing_frightened_flipper:
                # Draws white ghost
                frame = white_scared_ghost[ghost_frame_index]
                draw_x = red_ghost_x - frame.get_width()/2
                draw_y = red_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            
                draw_x = blue_ghost_x - frame.get_width()/2
                draw_y = blue_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
                
                draw_x = pink_ghost_x - frame.get_width()/2
                draw_y = pink_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            
                draw_x = orange_ghost_x - frame.get_width()/2
                draw_y = orange_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            elif frightened_timer >= 4 and not flashing_frightened_flipper:
                # Draws blue ghost    
                frame = scared_ghost[ghost_frame_index]
                draw_x = red_ghost_x - frame.get_width()/2
                draw_y = red_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            
                draw_x = blue_ghost_x - frame.get_width()/2
                draw_y = blue_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            
                draw_x = pink_ghost_x - frame.get_width()/2
                draw_y = pink_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))
            
                draw_x = orange_ghost_x - frame.get_width()/2
                draw_y = orange_ghost_y - frame.get_height()/2
                screen.blit(frame, (draw_x, draw_y))


            if frightened_timer >= FRIGHTENED_DURATION:
                frightened_mode = False
                frightened_timer = 0.0
                # resume normal scatter/chase mode
                ghost_mode_timer = 0
        else:

            ghost_mode_timer += dt

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

                target = get_red_target()
                red_direction = choose_ghost_direction(red_ghost_x, red_ghost_y, red_direction, target)

            # Move ghost by direction
            if red_direction == "up":
                red_ghost_y -= ghost_speed
            elif red_direction == "down":
                red_ghost_y += ghost_speed
            elif red_direction == "left":
                red_ghost_x -= ghost_speed
            elif red_direction == "right":
                red_ghost_x += ghost_speed


            # After moving, if ghost is now very close to the target tile center, snap to exact center
            if is_ghost_centered(red_ghost_x) and is_ghost_centered(red_ghost_y):
                red_ghost_x, red_ghost_y = snap_ghost_to_center(red_ghost_x, red_ghost_y)

            # --- Pink Ghost Movement ---
            if is_ghost_centered(pink_ghost_x) and is_ghost_centered(pink_ghost_y):
                # SNAP to center so rounding errors don't build up
                pink_ghost_x, pink_ghost_y = snap_ghost_to_center(pink_ghost_x, pink_ghost_y)
            
                target = get_pink_target()
                pink_direction = choose_ghost_direction(pink_ghost_x, pink_ghost_y, pink_direction, target)
        
            # Move ghost by direction 
            if pink_direction == "up":
                pink_ghost_y -= ghost_speed
            elif pink_direction == "down":
                pink_ghost_y += ghost_speed
            elif pink_direction == "left":
                pink_ghost_x -= ghost_speed
            elif pink_direction == "right":
                pink_ghost_x += ghost_speed  
            
    
            # After moving, if ghost is now very close to the target tile center, snap to exact center
            if is_ghost_centered(pink_ghost_x) and is_ghost_centered(pink_ghost_y):
                pink_ghost_x, pink_ghost_y = snap_ghost_to_center(pink_ghost_x, pink_ghost_y)

            # --- Blue Ghost Movement ---
            if is_ghost_centered(blue_ghost_x) and is_ghost_centered(blue_ghost_y):
                # SNAP to center so rounding errors don't build up
                blue_ghost_x, blue_ghost_y = snap_ghost_to_center(blue_ghost_x, blue_ghost_y)
        
                target = get_blue_target(red_ghost_x, red_ghost_y)
                blue_direction = choose_ghost_direction(blue_ghost_x, blue_ghost_y, blue_direction, target)
        
            # Move ghost by direction
            if blue_direction == "up":
                blue_ghost_y -= ghost_speed
            elif blue_direction == "down":
                blue_ghost_y += ghost_speed
            elif blue_direction == "left":
                blue_ghost_x -= ghost_speed
            elif blue_direction == "right":
                blue_ghost_x += ghost_speed
        
        
            # After moving, if ghost is now very close to the target tile center, snap to exact center
            if is_ghost_centered(blue_ghost_x) and is_ghost_centered(blue_ghost_y):
                blue_ghost_x, blue_ghost_y = snap_ghost_to_center(blue_ghost_x, blue_ghost_y)


            # --- Orange Ghost Movement ---
            if is_ghost_centered(orange_ghost_x) and is_ghost_centered(orange_ghost_y):
                # SNAP to center so rounding errors don't build up
                orange_ghost_x, orange_ghost_y = snap_ghost_to_center(orange_ghost_x, orange_ghost_y)
        
                target = get_orange_target(orange_ghost_x, orange_ghost_y)
                orange_direction = choose_ghost_direction(orange_ghost_x, orange_ghost_y, orange_direction, target)
        
            # Move ghost by direction
            if orange_direction == "up":
                orange_ghost_y -= ghost_speed
            elif orange_direction == "down":
                orange_ghost_y += ghost_speed
            elif orange_direction == "left":
                orange_ghost_x -= ghost_speed
            elif orange_direction == "right":
                orange_ghost_x += ghost_speed
            
            
            # After moving, if ghost is now very close to the target tile center, snap to exact center
            if is_ghost_centered(orange_ghost_x) and is_ghost_centered(orange_ghost_y):
                orange_ghost_x, orange_ghost_y = snap_ghost_to_center(orange_ghost_x, orange_ghost_y)

            # Draw normally
            # --- Draw red ghost ---
            r_ghost_frames = red_ghost_sprites[red_direction]
            frame = r_ghost_frames[ghost_frame_index]
            draw_x = red_ghost_x - frame.get_width()/2
            draw_y = red_ghost_y - frame.get_height()/2
            screen.blit(frame, (draw_x, draw_y))
                
            # --- Draw blue ghost ---
            b_ghost_frames = blue_ghost_sprites[blue_direction]   
            frame = b_ghost_frames[ghost_frame_index]
            draw_x = blue_ghost_x - frame.get_width()/2
            draw_y = blue_ghost_y - frame.get_height()/2
            screen.blit(frame, (draw_x, draw_y))
                
            # --- Draw pink ghost ---
            p_ghost_frames = pink_ghost_sprites[pink_direction]
            frame = p_ghost_frames[ghost_frame_index]
            draw_x = pink_ghost_x - frame.get_width()/2
            draw_y = pink_ghost_y - frame.get_height()/2
            screen.blit(frame, (draw_x, draw_y))
                
            # --- Draw Orange ghost ---
            o_ghost_frames = orange_ghost_sprites[orange_direction]
            frame = o_ghost_frames[ghost_frame_index]
            draw_x = orange_ghost_x - frame.get_width()/2
            draw_y = orange_ghost_y - frame.get_height()/2
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
