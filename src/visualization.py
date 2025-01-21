import numpy as np
import pygame
import random

class InvasionSimulation:
    def __init__(self, width=100, height=100, species_count=5):
        self.width = width
        self.height = height
        self.species_count = species_count
        
        self.grid = np.zeros((height, width), dtype=int)
        
        self.colors = [
            (255, 255, 255),
            (0, 0, 0),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0)
        ]
    
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
                    
                    if species_neighbors < 2 or species_neighbors > 3:
                        new_grid[y, x] = 0
                    
                    other_species_neighbors = total_neighbors - species_neighbors
                    if other_species_neighbors > species_neighbors:
                        invading_species = max(
                            [s for s in neighbors.keys() if s != current_species and s != 0], 
                            key=lambda s: neighbors[s]
                        )
                        new_grid[y, x] = invading_species
        
        self.grid = new_grid
    
    def render(self, screen, cell_size=5):
        for y in range(self.height):
            for x in range(self.width):
                species = self.grid[y, x]
                color = self.colors[species % len(self.colors)]
                rect = pygame.Rect(
                    x * cell_size, 
                    y * cell_size, 
                    cell_size, 
                    cell_size
                )
                pygame.draw.rect(screen, color, rect)