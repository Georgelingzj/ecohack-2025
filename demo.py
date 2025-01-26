import pygame
import sys
import json
import numpy as np

from src.ui.inputdata import InputDataManager, truncate_text, wrap_text, handle_scroll
from src.visual.visualization import InvasionSimulation, FCMVisualizer, EcologicalFCM
from src.ui.feedback import draw_feedback_panel, handle_feedback_scroll, add_feedback
from src.environment.conditions import GameConditions
from src.ui.plotting import DensityPlotter




pygame.init()

WIDTH = 1400  # Increased from 1000
HEIGHT = 1000
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

# Panel definitions
CHAT_HISTORY_PANEL = pygame.Rect(0, 0, 300, 700)
CHAT_INPUT_PANEL = pygame.Rect(0, 700, 300, 300)
GAME_AREA = pygame.Rect(300, 0, 700, 1000)
FCM_PANEL = pygame.Rect(1000, 0, 400, 800)  # FCM graphs panel
INFO_PANEL = pygame.Rect(1000, 800, 400, 200)  # Info panel below FCMs
FEEDBACK_PANEL = pygame.Rect(300, 700, 700, 300)  # For density plot

comments = []
user_input = {
    'species_count': None,
    'reduce_pollution': None,
    'temperature': None,
    'humidity': None
}
input_fields = [
    'reduce_pollution',
    'temperature',
    'humidity'
]
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

field_prompts = {
    'reduce_pollution': 'Enter pollution reduction effort (0-100%)',
    'temperature': 'Enter temperature (0-40°C)',
    'humidity': 'Enter humidity (0-100%, 50 is neutral)'
}

density_plotter = None

# Add new constants for the start button
START_BUTTON = pygame.Rect(10, 750, 280, 50)  # Moved up to be visible
START_BUTTON_COLOR = (50, 168, 82)  # Green color
START_BUTTON_HOVER = (60, 198, 97)  # Lighter green for hover
game_started = False

# Add new state variables
selected_parameter = 0  # Index of currently selected parameter
parameter_names = ['temperature', 'humidity', 'pollution_reduction']
parameter_ranges = {
    'temperature': (0, 40, '°C'),
    'humidity': (0, 100, '%'),
    'pollution_reduction': (0, 100, '%')
}

# Initialize both FCM visualizers
fcm_visualizer = FCMVisualizer()
ecological_fcm = EcologicalFCM()

def draw_environment():
    if environment is not None:
        # Get the rendered environment surface
        env_surface = environment.render(screen, cell_size=4)
        
        # Calculate fixed size for the game area
        fixed_width = GAME_AREA.width - 100  # 50px padding on each side
        fixed_height = GAME_AREA.height - 100  # 50px padding top/bottom
        
        # Scale environment to fixed size
        env_surface = pygame.transform.scale(env_surface, (fixed_width, fixed_height))
        
        # Center position
        x_offset = GAME_AREA.left + (GAME_AREA.width - fixed_width) // 2
        y_offset = GAME_AREA.top + (GAME_AREA.height - fixed_height) // 2
        
        # Draw weather background
        weather_color = environment.weather_colors.get(environment.current_weather, (255, 255, 255))
        weather_rect = pygame.Rect(
            GAME_AREA.left,
            GAME_AREA.top,
            GAME_AREA.width,
            GAME_AREA.height
        )
        pygame.draw.rect(screen, weather_color, weather_rect)
        
        # Draw border
        border_rect = pygame.Rect(
            x_offset - 2,
            y_offset - 2,
            fixed_width + 4,
            fixed_height + 4
        )
        pygame.draw.rect(screen, (200, 200, 200), border_rect)
        
        # Draw environment
        screen.blit(env_surface, (x_offset, y_offset))

def draw_start_button(mouse_pos):
    """Draw the start button and handle hover effect"""
    button_color = START_BUTTON_COLOR
    if START_BUTTON.collidepoint(mouse_pos):
        button_color = START_BUTTON_HOVER
        
    pygame.draw.rect(screen, button_color, START_BUTTON)
    
    # Draw button text
    start_text = "Start Simulation"
    text_surface = input_font.render(start_text, True, WHITE)
    text_rect = text_surface.get_rect(center=START_BUTTON.center)
    screen.blit(text_surface, text_rect)

