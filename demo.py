import pygame
import sys
import json
from inputdata import InputDataManager
from visualization import InvasionSimulation

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
RED = (255, 0, 0)

# Fonts
font = pygame.font.SysFont(None, 28)
input_font = pygame.font.SysFont(None, 36)

# Panels
COMMENT_PANEL = pygame.Rect(0, 0, 400, 1000)
INPUT_PANEL = pygame.Rect(0, 1000, 400, 400)
GAME_AREA = pygame.Rect(400, 0, 1000, 1400)

# Data
comments = []
user_input = {
    'species_count': 5,  # Default value
    'environment_type': '',
    'interaction_mode': ''
}
input_fields = ['species_count', 'environment_type', 'interaction_mode']
current_field_index = 0
input_text = ""
input_active = False

# Input Data Manager
input_manager = InputDataManager()

# Global scroll variables
comments_scroll_offset = 0
MAX_SCROLL_HEIGHT = 960  # Height of comment panel

# Global environment simulation
environment = None

def truncate_text(text, font, max_width):
    """
    Truncate text to fit within a specified width.
    
    Args:
        text (str): The text to truncate
        font (pygame.font.Font): The font used to render text
        max_width (int): Maximum width in pixels
    
    Returns:
        str: Truncated text with ellipsis if too long
    """
    if not text:
        return text
    
    # If text is already short enough, return as-is
    if font.render(text, True, WHITE).get_width() <= max_width:
        return text
    
    # Binary search to find the right truncation point
    left, right = 0, len(text)
    while left < right:
        mid = (left + right + 1) // 2
        truncated = text[:mid] + '...'
        rendered = font.render(truncated, True, WHITE)
        
        if rendered.get_width() <= max_width:
            left = mid
        else:
            right = mid - 1
    
    return text[:left] + '...'

def wrap_text(text, font, max_width):
    """
    Wrap text to multiple lines based on max width.
    
    Args:
        text (str): Text to wrap
        font (pygame.font.Font): Font used for rendering
        max_width (int): Maximum width in pixels
    
    Returns:
        list: List of text lines
    """
    words = text.split()
    wrapped_lines = []
    current_line = []
    current_line_width = 0

    for word in words:
        # Render the word to get its width
        word_surface = font.render(word, True, BLACK)
        word_width = word_surface.get_width()
        
        # Check if adding this word would exceed max width
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, BLACK)
        
        if test_surface.get_width() <= max_width:
            current_line.append(word)
        else:
            # Start a new line
            if current_line:
                wrapped_lines.append(' '.join(current_line))
            current_line = [word]
    
    # Add the last line
    if current_line:
        wrapped_lines.append(' '.join(current_line))
    
    return wrapped_lines

def draw_scrollable_text(surface, text, font, color, rect, scroll_offset=0):
    """
    Draw scrollable text with mouse wheel support.
    
    Args:
        surface (pygame.Surface): Surface to draw on
        text (list): List of text lines to draw
        font (pygame.font.Font): Font to use
        color (tuple): RGB color of text
        rect (pygame.Rect): Rectangle to draw within
        scroll_offset (int): Vertical scroll offset
    
    Returns:
        int: Total height of content
    """
    # Clip drawing to the specified rectangle
    surface.set_clip(rect)
    
    # Calculate line height
    line_height = font.get_linesize()
    
    # Total content height
    total_height = len(text) * line_height
    
    # Draw each line of text
    y_offset = rect.top - scroll_offset
    for line in text:
        text_surface = font.render(line, True, color)
        
        # Only draw if line is within visible area
        if y_offset + line_height >= rect.top and y_offset < rect.bottom:
            surface.blit(text_surface, (rect.left + 5, y_offset))
        
        y_offset += line_height
    
    # Remove clipping
    surface.set_clip(None)
    
    return total_height

def handle_scroll(event, total_height, max_scroll_height):
    """
    Handle mouse wheel scrolling.
    
    Args:
        event (pygame.event.Event): Pygame event
        total_height (int): Total height of content
        max_scroll_height (int): Maximum scrollable height
    
    Returns:
        int: Updated scroll offset
    """
    global comments_scroll_offset
    
    # Calculate maximum scroll
    max_scroll = max(0, total_height - max_scroll_height)
    
    # Handle mouse wheel
    if event.type == pygame.MOUSEWHEEL:
        if event.y > 0:
            # Scroll up
            comments_scroll_offset = max(0, comments_scroll_offset - 20)
        elif event.y < 0:
            # Scroll down
            comments_scroll_offset = min(max_scroll, comments_scroll_offset + 20)
    
    return comments_scroll_offset

def initialize_environment(environment_type, species_count):
    """
    Initialize the environment based on user input.
    
    Args:
        environment_type (str): Type of environment (not used in this version)
        species_count (int): Number of species from user input
    """
    global environment
    
    # Create invasion simulation with specified species count
    environment = InvasionSimulation(
        width=280,  # Adjusted to fit game area
        height=400, 
        species_count=species_count
    )
    
    # Randomly initialize the grid
    environment.initialize_random()

