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
        self.pollution_reduction = 0  # Percentage of reduction (0-100)
        self.invasive_species = 2  # Red species (index 2 in colors list)
        
        # Base colors for species (no None value)
        self.colors = [
            (255, 255, 255),  # Default color, will be replaced by weather color
            (0, 0, 0),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0)
        ]
        
        # Weather-specific background colors - more intuitive and natural
        self.weather_colors = {
            "Clear": (255, 252, 245),      # Warm white with slight yellow tint
            "Foggy": (235, 235, 235),      # Light grey
            "Rainy": (235, 245, 255),      # Very light blue
            "Cloudy": (245, 245, 250),     # Light grey with slight blue tint
            "Snowy": (250, 250, 255),      # White with blue tint
            "Windy": (250, 255, 250)       # White with slight green tint
        }
    
    def initialize_random(self, invasion_density=0.2):
        for _ in range(int(self.width * self.height * invasion_density)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            species = random.randint(1, self.species_count)
            self.grid[y, x] = species
    
    def count_neighbors(self, x, y):
        neighbor_counts = {i: 0 for i in range(self.species_count + 1)}
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = (x + dx) % self.width, (y + dy) % self.height
                neighbor_counts[self.grid[ny, nx]] += 1
        
        return neighbor_counts
    
    def update(self):
        new_grid = self.grid.copy()
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                current_species = self.grid[y, x]
                
                if current_species == 0:
                    invading_species = [
                        species for species, count in neighbors.items() 
                        if species != 0 and count >= 3
                    ]
                    if invading_species:
                        new_grid[y, x] = max(set(invading_species), key=invading_species.count)
                else:
                    total_neighbors = sum(neighbors.values())
                    species_neighbors = neighbors[current_species]
                    
                    # Apply pollution reduction effect to invasive species
                    if current_species == self.invasive_species:
                        # Chance to die based on pollution reduction
                        if random.random() < (self.pollution_reduction / 200):  # Divided by 200 to make it more gradual
                            new_grid[y, x] = 0
                            continue
                    
                    if species_neighbors < 2 or species_neighbors > 3:
                        new_grid[y, x] = 0
                    
                    other_species_neighbors = total_neighbors - species_neighbors
                    if other_species_neighbors > species_neighbors:
                        # Reduce invasion probability for invasive species based on pollution reduction
                        if self.invasive_species in neighbors:
                            invasion_chance = 1 - (self.pollution_reduction / 100)
                            if random.random() > invasion_chance:
                                continue
                        
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