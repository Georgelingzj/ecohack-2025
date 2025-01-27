import matplotlib
matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
import pygame

class DensityPlotter:
    def __init__(self, species_count=3, history_length=100):
        self.species_count = species_count
        self.history_length = history_length
        self.densities = {i: [] for i in range(1, species_count + 1)}
        
        # Enhance plot styling
        plt.style.use('default')  # Use default style for better visibility
        self.dpi = 100
        self.fig = plt.figure(figsize=(7, 3), dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        self.fig.set_facecolor('white')
        self.ax.set_facecolor('#f0f0f0')  # Light gray background
        
        # Configure axes with grid
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel('Time (steps)', fontsize=8)
        self.ax.set_ylabel('Population (%)', fontsize=8)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.tick_params(labelsize=8)
        
        # Enhanced line styles
        self.colors = ['#2ecc71', '#e74c3c', '#f1c40f']  # Prettier colors
        self.line_styles = ['-', '-', '-']
        self.line_widths = [2, 2, 2]
        self.labels = ['Native', 'Invasive', 'Endangered']
        
        # Initialize lines with better styling
        self.lines = []
        for i in range(species_count):
            line = self.ax.plot([], [], 
                              self.colors[i],
                              self.line_styles[i],
                              linewidth=self.line_widths[i],
                              label=self.labels[i])[0]  # Get first element of returned tuple
            self.lines.append(line)
        
        # Enhanced legend
        self.ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
        
        # Ensure tight layout
        self.fig.tight_layout()
    
    def update(self, grid):
        """Update density history with new grid state"""
        total_cells = grid.size
        
        # Calculate current densities
        for species in range(1, self.species_count + 1):
            density = np.sum(grid == species) / total_cells * 100
            self.densities[species].append(density)
            
            # Trim history if too long
            if len(self.densities[species]) > self.history_length:
                self.densities[species] = self.densities[species][-self.history_length:]
        
        # Update plot lines
        for i, species in enumerate(range(1, self.species_count + 1)):
            self.lines[i].set_data(range(len(self.densities[species])), 
                                 self.densities[species])
        
        # Adjust x-axis limits
        self.ax.set_xlim(0, self.history_length)
    
    def render(self, screen, rect):
        """Render the plot to the pygame surface"""
        # Draw the plot
        self.fig.canvas.draw()
        
        # Get the RGBA buffer from the figure
        buf = np.asarray(self.fig.canvas.buffer_rgba())
        
        # Convert RGBA to RGB
        rgb_buf = buf[:, :, :3]
        
        # Create pygame surface
        plot_surface = pygame.surfarray.make_surface(rgb_buf.swapaxes(0, 1))
        
        # Scale to fit the rect
        plot_surface = pygame.transform.scale(plot_surface, (rect.width, rect.height))
        
        # Draw background
        pygame.draw.rect(screen, (255, 255, 255), rect)
        
        # Blit plot to screen
        screen.blit(plot_surface, rect) 