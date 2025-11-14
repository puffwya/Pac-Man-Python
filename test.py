import pygame

pygame.init()
pygame.font.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame Text Example")

white = (255, 255, 255)
black = (0, 0, 0)

# Create a font object
font = pygame.font.SysFont("Arial", 50)

# Render the text
text_surface = font.render("Welcome to Pygame!", True, white)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(black) # Fill the background

    # Blit the text to the screen
    screen.blit(text_surface, (100,100))

    pygame.display.flip()

pygame.quit()
