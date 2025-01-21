import pygame
import numpy as np

class DynamicVisualizer:
    def __init__(self, screen, cell_size=5):
        self.screen = screen
        self.cell_size = cell_size
        self.color_palette = {
            'empty': (200, 200, 200),  # Light grey for empty cells
            'species': [
                (255, 0, 0),    # Red for first species
                (0, 255, 0),    # Green for second species
                (0, 0, 255),    # Blue for third species
                (255, 255, 0),  # Yellow for fourth species
                (255, 0, 255),  # Magenta for fifth species
            ]
        }
        self.environmental_effects = {
            'pollution': 0,     # 0-100 scale
            'temperature': 25,  # Celsius
            'nutrients': 50,    # 0-100 scale
            'deforestation': 0  # 0-100 scale
        }

    def update_environmental_effects(self, environment):
        """
        Update environmental effects from the Environment object
        """
        self.environmental_effects = {
            'pollution': environment.pollution,
            'temperature': environment.climate_change,  # Using climate_change as a proxy for temperature
            'nutrients': environment.nutrients,
            'deforestation': environment.deforestation
        }

    def apply_environmental_overlay(self, base_color):
        """
        Apply environmental effects to the base color
        """
        # Pollution: Desaturate and grey out colors
        pollution_factor = self.environmental_effects['pollution'] / 100
        grey_color = tuple(int(sum(base_color) / 3) for _ in range(3))
        color = tuple(
            int(c * (1 - pollution_factor) + grey_color[i] * pollution_factor)
            for i, c in enumerate(base_color)
        )

        # Temperature: Shift color temperature
        temp_factor = (self.environmental_effects['temperature'] - 25) / 50
        if temp_factor > 0:  # Warmer
            color = tuple(
                min(255, int(c * (1 + temp_factor * 0.5))) for c in color
            )
        else:  # Cooler
            color = tuple(
                max(0, int(c * (1 + temp_factor * 0.5))) for c in color
            )

        # Nutrients: Adjust saturation
        nutrients_factor = self.environmental_effects['nutrients'] / 100
        color = tuple(
            int(c * (0.5 + nutrients_factor * 0.5)) for c in color
        )

        return color

    def render_grid(self, grid):
        """
        Render the grid with dynamic environmental effects
        """
        for y, row in enumerate(grid):
            for x, species_id in enumerate(row):
                # Select base color
                if species_id == 0:
                    base_color = self.color_palette['empty']
                else:
                    base_color = self.color_palette['species'][species_id % len(self.color_palette['species'])]
                
                # Apply environmental overlay
                color = self.apply_environmental_overlay(base_color)
                
                # Draw cell
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(self.screen, color, rect)

    def render_environmental_indicators(self):
        """
        Render additional environmental indicators
        """
        # Pollution indicator
        pollution_height = int(self.screen.get_height() * 0.05)
        pollution_width = int(self.screen.get_width() * (self.environmental_effects['pollution'] / 100))
        pollution_rect = pygame.Rect(0, 0, pollution_width, pollution_height)
        pygame.draw.rect(self.screen, (100, 100, 100), pollution_rect)

        # Temperature indicator
        temp_color = self._get_temperature_color()
        temp_height = int(self.screen.get_height() * 0.05)
        temp_width = int(self.screen.get_width() * ((self.environmental_effects['temperature'] + 50) / 100))
        temp_rect = pygame.Rect(0, pollution_height, temp_width, temp_height)
        pygame.draw.rect(self.screen, temp_color, temp_rect)

    def _get_temperature_color(self):
        """
        Generate a color based on temperature
        """
        temp = self.environmental_effects['temperature']
        if temp < 0:
            return (0, 0, 255)  # Cold blue
        elif temp < 25:
            return (0, 255, 255)  # Cool cyan
        elif temp < 50:
            return (255, 255, 0)  # Warm yellow
        else:
            return (255, 0, 0)  # Hot red