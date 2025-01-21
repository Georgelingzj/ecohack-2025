import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygame

class DensityPlotter:
    def __init__(self, species_count=3, history_length=100):
        self.species_count = species_count
        self.history_length = history_length
        
        # Initialize history arrays for each species
        self.density_history = {i: np.zeros(history_length) for i in range(1, species_count + 1)}
        self.time_points = np.arange(history_length)
        
        # Create matplotlib figure with fixed size
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(6, 2.5))
        self.fig.set_facecolor('white')
        self.fig.tight_layout(pad=2.0)
        
        # Adjust plot settings for better visibility
        self.ax.set_ylim(0, 100)  # Full percentage range
        self.ax.yaxis.set_major_locator(plt.MultipleLocator(20))  # Major ticks every 20%
        self.ax.yaxis.set_minor_locator(plt.MultipleLocator(5))   # Minor ticks every 5%
        self.ax.grid(True, which='major', alpha=0.3)
        self.ax.grid(True, which='minor', alpha=0.1)
        
        # Species colors (matching visualization colors)
        self.species_colors = {
            1: '#2ecc71',    # Native species (green)
            2: '#e74c3c',    # Invasive species (red)
            3: '#f1c40f'     # Endangered species (yellow)
        }
        
        # Species names for legend
        self.species_names = {
            1: 'Native',
            2: 'Invasive',
            3: 'Endangered'
        }
        
    def update(self, grid):
        """Update density history with new grid state"""
        total_cells = grid.size
        
        # Calculate current densities
        for species in range(1, self.species_count + 1):
            current_density = np.sum(grid == species) / total_cells * 100
            
            # Shift history and add new value
            self.density_history[species] = np.roll(self.density_history[species], -1)
            self.density_history[species][-1] = current_density
    
    def render(self, surface, rect):
        """Render the plot to a pygame surface"""
        self.ax.clear()
        
        # Plot each species
        for species in range(1, self.species_count + 1):
            self.ax.plot(self.time_points, self.density_history[species],
                        color=self.species_colors[species],
                        label=self.species_names[species],
                        linewidth=2)
        
        # Customize plot
        self.ax.set_xlabel('Time', fontsize=8)
        self.ax.set_ylabel('Population %', fontsize=8)
        self.ax.legend(loc='upper right', fontsize=8)
        self.ax.set_title('Species Population Over Time', fontsize=10, pad=8)
        
        # Adjust tick label sizes
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        
        # Convert matplotlib figure to pygame surface
        canvas = FigureCanvasAgg(self.fig)
        canvas.draw()
        
        # Get the RGBA buffer from the figure
        w, h = self.fig.get_size_inches() * self.fig.get_dpi()
        buf = np.frombuffer(canvas.tostring_argb(), dtype=np.uint8)
        buf.shape = int(h), int(w), 4
        
        # Convert ARGB to RGBA
        buf = np.roll(buf, 3, axis=2)
        
        # Create pygame surface
        plot_surface = pygame.image.frombuffer(buf, (int(w), int(h)), "RGBA")
        
        # Scale to fit the rect while maintaining aspect ratio
        scale_factor = min(rect.width / plot_surface.get_width(),
                         rect.height / plot_surface.get_height())
        new_width = int(plot_surface.get_width() * scale_factor)
        new_height = int(plot_surface.get_height() * scale_factor)
        
        # Center the plot in the rect
        x_offset = rect.left + (rect.width - new_width) // 2
        y_offset = rect.top + (rect.height - new_height) // 2
        
        # Scale and position the plot
        plot_surface = pygame.transform.smoothscale(plot_surface, (new_width, new_height))
        surface.blit(plot_surface, (x_offset, y_offset)) 