def handle_input_events(event):
    global input_text, input_active, current_field_index, user_input, comments, environment, game_started, selected_parameter

    if event.type == pygame.MOUSEBUTTONDOWN:
        # Check for start button click
        if not game_started and START_BUTTON.collidepoint(event.pos):
            game_started = True
            initialize_environment(None)
            return
            
        # Check for chat input box click
        input_box = pygame.Rect(10, CHAT_INPUT_PANEL.top + 10, 
                              CHAT_INPUT_PANEL.width - 20, 40)
        input_active = input_box.collidepoint(event.pos)
    
    elif event.type == pygame.KEYDOWN:
        if input_active:
            if event.key == pygame.K_RETURN and input_text:
                # Process chat message
                params = input_manager.process_chat_message(input_text)
                
                # Update environment based on extracted parameters
                if environment:
                    if 'temperature' in params:
                        environment.set_temperature(params['temperature'])
                    if 'humidity' in params:
                        environment.set_humidity(params['humidity'])
                    if 'pollution' in params:
                        environment.set_pollution_reduction(params['pollution'])
                
                input_text = ""
            
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                input_text = ""
                input_active = False
            else:
                input_text += event.unicode

def draw_input_field():
    # Always draw input field before all inputs are completed
    if current_field_index >= len(input_fields):
        return
    
    current_field = input_fields[current_field_index]
    
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

def initialize_environment(environment_type, species_count=None):
    global environment, density_plotter
    
    density_plotter = DensityPlotter(3)  # Initialize with 3 species
    environment = InvasionSimulation(
        width=200,  
        height=200,
        density_plotter=density_plotter  # Pass the density plotter
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

def draw_environment_stats():
    """Draw current environmental parameters"""
    if environment:
        stats_text = [
            f"Pollution Reduction: {environment.pollution_reduction}%",
            f"Temperature: {environment.temperature}°",
            f"Humidity: {environment.humidity}%"
        ]
        
        y_offset = CONDITIONS_PANEL.bottom + 10
        for text in stats_text:
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (GAME_AREA.left + 10, y_offset))
            y_offset += 25

def draw_game_status():
    """Draw game status information"""
    if environment:
        # Calculate densities
        total_cells = environment.grid.size
        native_density = np.sum(environment.grid == 1) / total_cells * 100
        invasive_density = np.sum(environment.grid == 2) / total_cells * 100
        total_density = native_density + invasive_density
        
        # Draw density information
        status_text = [
            f"Native Species: {native_density:.1f}%",
            f"Invasive Species: {invasive_density:.1f}%",
            f"Total Population: {total_density:.1f}%"
        ]
        
        if environment.victory_condition_met:
            status_text.append("Victory! Invasive species controlled!")
        elif environment.game_over:
            status_text.append("Game Over - Population collapsed!")
        
        # Add endangered species status
        endangered_status = environment.get_endangered_status()
        status_text.append(endangered_status)
        
        # Use different colors based on status
        if "critical" in endangered_status.lower():
            status_color = RED
        elif "alert" in endangered_status.lower():
            status_color = (255, 140, 0)  # Orange
        else:
            status_color = BLACK
        
        y_offset = CONDITIONS_PANEL.bottom + 50
        for text in status_text:
            text_surface = font.render(text, True, status_color)
            screen.blit(text_surface, (GAME_AREA.left + 10, y_offset))
            y_offset += 25
        
        # Draw currently selected parameter
        param = parameter_names[selected_parameter]
        current_val = getattr(environment, param)
        min_val, max_val, unit = parameter_ranges[param]
        selected_text = f"Selected: {param} ({current_val}{unit})"
        text_surface = font.render(selected_text, True, RED)
        screen.blit(text_surface, (GAME_AREA.left + 10, y_offset + 25))

