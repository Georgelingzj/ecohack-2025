import numpy as np
import pygame
import random

class InvasionSimulation:
    def __init__(self, width=100, height=100, species_count=5):
        """
        Initialize the invasion simulation grid
        
        Args:
            width (int): Width of the grid
            height (int): Height of the grid
            species_count (int): Number of different species to simulate
        """
        self.width = width
        self.height = height
        self.species_count = species_count
        
        # Create a grid with multiple species
        self.grid = np.zeros((height, width), dtype=int)
        
        # Color palette for different species
        self.colors = [
            (255, 255, 255),  # White (empty)
            (0, 0, 0),         # Black (species 1)
            (255, 0, 0),       # Red (species 2)
            (0, 255, 0),       # Green (species 3)
            (0, 0, 255),       # Blue (species 4)
            (255, 255, 0)      # Yellow (species 5)
        ]
    
    def initialize_random(self, invasion_density=0.2):
        """
        Randomly initialize the grid with multiple species
        
        Args:
            invasion_density (float): Percentage of grid to be populated
        """
        for _ in range(int(self.width * self.height * invasion_density)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            species = random.randint(1, self.species_count)
            self.grid[y, x] = species
    
    def count_neighbors(self, x, y):
        """
        Count neighbors and their species for invasion mechanics
        
        Args:
            x (int): x-coordinate
            y (int): y-coordinate
        
        Returns:
            dict: Count of neighbors by species
        """
        neighbor_counts = {i: 0 for i in range(self.species_count + 1)}
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = (x + dx) % self.width, (y + dy) % self.height
                neighbor_counts[self.grid[ny, nx]] += 1
        
        return neighbor_counts
    
    def update(self):
        """
        Update grid based on invasion and survival rules
        """
        new_grid = self.grid.copy()
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                current_species = self.grid[y, x]
                
                # Invasion and survival rules
                if current_species == 0:
                    # Empty cell can be invaded if it has multiple neighbor species
                    invading_species = [
                        species for species, count in neighbors.items() 
                        if species != 0 and count >= 3
                    ]
                    if invading_species:
                        new_grid[y, x] = max(set(invading_species), key=invading_species.count)
                else:
                    # Existing species survival or invasion
                    total_neighbors = sum(neighbors.values())
                    species_neighbors = neighbors[current_species]
                    
                    # Species dies if too few or too many neighbors
                    if species_neighbors < 2 or species_neighbors > 3:
                        new_grid[y, x] = 0
                    
                    # Potential invasion by other species
                    other_species_neighbors = total_neighbors - species_neighbors
                    if other_species_neighbors > species_neighbors:
                        invading_species = max(
                            [s for s in neighbors.keys() if s != current_species and s != 0], 
                            key=lambda s: neighbors[s]
                        )
                        new_grid[y, x] = invading_species
        
        self.grid = new_grid
    
    def render(self, screen, cell_size=5):
        """
        Render the grid on a pygame screen
        
        Args:
            screen (pygame.Surface): Screen to render on
            cell_size (int): Size of each cell in pixels
        """
        for y in range(self.height):
            for x in range(self.width):
                species = self.grid[y, x]
                # Use modulo to ensure we always have a valid color
                color = self.colors[species % len(self.colors)]
                rect = pygame.Rect(
                    x * cell_size, 
                    y * cell_size, 
                    cell_size, 
                    cell_size
                )
                pygame.draw.rect(screen, color, rect)