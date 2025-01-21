import numpy as np
import pygame
import random

class InvasionSimulation:
    def __init__(self, width=100, height=100, species_count=5):
        self.width = width
        self.height = height
        self.species_count = species_count
        self.grid = np.zeros((height, width), dtype=int)
        self.current_weather = "Clear"
        self.pollution_reduction = 0  # Only used for update frequency
        
        # Base colors for species
        self.colors = [
            (255, 255, 255),  # Default color, will be replaced by weather color
            (0, 0, 0),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0)
        ]
        
        # Weather-specific background colors
        self.weather_colors = {
            "Clear": (255, 252, 245),      # Warm white with slight yellow tint
            "Foggy": (235, 235, 235),      # Light grey
            "Rainy": (235, 245, 255),      # Very light blue
            "Cloudy": (245, 245, 250),     # Light grey with slight blue tint
            "Snowy": (250, 250, 255),      # White with blue tint
            "Windy": (250, 255, 250)       # White with slight green tint
        }
    
    def initialize_random(self):
        """Randomly initialize species on the grid"""
        # Clear the grid first
        self.grid.fill(0)
        
        # Randomly place species
        for _ in range((self.width * self.height) // 3):  # Fill about 1/3 of the grid
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            species = random.randint(1, self.species_count)
            self.grid[y, x] = species
    
    def update(self):
        new_grid = self.grid.copy()
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                current_species = self.grid[y, x]
                
                if current_species == 0:
                    # Empty cell - check for invasion
                    # Increase required neighbors based on pollution reduction
                    required_neighbors = 3 + round(self.pollution_reduction / 25)  # Every 25% adds 1 required neighbor
                    invading_species = [
                        species for species, count in neighbors.items() 
                        if species != 0 and count >= required_neighbors
                    ]
                    if invading_species:
                        new_grid[y, x] = max(set(invading_species), key=invading_species.count)
                else:
                    # Occupied cell
                    species_neighbors = neighbors[current_species]
                    
                    # Die if too few or too many neighbors
                    if species_neighbors < 2 or species_neighbors > 3:
                        new_grid[y, x] = 0
                    
                    # Check for invasion by other species
                    other_species_neighbors = sum(neighbors.values()) - species_neighbors
                    if other_species_neighbors > species_neighbors:
                        invading_species = max(
                            [s for s in neighbors.keys() if s != current_species and s != 0], 
                            key=lambda s: neighbors[s]
                        )
                        new_grid[y, x] = invading_species
        
        self.grid = new_grid
    
    def set_weather(self, weather):
        """Update the weather state"""
        self.current_weather = weather
    
    def set_pollution_reduction(self, reduction):
        """Set pollution reduction percentage"""
        self.pollution_reduction = reduction
    
    def render(self, screen, cell_size=5):
        # First fill the background with weather color
        background_color = self.weather_colors.get(self.current_weather, (255, 255, 255))
        screen.fill(background_color, (0, 0, self.width * cell_size, self.height * cell_size))
        
        # Then draw the species
        for y in range(self.height):
            for x in range(self.width):
                species = self.grid[y, x]
                if species > 0:  # Only draw non-empty cells
                    color = self.colors[species % len(self.colors)]
                    rect = pygame.Rect(
                        x * cell_size, 
                        y * cell_size, 
                        cell_size, 
                        cell_size
                    )
                    pygame.draw.rect(screen, color, rect)
    
    def count_neighbors(self, x, y):
        """Count the number of neighbors of each species around the given cell"""
        neighbors = {i: 0 for i in range(self.species_count + 1)}  # Include 0 for empty cells
        
        # Check all 8 neighboring cells
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:  # Skip the center cell
                    continue
                    
                # Get neighbor coordinates with wraparound
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                
                # Count the species in this neighbor cell
                neighbor_species = self.grid[ny, nx]
                neighbors[neighbor_species] += 1
                
        return neighbors