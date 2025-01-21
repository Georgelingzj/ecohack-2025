import pygame

# Feedback Panel Constants
FEEDBACK_PANEL = pygame.Rect(300, 700, 700, 300)
MAX_FEEDBACK_SCROLL_HEIGHT = 260  # Slightly less than panel height

# Global variables for feedback
feedback_messages = []
feedback_scroll_offset = 0

def draw_scrollable_text(screen, messages, font, color, rect, scroll_offset=0):
    """
    Draw scrollable text within a given rectangle with text wrapping
    
    Args:
        screen (pygame.Surface): Surface to draw on
        messages (list): List of messages to display
        font (pygame.font.Font): Font to render text
        color (tuple): RGB color for text
        rect (pygame.Rect): Rectangle to draw text within
        scroll_offset (int, optional): Vertical scroll offset. Defaults to 0.
    """
    # Create a surface for clipping
    clip_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    clip_surface.fill((255, 255, 255, 0))  # Transparent background

    # Wrap text to fit within the rectangle width
    def wrap_text(text, font, max_width):
        words = text.split()
        wrapped_lines = []
        current_line = []
        current_line_width = 0

        for word in words:
            word_surface = font.render(word, True, color)
            word_width = word_surface.get_width()
            
            # If adding this word would exceed max width, start a new line
            if current_line_width + word_width > max_width:
                wrapped_lines.append(' '.join(current_line))
                current_line = [word]
                current_line_width = word_width
            else:
                current_line.append(word)
                current_line_width += word_width + font.render(' ', True, color).get_width()

        # Add the last line
        if current_line:
            wrapped_lines.append(' '.join(current_line))

        return wrapped_lines

    # Render messages with scrolling and wrapping
    y_offset = -scroll_offset
    line_height = font.get_linesize()
    max_width = rect.width - 10  # Leave some padding

    for message in messages:
        # Wrap the message
        wrapped_lines = wrap_text(message, font, max_width)
        
        # Render each wrapped line
        for line in wrapped_lines:
            text_surface = font.render(line, True, color)
            clip_surface.blit(text_surface, (5, y_offset))
            y_offset += line_height

            # Stop rendering if we've gone beyond the rect height
            if y_offset > rect.height:
                break

    # Blit the clipped surface onto the screen
    screen.blit(clip_surface, rect.topleft)

def draw_feedback_panel(screen, font):
    """
    Draw the feedback panel with scrollable messages
    
    Args:
        screen (pygame.Surface): The main game screen
        font (pygame.font.Font): Font for rendering text
    
    Returns:
        int: Total height of feedback messages
    """
    # Draw feedback panel background
    pygame.draw.rect(screen, (173, 216, 230), FEEDBACK_PANEL)  # LIGHT_BLUE
    pygame.draw.rect(screen, (0, 0, 0), FEEDBACK_PANEL, 2)  # BLACK border

    # Title for feedback panel
    title_surface = font.render("Simulation Feedback", True, (0, 0, 0))  # BLACK
    screen.blit(title_surface, (FEEDBACK_PANEL.left + 10, FEEDBACK_PANEL.top + 5))

    # Draw scrollable feedback messages
    feedback_rect = pygame.Rect(
        FEEDBACK_PANEL.left + 10, 
        FEEDBACK_PANEL.top + 30, 
        FEEDBACK_PANEL.width - 20, 
        FEEDBACK_PANEL.height - 40
    )
    
    draw_scrollable_text(
        screen, 
        feedback_messages, 
        font, 
        (0, 0, 0),  # BLACK 
        feedback_rect, 
        feedback_scroll_offset
    )

    # Return total height of feedback messages
    return len(feedback_messages) * font.get_linesize()

def handle_feedback_scroll(event, font):
    """
    Handle scrolling of feedback messages
    
    Args:
        event (pygame.event.Event): Pygame event for mouse scroll
        font (pygame.font.Font): Font to calculate line height
    
    Returns:
        int: Updated scroll offset
    """
    global feedback_scroll_offset

    # Calculate total height of feedback messages
    total_height = len(feedback_messages) * font.get_linesize()

    max_scroll = max(0, total_height - MAX_FEEDBACK_SCROLL_HEIGHT)

    if event.type == pygame.MOUSEWHEEL:
        if event.y > 0:
            feedback_scroll_offset = max(0, feedback_scroll_offset - 20)
        else:
            feedback_scroll_offset = min(max_scroll, feedback_scroll_offset + 20)

    return feedback_scroll_offset

def add_feedback(message):
    """
    Add a new feedback message
    
    Args:
        message (str): Feedback message to add
    """
    feedback_messages.append(message)
    
    # Limit the number of feedback messages
    if len(feedback_messages) > 50:
        feedback_messages.pop(0)