def draw_game():
    # Draw original FCM graph
    pygame.draw.rect(screen, WHITE, FCM_PANEL)
    if environment:
        fcm_visualizer.update_values(environment)
        fcm_visualizer.render(screen, pygame.Rect(FCM_PANEL.left, FCM_PANEL.top, 
                                                FCM_PANEL.width, FCM_PANEL.height//2))
        
        # Draw ecological FCM below
        ecological_fcm.update_values(environment)
        ecological_fcm.render(screen, pygame.Rect(FCM_PANEL.left, FCM_PANEL.top + FCM_PANEL.height//2,
                                                FCM_PANEL.width, FCM_PANEL.height//2))

def draw_chat_history():
    """Draw chat history in the left panel"""
    history_surface = pygame.Surface((CHAT_HISTORY_PANEL.width, CHAT_HISTORY_PANEL.height))
    history_surface.fill(GRAY)
    
    y_offset = 10
    for sender, message in input_manager.chat_history[-20:]:  # Show last 20 messages
        color = DARK_GRAY if sender == "system" else BLACK
        text_surface = font.render(f"{sender}: {message}", True, color)
        history_surface.blit(text_surface, (10, y_offset))
        y_offset += 25
    
    screen.blit(history_surface, CHAT_HISTORY_PANEL)

def draw_chat_input():
    """Draw chat input box"""
    pygame.draw.rect(screen, DARK_GRAY, CHAT_INPUT_PANEL)
    
    # Draw input box
    input_box = pygame.Rect(10, CHAT_INPUT_PANEL.top + 10, 
                           CHAT_INPUT_PANEL.width - 20, 40)
    pygame.draw.rect(screen, WHITE, input_box)
    
    # Draw input text
    if input_text:
        text_surface = input_font.render(input_text, True, BLACK)
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

def draw_game_info():
    """Draw game information in the right panel"""
    if environment:
        info_surface = pygame.Surface((INFO_PANEL.width, INFO_PANEL.height))
        info_surface.fill(WHITE)
        
        # Calculate densities
        total_cells = environment.grid.size
        native_density = np.sum(environment.grid == 1) / total_cells * 100
        invasive_density = np.sum(environment.grid == 2) / total_cells * 100
        
        # Create info text
        info_text = [
            f"Environmental Parameters:",
            f"Temperature: {environment.temperature}°C",
            f"Humidity: {environment.humidity}%",
            f"Pollution Reduction: {environment.pollution_reduction}%",
            "",
            f"Species Status:",
            f"Native: {native_density:.1f}%",
            f"Invasive: {invasive_density:.1f}%",
            f"Weather: {environment.current_weather}"
        ]
        
        y_offset = 10
        for text in info_text:
            text_surface = font.render(text, True, BLACK)
            info_surface.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        screen.blit(info_surface, INFO_PANEL)

running = True
clock = pygame.time.Clock()

# Track time for periodic updates
last_update_time = pygame.time.get_ticks()
UPDATE_INTERVAL = 1000  # 1 second between updates

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Clear the screen
    screen.fill(WHITE)
    
    if not game_started:
        # Draw start button when game hasn't started
        draw_start_button(mouse_pos)
    else:
        # Draw chat interface
        draw_chat_history()
        draw_chat_input()
        
        # Draw game elements
        draw_environment()
        
        # Draw FCM graphs
        draw_game()
        
        # Draw game info below FCMs
        draw_game_info()
        
        # Update and draw plot
        if density_plotter and environment:
            density_plotter.update(environment.grid)
            density_plotter.render(screen, FEEDBACK_PANEL)
        
        # Periodic environment update
        current_time = pygame.time.get_ticks()
        if current_time - last_update_time > UPDATE_INTERVAL:
            if environment is not None:
                environment.update()
                game_conditions.update()
                
                # Get current conditions and update environment weather
                conditions = game_conditions.get_current_conditions()
                environment.set_weather(conditions['weather'])
            
            last_update_time = current_time
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        handle_input_events(event)
        
        if game_started:
            handle_feedback_scroll(event, font)
    
    # Update display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(30)

pygame.quit()
sys.exit()