def handle_input_events(event):
    """Handle input events for user input"""
    global input_text, input_active, current_field_index, user_input, comments

    if event.type == pygame.MOUSEBUTTONDOWN:
        input_box = pygame.Rect(10, 1130, 380, 50)
        input_active = input_box.collidepoint(event.pos)
    
    if event.type == pygame.KEYDOWN and input_active:
        if event.key == pygame.K_RETURN:
            # Save the current input
            try:
                # Ensure we're within the input fields range
                if current_field_index >= len(input_fields):
                    comments.append("All inputs already completed.")
                    input_text = ""
                    return

                current_field = input_fields[current_field_index]
                
                # Validate and convert input based on field
                if current_field == 'species_count':
                    species_count = int(input_text.strip())
                    if species_count <= 0:
                        raise ValueError("Species count must be a positive integer")
                    user_input[current_field] = species_count
                else:
                    # Validate other inputs are not empty
                    if not input_text.strip():
                        raise ValueError(f"{current_field} cannot be empty")
                    user_input[current_field] = input_text.strip().lower()
                
                # Add comment showing the input
                comments.append(f"Input for {current_field}: {input_text}")
                
                # Move to next field
                current_field_index += 1
                
                # Reset input text after each input
                input_text = ""
                
                # Check if all inputs are completed
                if current_field_index >= len(input_fields):
                    # Save the complete input
                    filepath = input_manager.save_input(user_input)
                    comments.append(f"All inputs saved to {filepath}")
                    comments.append(f"Final Input: {json.dumps(user_input, indent=2)}")
                    
                    # Initialize environment based on user input
                    initialize_environment(
                        user_input['environment_type'], 
                        user_input['species_count']
                    )
                    
                    # Disable further input
                    input_active = False
            
            except ValueError as e:
                comments.append(f"Error: {str(e)}")
                input_text = ""
        
        elif event.key == pygame.K_BACKSPACE:
            input_text = input_text[:-1]
        
        elif event.key == pygame.K_ESCAPE:
            # Allow cancelling current input
            input_text = ""
            input_active = False
        
        else:
            # Limit input length and allow only appropriate characters
            if current_field_index == 0:  # species_count
                # Only allow digits for species count
                if event.unicode.isdigit():
                    input_text += event.unicode
            else:
                # Allow any text input for other fields
                input_text += event.unicode

def draw_input_field():
    """Draw the current input field and its value"""
    # Only draw input if not all fields are completed
    if current_field_index >= len(input_fields):
        return
    
    current_field = input_fields[current_field_index]
    
    # Determine the prompt text based on the current field
    field_prompts = {
        'species_count': 'Enter number of species (positive integer)',
        'environment_type': 'Enter environment (forest/desert/ocean/tundra)',
        'interaction_mode': 'Enter interaction mode (predator_prey/cooperative/competitive)'
    }
    
    # Wrap the prompt text
    prompt_text = field_prompts.get(current_field, current_field)
    wrapped_prompt = wrap_text(prompt_text, input_font, 380)
    
    # Render wrapped prompt
    y_offset = 1020
    for line in wrapped_prompt:
        prompt_surface = input_font.render(line, True, WHITE)
        screen.blit(prompt_surface, (10, y_offset))
        y_offset += input_font.get_linesize()
    
    # Current field value
    current_value = str(user_input[current_field]) if user_input[current_field] else ''
    field_text = f"{current_field}: {current_value}"
    wrapped_field_text = wrap_text(field_text, input_font, 380)
    
    # Render wrapped field text
    for line in wrapped_field_text:
        field_surface = input_font.render(line, True, WHITE)
        screen.blit(field_surface, (10, y_offset))
        y_offset += input_font.get_linesize()
    
    # Draw input text box
    input_box = pygame.Rect(10, y_offset + 10, 380, 50)
    pygame.draw.rect(screen, WHITE if input_active else GRAY, input_box, 2)
    
    # Wrap input text
    wrapped_input = wrap_text(input_text, input_font, 370)
    
    # Render input text
    for line in wrapped_input:
        text_surface = input_font.render(line, True, WHITE)
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5 + 
                    (wrapped_input.index(line) * input_font.get_linesize())))

def draw_comments():
    """Draw the comments section"""
    # Draw comments panel
    pygame.draw.rect(screen, GRAY, COMMENT_PANEL)
    
    # Draw comments title
    comment_title = font.render("Comments History", True, BLACK)
    screen.blit(comment_title, (10, 10))
    
    # Wrap comments
    wrapped_comments = []
    for comment in comments:
        wrapped_comments.extend(wrap_text(comment, font, 380))
    
    # Draw scrollable comments
    total_height = draw_scrollable_text(
        screen, 
        wrapped_comments,
        font, 
        BLACK, 
        pygame.Rect(0, 40, 400, 960),
        comments_scroll_offset
    )

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events first
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        
        # Handle input events
        handle_input_events(event)
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw input field
    draw_input_field()
    
    # Update and render environment if initialized
    if environment:
        environment.update()
        environment.render(screen)
    
    # Draw comments section
    draw_comments()
    
    # Update display
    pygame.display.flip()
    
    # Increase frame rate to 30 FPS for smoother interaction
    clock.tick(30)

# Quit the game
pygame.quit()
sys.exit()
