import json
from typing import Dict, Any
from datetime import datetime
import os
import pygame

class InputDataManager:
    def __init__(self, data_dir='input_data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, str]:
        errors = {}
        
        try:
            species_count = input_data['species_count']
            if not isinstance(species_count, int):
                errors['species_count'] = "Species count must be an integer"
            elif species_count <= 0 or species_count > 5:
                errors['species_count'] = "Species count must be between 1 and 5"
        except Exception:
            errors['species_count'] = "Invalid species count"
        
        return errors
    
    def save_input(self, input_data: Dict[str, Any]) -> str:
        validation_errors = self.validate_input(input_data)
        
        if validation_errors:
            error_message = "Invalid input data:\n" + "\n".join(
                f"- {key}: {value}" for key, value in validation_errors.items()
            )
            raise ValueError(error_message)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"input_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(input_data, f, indent=4)
        
        return filepath
    
    def load_latest_input(self) -> Dict[str, Any]:
        input_files = [f for f in os.listdir(self.data_dir) if f.startswith('input_') and f.endswith('.json')]
        
        if not input_files:
            return {}
        
        latest_file = max(input_files)
        filepath = os.path.join(self.data_dir, latest_file)
        
        with open(filepath, 'r') as f:
            return json.load(f)

def truncate_text(text, font, max_width):
    """
    Truncate text to fit within a specified width, adding ellipsis if needed.
    
    Args:
        text (str): The text to truncate
        font (pygame.font.Font): The font used for rendering
        max_width (int): Maximum allowed width
    
    Returns:
        str: Truncated text
    """
    if not text:
        return text
    
    if font.render(text, True, (255, 255, 255)).get_width() <= max_width:
        return text
    
    left, right = 0, len(text)
    while left < right:
        mid = (left + right + 1) // 2
        truncated = text[:mid] + '...'
        rendered = font.render(truncated, True, (255, 255, 255))
        
        if rendered.get_width() <= max_width:
            left = mid
        else:
            right = mid - 1
    
    return text[:left] + '...'

def wrap_text(text, font, max_width):
    """
    Wrap text to fit within a specified width.
    
    Args:
        text (str): The text to wrap
        font (pygame.font.Font): The font used for rendering
        max_width (int): Maximum allowed width
    
    Returns:
        list: List of wrapped text lines
    """
    words = text.split()
    wrapped_lines = []
    current_line = []
    current_line_width = 0

    for word in words:
        word_surface = font.render(word, True, (0, 0, 0))
        word_width = word_surface.get_width()
        
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, (0, 0, 0))
        
        if test_surface.get_width() <= max_width:
            current_line.append(word)
        else:
            if current_line:
                wrapped_lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        wrapped_lines.append(' '.join(current_line))
    
    return wrapped_lines

def handle_scroll(event, total_height, max_scroll_height):
    """
    Handle scrolling for a scrollable text area.
    
    Args:
        event (pygame.event.Event): The pygame event
        total_height (int): Total height of the content
        max_scroll_height (int): Maximum scrollable height
    
    Returns:
        int: Updated scroll offset
    """
    scroll_offset = 0
    max_scroll = max(0, total_height - max_scroll_height)
    
    if event.type == pygame.MOUSEWHEEL:
        if event.y > 0:
            scroll_offset = max(0, scroll_offset - 20)
        elif event.y < 0:
            scroll_offset = min(max_scroll, scroll_offset + 20)
    
    return scroll_offset