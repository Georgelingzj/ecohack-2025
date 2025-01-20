import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1400, 1400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hackathon Eco Game Interface")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Fonts
font = pygame.font.SysFont(None, 28)
input_font = pygame.font.SysFont(None, 36)

# Panels
COMMENT_PANEL = pygame.Rect(0, 0, 400, 1000)
INPUT_PANEL = pygame.Rect(0, 1000, 400, 400)
GAME_AREA = pygame.Rect(400, 0, 1000, 1400)

# Data
comments = []
user_input = ""

# Draw the interface
def draw_interface():
    # Draw panels
    pygame.draw.rect(screen, GRAY, COMMENT_PANEL)
    pygame.draw.rect(screen, DARK_GRAY, INPUT_PANEL)
    pygame.draw.rect(screen, WHITE, GAME_AREA)

    # Draw labels
    comment_title = font.render("Comments History", True, BLACK)
    input_title = font.render("User Input", True, WHITE)
    screen.blit(comment_title, (10, 10))
    screen.blit(input_title, (10, 1010))

    # Draw comments
    y_offset = 40
    for comment in comments[-20:]:  # Display the last 20 comments
        comment_surface = font.render(comment, True, BLACK)
        screen.blit(comment_surface, (10, y_offset))
        y_offset += 30

    # Draw user input
    input_surface = input_font.render(user_input, True, WHITE)
    screen.blit(input_surface, (10, 1250))

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Submit user input
                if user_input.strip():
                    comments.append(user_input.strip())  # Add to comments history
                    user_input = ""  # Clear input
            elif event.key == pygame.K_BACKSPACE:  # Delete last character
                user_input = user_input[:-1]
            else:  # Add typed character
                user_input += event.unicode

    # Clear screen
    screen.fill(WHITE)

    # Draw interface
    draw_interface()

    # Update the display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
