import pygame
import sys
import json
from inputdata import InputDataManager, truncate_text, wrap_text, handle_scroll
from visualization import InvasionSimulation
from feedback import draw_feedback_panel, handle_feedback_scroll, add_feedback
from conditions import GameConditions

pygame.init()

WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hackathon Eco Game Interface")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)

font = pygame.font.SysFont(None, 22)
input_font = pygame.font.SysFont(None, 28)

COMMENT_PANEL = pygame.Rect(0, 0, 300, 700)
INPUT_PANEL = pygame.Rect(0, 700, 300, 300)
GAME_AREA = pygame.Rect(300, 0, 700, 700)
FEEDBACK_PANEL = pygame.Rect(300, 700, 700, 300)
CONDITIONS_PANEL = pygame.Rect(300, 0, 700, 100)  # Top of game area

comments = []
user_input = {
    'species_count': None
}
input_fields = ['species_count']
current_field_index = 0
input_text = ""
input_active = False

input_manager = InputDataManager()

comments_scroll_offset = 0
MAX_SCROLL_HEIGHT = 680

environment = None

feedback_messages = []
feedback_scroll_offset = 0
MAX_FEEDBACK_SCROLL_HEIGHT = 260  # Slightly less than panel height

game_conditions = GameConditions()

def draw_environment():
    if environment is not None:
        # Create a surface for the environment
        env_surface = pygame.Surface((GAME_AREA.width, GAME_AREA.height - CONDITIONS_PANEL.height))
        env_surface.fill(WHITE)  # Fill with white background
        
        # Adjust grid size and cell size to fill more of the game area
        grid_width = 200  # Reduced grid width
        grid_height = 200  # Reduced grid height
        
        # Calculate cell size to maximize grid size while fitting in game area
        cell_size_x = GAME_AREA.width // grid_width
        cell_size_y = (GAME_AREA.height - CONDITIONS_PANEL.height) // grid_height
        cell_size = min(cell_size_x, cell_size_y)
        
        # Center the grid in the game area
        offset_x = (GAME_AREA.width - (grid_width * cell_size)) // 2
        offset_y = ((GAME_AREA.height - CONDITIONS_PANEL.height) - (grid_height * cell_size)) // 2
        
        # Render the environment
        for y in range(grid_height):
            for x in range(grid_width):
                species = environment.grid[y, x]
                color = environment.colors[species % len(environment.colors)]
                rect = pygame.Rect(
                    offset_x + x * cell_size, 
                    offset_y + y * cell_size, 
                    cell_size, 
                    cell_size
                )
                pygame.draw.rect(env_surface, color, rect)
        
        # Blit the environment surface onto the main screen at the game area
        screen.blit(env_surface, (GAME_AREA.left, GAME_AREA.top + CONDITIONS_PANEL.height))

def handle_input_events(event):
    global input_text, input_active, current_field_index, user_input, comments, environment

    if event.type == pygame.MOUSEBUTTONDOWN:
        input_box = INPUT_PANEL
        input_active = input_box.collidepoint(event.pos)
    
    if event.type == pygame.KEYDOWN and input_active:
        if event.key == pygame.K_RETURN:
            try:
                species_count = int(input_text.strip())
                if species_count < 1 or species_count > 5:
                    raise ValueError("Species count must be between 1 and 5")
                
                user_input['species_count'] = species_count
                comments.append(f"Species count set to: {species_count}")
                
                initialize_environment(None, species_count)
                
                input_text = ""
                input_active = False
                current_field_index = len(input_fields)
                game_conditions.update()  # Update game conditions after user input
                add_feedback(f"Game conditions updated for {species_count} species.")
            
            except ValueError as e:
                comments.append(f"Error: {str(e)}")
                input_text = ""
        
        elif event.key == pygame.K_BACKSPACE:
            input_text = input_text[:-1]
        
        elif event.key == pygame.K_ESCAPE:
            input_text = ""
            input_active = False
        
        else:
            if event.unicode.isdigit():
                input_text += event.unicode

def draw_input_field():
    # Always draw input field before all inputs are completed
    if current_field_index >= len(input_fields):
        return
    
    current_field = input_fields[current_field_index]
    
    field_prompts = {
        'species_count': 'Enter number of species (1-5)'
    }
    
    prompt_text = field_prompts.get(current_field, current_field)
    wrapped_prompt = wrap_text(prompt_text, input_font, 280)
    
    y_offset = 720
    for line in wrapped_prompt:
        prompt_surface = input_font.render(line, True, WHITE)
        screen.blit(prompt_surface, (10, y_offset))
        y_offset += input_font.get_linesize()
    
    # Show current input or placeholder
    current_value = str(input_text) if input_text else ''
    field_text = f"{current_field}: {current_value}"
    wrapped_field_text = wrap_text(field_text, input_font, 280)
    
    for line in wrapped_field_text:
        field_surface = input_font.render(line, True, WHITE)
        screen.blit(field_surface, (10, y_offset))
        y_offset += input_font.get_linesize()
    
    # Draw input box
    input_box = pygame.Rect(10, y_offset + 10, 280, 50)
    pygame.draw.rect(screen, WHITE if input_active else GRAY, input_box, 2)

def initialize_environment(environment_type, species_count):
    global environment
    
    environment = InvasionSimulation(
        width=200,  
        height=200,  
        species_count=species_count
    )
    
    environment.initialize_random()

def draw_conditions():
    # Draw conditions panel
    pygame.draw.rect(screen, LIGHT_BLUE, CONDITIONS_PANEL)
    conditions = game_conditions.get_current_conditions()
    
    # Format conditions text
    conditions_text = [
        f"Year: {conditions['year']} | Month: {conditions['month']} | Week: {conditions['week']}",
        f"Temperature: {conditions['temperature']}°C | Humidity: {conditions['humidity']}% | Weather: {conditions['weather']}"
    ]
    
    y_offset = 20
    for text in conditions_text:
        text_surface = font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(CONDITIONS_PANEL.centerx, CONDITIONS_PANEL.top + y_offset))
        screen.blit(text_surface, text_rect)
        y_offset += 30

running = True
clock = pygame.time.Clock()

# Track time for periodic updates
last_update_time = pygame.time.get_ticks()
UPDATE_INTERVAL = 1000  # 1 second between updates

while running:
    # Clear the screen
    screen.fill(WHITE)
    
    # Draw panels
    pygame.draw.rect(screen, GRAY, COMMENT_PANEL)
    pygame.draw.rect(screen, DARK_GRAY, INPUT_PANEL)
    
    # Draw input field
    draw_input_field()
    
    # Draw game environment
    draw_environment()
    
    # Draw conditions panel
    draw_conditions()
    
    # Draw feedback panel and get its total height
    feedback_total_height = draw_feedback_panel(screen, font)
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Existing input and comment scroll handling
        handle_input_events(event)
        
        # New feedback scroll handling
        handle_feedback_scroll(event, font)
    
    # Periodic environment update
    current_time = pygame.time.get_ticks()
    if current_time - last_update_time > UPDATE_INTERVAL:
        if environment is not None:
            environment.update()
            game_conditions.update()  # Explicitly update game conditions
            # Feedback about both environment and conditions
            add_feedback(f"Environment and game conditions updated.")
        
        last_update_time = current_time
    
    # Update display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(30)

pygame.quit()
sys.exit()
