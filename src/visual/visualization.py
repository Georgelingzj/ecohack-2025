import numpy as np
import pygame
import random
import math
from ..FCM.invasion_theories import InvasionStrategy, InvasionTheory

class InvasionSimulation:
    def __init__(self, width=100, height=100, density_plotter=None, 
                 invasion_theory=InvasionTheory.ENEMY_RELEASE):
        self.width = width
        self.height = height
        self.species_count = 3  # Now 3 species: native, invasive, endangered
        self.grid = np.zeros((height, width), dtype=int)
        self.current_weather = "Clear"
        
        # Environmental parameters
        self.pollution_reduction = 0
        self.temperature = 20  # Default 20°C (changed from 50)
        self.humidity = 50     # 0=dry, 100=wet
        
        # Growth and death rates (to be replaced by API data in future)
        self.growth_rates = {
            1: 0.02,  # Native species: slow growth
            2: 0.05,  # Invasive species: faster growth
            3: 0.01   # Endangered species: very slow growth
        }
        self.death_rates = {
            1: 0.01,  # Native species: normal death rate
            2: 0.01,  # Invasive species: normal death rate
            3: 0.02   # Endangered species: higher base death rate
        }
        
        # Growth control parameters
        self.initial_density = 0.2  # Lower initial density
        self.base_neighbors_required = 3
        self.survival_min = 2 
        self.survival_max = 3
        self.invasion_threshold = 1.0
        
        # Colors: 0=empty, 1=native (green), 2=invasive (red), 3=endangered (yellow)
        self.colors = [
            (255, 255, 255),              # Empty
            (46, 204, 113),               # Native species (green)
            (231, 76, 60),                # Invasive species (red)
            (241, 196, 15)                # Endangered species (yellow)
        ]
        
        # Track endangered species population history
        self.endangered_history = []
        self.last_endangered_percentage = 0
        
        # Track invasive species
        self.invasive_species = 2  # Red species
        
        # Initialize invasion strength
        self.invasion_strength = {
            1: 0.3,  # Native species
            2: 0.4   # Invasive species
        }
        
        # Initialize survival parameters with realistic temperatures
        self.temp_survival = {
            1: (5, 35),    # Native species - adaptable
            2: (15, 30),   # Invasive species - moderate range
            3: (18, 25)    # Endangered species - very narrow range
        }
        
        self.humidity_survival = {
            1: (20, 90),   # Native species - adaptable
            2: (40, 70),   # Invasive species - moderate range
            3: (45, 65)    # Endangered species - very narrow range
        }
        
        # Initialize environmental effects
        self.calculate_growth_parameters()
        
        # Restore weather colors
        self.weather_colors = {
            "Clear": (245, 245, 245),    # Very light gray
            "Foggy": (230, 230, 230),    # Light gray
            "Rainy": (235, 240, 245),    # Very light blue-gray
            "Cloudy": (240, 240, 240),   # Light gray
            "Snowy": (250, 250, 252),    # Almost white
            "Windy": (242, 245, 242)     # Very light green-gray
        }
        
        # Add game state tracking
        self.game_over = False
        self.victory_condition_met = False
        
        # Define optimal living conditions for each species
        self.optimal_conditions = {
            1: {'temperature': (15, 30), 'humidity': (30, 70)},  # Native species
            2: {'temperature': (15, 30), 'humidity': (40, 70)},  # Invasive species
            3: {'temperature': (18, 25), 'humidity': (45, 65)}   # Endangered species
        }
        
        # Initialize density plotter
        self.density_plotter = density_plotter
        
        # Add minimum population thresholds
        self.min_population_threshold = {
            1: 0.05,  # Native species minimum 5%
            2: 0.02,  # Invasive species minimum 2%
            3: 0.01   # Endangered species minimum 1%
        }
        
        # Add recovery rates when conditions are favorable
        self.recovery_rates = {
            1: 0.03,  # Native species recovery rate
            2: 0.04,  # Invasive species recovery rate
            3: 0.02   # Endangered species recovery rate
        }
        
        # Initialize invasion strategy
        self.invasion_strategy = InvasionStrategy(invasion_theory)
        
        # Update growth rates based on theory
        self.growth_rates[2] = self.invasion_strategy.params['growth_rate']
        self.death_rates[2] = self.invasion_strategy.params['death_rate']
    
    def update_environmental_parameters(self, pollution=None, temperature=None, humidity=None):
        """Update environmental parameters and their effects on growth"""
        if pollution is not None:
            self.pollution_reduction = max(0, min(100, pollution))
        if temperature is not None:
            self.temperature = max(0, min(100, temperature))
        if humidity is not None:
            self.humidity = max(0, min(100, humidity))
            
        # Calculate environmental effects
        self.calculate_growth_parameters()

    def calculate_growth_parameters(self):
        """Calculate growth parameters based on environmental conditions"""
        # Temperature stress (based on realistic temperature range)
        temp_stress = 0
        if self.temperature < 15 or self.temperature > 30:
            temp_stress = min(abs(self.temperature - 15), abs(self.temperature - 30)) / 10
        
        # Humidity stress
        humidity_stress = abs(self.humidity - 50) / 100  # Normalize humidity stress
        
        # Combined environmental pressure
        env_pressure = (temp_stress + humidity_stress) / 2  # Normalize to 0-1 range
        
        # Base growth rates with more resilience
        self.growth_rates = {
            1: max(0.02, 0.04 - env_pressure * 0.03),  # Native species
            2: max(0.03, 0.05 - env_pressure * 0.02),  # Invasive species (more resilient)
            3: max(0.01, 0.03 - env_pressure * 0.04)   # Endangered species (more sensitive)
        }
        
        # Adjust death rates based on conditions
        self.death_rates = {
            1: min(0.02, 0.01 + env_pressure * 0.02),  # Native species
            2: min(0.015, 0.01 + env_pressure * 0.01), # Invasive species (more resilient)
            3: min(0.03, 0.02 + env_pressure * 0.03)   # Endangered species (more sensitive)
        }

    def initialize_random(self):
        """Initialize with realistic starting populations"""
        self.grid.fill(0)
        
        # Start with more native species (50%)
        cells_for_native = int(self.width * self.height * 0.5)
        for _ in range(cells_for_native):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.grid[y, x] = 1
        
        # Fewer invasive species (20%)
        cells_for_invasive = int(self.width * self.height * 0.2)
        for _ in range(cells_for_invasive):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y, x] == 0:  # Only place if cell is empty
                self.grid[y, x] = 2
        
        # Very few endangered species (5%)
        cells_for_endangered = int(self.width * self.height * 0.05)
        for _ in range(cells_for_endangered):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y, x] == 0:  # Only place if cell is empty
                self.grid[y, x] = 3

    def update(self):
        """Update with modified growth dynamics and recovery mechanism"""
        new_grid = self.grid.copy()
        
        # Calculate current densities
        total_cells = self.grid.size
        densities = {
            species: (np.sum(self.grid == species) / total_cells)
            for species in range(1, self.species_count + 1)
        }
        
        # Calculate competition pressure from invasive species
        invasive_pressure = self.invasion_strategy.calculate_competition_effect(
            native_density=densities[1],
            invasive_density=densities[2]
        )
        
        # Update each cell based on environmental conditions
        for y in range(self.height):
            for x in range(self.width):
                current_species = self.grid[y, x]
                
                if current_species == 0:  # Empty cell
                    # Calculate growth probabilities based on environmental conditions
                    growth_probs = self.calculate_growth_probabilities(x, y, densities)
                    
                    # Apply growth based on probabilities
                    rand_val = random.random()
                    cumulative_prob = 0
                    for species, prob in growth_probs.items():
                        cumulative_prob += prob
                        if rand_val < cumulative_prob:
                            new_grid[y, x] = species
                            break
                            
                else:  # Occupied cell
                    # Calculate death probability based on conditions
                    death_prob = self.calculate_death_chance(current_species)
                    
                    # Apply environmental stress
                    if not self.check_favorable_conditions(current_species):
                        death_prob *= 1.5
                    
                    # Apply competition pressure for native species
                    if current_species == 1:  # Native species
                        death_prob *= (1 + invasive_pressure)
                    
                    if random.random() < death_prob:
                        new_grid[y, x] = 0
        
        # Apply recovery mechanism
        self.apply_recovery_mechanism(new_grid, densities)
        
        self.grid = new_grid
        
        # Update the density plotter if available
        if self.density_plotter:
            self.density_plotter.update(self.grid)
    
    def calculate_growth_probabilities(self, x, y, densities):
        """Calculate growth probabilities for each species based on conditions"""
        probs = {}
        for species in range(1, self.species_count + 1):
            base_rate = self.growth_rates[species]
            neighbor_factor = self.count_neighbors(x, y, species) / 8.0
            
            # Adjust based on environmental conditions
            env_factor = 1.0
            if self.check_favorable_conditions(species):
                env_factor = 1.2
            else:
                env_factor = 0.8
            
            probs[species] = base_rate * neighbor_factor * env_factor
        
        return probs

    def set_weather(self, weather):
        """Update the weather state"""
        self.current_weather = weather
    
    def set_pollution_reduction(self, reduction):
        """Set pollution reduction percentage (0-100)"""
        self.update_environmental_parameters(pollution=reduction)
    
    def set_temperature(self, degrees):
        """Set temperature in degrees (0-40)"""
        self.temperature = max(0, min(40, degrees))
        self.calculate_growth_parameters()
    
    def set_humidity(self, percentage):
        """Set humidity percentage (0-100)"""
        self.humidity = max(0, min(100, percentage))
        self.calculate_growth_parameters()
    
    def set_environment(self, pollution=None, temperature=None, humidity=None):
        """Set multiple environmental parameters at once"""
        self.update_environmental_parameters(
            pollution=pollution,
            temperature=temperature,
            humidity=humidity
        )
    
    def set_growth_parameters(self, initial_density=None, base_neighbors=None, 
                            survival_min=None, survival_max=None, 
                            invasion_threshold=None):
        """Update growth control parameters"""
        if initial_density is not None:
            self.initial_density = max(0.0, min(1.0, initial_density))
        if base_neighbors is not None:
            self.base_neighbors_required = max(1, int(base_neighbors))
        if survival_min is not None:
            self.survival_min = max(0, int(survival_min))
        if survival_max is not None:
            self.survival_max = max(self.survival_min, int(survival_max))
        if invasion_threshold is not None:
            self.invasion_threshold = max(0.0, float(invasion_threshold))
    
    def render(self, screen, cell_size=5):
        """Render the environment with improved visuals"""
        # Create a surface for the environment
        env_surface = pygame.Surface((self.width * cell_size, self.height * cell_size))
        
        # Fill with white background
        env_surface.fill((255, 255, 255))
        
        # Draw grid lines (subtle)
        grid_color = (240, 240, 240)  # Very light gray
        for x in range(0, self.width * cell_size, cell_size):
            pygame.draw.line(env_surface, grid_color, (x, 0), (x, self.height * cell_size))
        for y in range(0, self.height * cell_size, cell_size):
            pygame.draw.line(env_surface, grid_color, (0, y), (self.width * cell_size, y))
        
        # Draw species with rounded corners and padding
        padding = 1  # Pixels of padding within each cell
        for y in range(self.height):
            for x in range(self.width):
                species = self.grid[y, x]
                if species > 0:  # Only draw non-empty cells
                    color = self.colors[species]
                    rect = pygame.Rect(
                        x * cell_size + padding,
                        y * cell_size + padding,
                        cell_size - padding * 2,
                        cell_size - padding * 2
                    )
                    pygame.draw.rect(env_surface, color, rect, border_radius=2)
        
        return env_surface
    
    def count_neighbors(self, x, y, species):
        """Count the number of neighbors of a specific species around the given cell"""
        neighbors = 0
        
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
                if neighbor_species == species:
                    neighbors += 1
                
        return neighbors

    def check_victory_condition(self):
        """Check if victory conditions are met"""
        total_cells = self.grid.size
        invasive_density = np.sum(self.grid == 2) / total_cells * 100
        total_density = (np.sum(self.grid == 1) + np.sum(self.grid == 2)) / total_cells * 100
        
        # Victory when invasive species reduced to 10% and total density above 10%
        if invasive_density <= 10 and total_density >= 10:
            self.victory_condition_met = True
            return True
        return False
    
    def check_game_over(self):
        """Check if game over conditions are met"""
        total_cells = self.grid.size
        total_density = (np.sum(self.grid == 1) + np.sum(self.grid == 2)) / total_cells * 100
        
        # Game over if total density falls below 5%
        if total_density < 5:
            self.game_over = True
            return True
        return False

    def calculate_death_chance(self, species):
        """Calculate death chance based on environmental conditions"""
        base_rate = self.death_rates[species]
        
        # Environmental stress factors
        temp_stress = self.calculate_temperature_stress(species)
        humidity_stress = self.calculate_humidity_stress(species)
        pollution_stress = self.pollution_reduction / 200  # Reduced effect
        
        # Endangered species more sensitive to all stresses
        if species == 3:
            temp_stress *= 2
            humidity_stress *= 2
            pollution_stress *= 0.5  # But benefits more from pollution reduction
        
        return base_rate + temp_stress + humidity_stress - pollution_stress

    def get_endangered_status(self):
        """Get status message for endangered species"""
        if not self.endangered_history:
            return "Monitoring endangered species..."
        
        current = self.endangered_history[-1]
        previous = self.endangered_history[0] if len(self.endangered_history) > 1 else current
        
        if current < 2:
            return "WARNING: Endangered species critical!"
        elif current < previous:
            return f"Alert: Endangered species declining ({current:.1f}%)"
        elif current > previous:
            return f"Good: Endangered species recovering ({current:.1f}%)"
        else:
            return f"Stable: Endangered species at {current:.1f}%"

    def calculate_temperature_stress(self, species):
        """Calculate temperature stress for a species"""
        temp_min, temp_max = self.temp_survival[species]
        
        if self.temperature < temp_min:
            return (temp_min - self.temperature) / temp_min
        elif self.temperature > temp_max:
            return (self.temperature - temp_max) / (40 - temp_max)
        return 0.0

    def calculate_humidity_stress(self, species):
        """Calculate humidity stress for a species"""
        humid_min, humid_max = self.humidity_survival[species]
        
        if self.humidity < humid_min:
            return (humid_min - self.humidity) / humid_min
        elif self.humidity > humid_max:
            return (self.humidity - humid_max) / (100 - humid_max)
        return 0.0

    def check_favorable_conditions(self, species):
        """Check if conditions are favorable for species recovery"""
        temp_min, temp_max = self.temp_survival[species]
        humid_min, humid_max = self.humidity_survival[species]
        
        # More lenient temperature conditions for recovery
        temp_range = temp_max - temp_min
        temp_tolerance = temp_range * 0.2  # 20% tolerance
        temp_favorable = (temp_min - temp_tolerance <= self.temperature <= temp_max + temp_tolerance)
        
        # More lenient humidity conditions
        humid_range = humid_max - humid_min
        humid_tolerance = humid_range * 0.2  # 20% tolerance
        humid_favorable = (humid_min - humid_tolerance <= self.humidity <= humid_max + humid_tolerance)
        
        # Pollution threshold depends on species
        if species == 2:  # Invasive species
            pollution_favorable = True  # Invasive species less affected by pollution
        else:
            pollution_favorable = self.pollution_reduction >= 30  # Lower threshold for recovery
        
        return temp_favorable and humid_favorable and pollution_favorable

    def apply_recovery_mechanism(self, new_grid, densities):
        """Apply recovery mechanism based on densities"""
        total_cells = self.grid.size
        for species in range(1, self.species_count + 1):
            if densities[species] < self.min_population_threshold[species]:
                if self.check_favorable_conditions(species):
                    empty_cells = np.where(self.grid == 0)
                    if len(empty_cells[0]) > 0:
                        recovery_count = int(self.recovery_rates[species] * total_cells)
                        recovery_count = max(recovery_count, int(0.02 * total_cells))
                        
                        for _ in range(min(recovery_count, len(empty_cells[0]))):
                            idx = random.randint(0, len(empty_cells[0]) - 1)
                            y, x = empty_cells[0][idx], empty_cells[1][idx]
                            new_grid[y, x] = species

class FCMVisualizer:
    def __init__(self):
        # Adjust node positions for better spacing
        self.nodes = {
            "Temperature": {"pos": (80, 80), "value": 20},
            "Humidity": {"pos": (80, 200), "value": 50},
            "Pollution": {"pos": (80, 320), "value": 0},
            "Native": {"pos": (250, 140), "value": 50},
            "Invasive": {"pos": (250, 260), "value": 20},
            "Endangered": {"pos": (350, 200), "value": 5}
        }
        
        # Define edges and their weights
        self.edges = [
            ("Temperature", "Native", 0.6),
            ("Temperature", "Invasive", 0.8),
            ("Temperature", "Endangered", 0.3),
            ("Humidity", "Native", 0.4),
            ("Humidity", "Invasive", 0.6),
            ("Humidity", "Endangered", 0.7),
            ("Pollution", "Native", -0.8),
            ("Pollution", "Invasive", -0.3),
            ("Pollution", "Endangered", -0.9)
        ]
        
        # Node colors
        self.colors = {
            "Temperature": (255, 128, 0),  # Orange
            "Humidity": (0, 128, 255),     # Blue
            "Pollution": (128, 128, 128),  # Gray
            "Native": (46, 204, 113),      # Green
            "Invasive": (231, 76, 60),     # Red
            "Endangered": (241, 196, 15)   # Yellow
        }
    
    def update_values(self, environment):
        """Update node values based on environment state"""
        self.nodes["Temperature"]["value"] = environment.temperature
        self.nodes["Humidity"]["value"] = environment.humidity
        self.nodes["Pollution"]["value"] = environment.pollution_reduction
        
        # Calculate species densities
        total_cells = environment.grid.size
        self.nodes["Native"]["value"] = np.sum(environment.grid == 1) / total_cells * 100
        self.nodes["Invasive"]["value"] = np.sum(environment.grid == 2) / total_cells * 100
        self.nodes["Endangered"]["value"] = np.sum(environment.grid == 3) / total_cells * 100
    
    def render(self, surface, rect):
        """Render the FCM graph"""
        # Create subsurface for FCM
        fcm_surface = pygame.Surface((rect.width, rect.height))
        fcm_surface.fill((255, 255, 255))
        
        # Draw edges first
        for start, end, weight in self.edges:
            start_pos = self.nodes[start]["pos"]
            end_pos = self.nodes[end]["pos"]
            
            # Calculate color based on weight
            if weight > 0:
                color = (0, int(255 * weight), 0)  # Green for positive
            else:
                color = (int(255 * -weight), 0, 0)  # Red for negative
            
            # Draw arrow
            pygame.draw.line(fcm_surface, color, start_pos, end_pos, 2)
            
            # Draw arrowhead
            angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
            arrow_size = 10
            arrow_points = [
                end_pos,
                (end_pos[0] - arrow_size * math.cos(angle + math.pi/6),
                 end_pos[1] - arrow_size * math.sin(angle + math.pi/6)),
                (end_pos[0] - arrow_size * math.cos(angle - math.pi/6),
                 end_pos[1] - arrow_size * math.sin(angle - math.pi/6))
            ]
            pygame.draw.polygon(fcm_surface, color, arrow_points)
        
        # Draw nodes
        for name, data in self.nodes.items():
            pos = data["pos"]
            value = data["value"]
            color = self.colors[name]
            
            # Draw node circle
            pygame.draw.circle(fcm_surface, color, pos, 15)  # Reduced circle size
            
            # Draw node label with offset
            font = pygame.font.SysFont(None, 18)  # Smaller font
            label = font.render(f"{name}: {value:.1f}", True, (0, 0, 0))
            label_pos = (pos[0] - label.get_width()//2, pos[1] + 20)
            fcm_surface.blit(label, label_pos)
        
        # Blit FCM surface to main surface
        surface.blit(fcm_surface, rect)

class EcologicalFCM:
    def __init__(self):
        self.nodes = {
            "Resource\nCompetition": {"pos": (80, 80), "value": 0.5},
            "Predation": {"pos": (250, 80), "value": 0.3},
            "Habitat\nModification": {"pos": (350, 80), "value": 0.6},
            "Native\nBiodiversity": {"pos": (80, 200), "value": 0.7},
            "Ecosystem\nStability": {"pos": (250, 200), "value": 0.8},
            "Invasive\nDominance": {"pos": (350, 200), "value": 0.4}
        }
        
        # Define ecological relationships
        self.edges = [
            ("Resource\nCompetition", "Native\nBiodiversity", -0.7),
            ("Resource\nCompetition", "Invasive\nDominance", 0.8),
            ("Predation", "Ecosystem\nStability", -0.5),
            ("Predation", "Native\nBiodiversity", -0.6),
            ("Habitat\nModification", "Ecosystem\nStability", -0.8),
            ("Habitat\nModification", "Invasive\nDominance", 0.7),
            ("Native\nBiodiversity", "Ecosystem\nStability", 0.9),
            ("Ecosystem\nStability", "Invasive\nDominance", -0.6),
            ("Invasive\nDominance", "Native\nBiodiversity", -0.8)
        ]
        
        # Node colors
        self.colors = {
            "Resource\nCompetition": (255, 165, 0),     # Orange
            "Predation": (255, 69, 0),                  # Red-Orange
            "Habitat\nModification": (106, 90, 205),    # Slate Blue
            "Native\nBiodiversity": (46, 204, 113),     # Green
            "Ecosystem\nStability": (52, 152, 219),     # Blue
            "Invasive\nDominance": (231, 76, 60)        # Red
        }
    
    def update_values(self, environment):
        """Update node values based on current simulation state"""
        total_cells = environment.grid.size
        native_density = np.sum(environment.grid == 1) / total_cells
        invasive_density = np.sum(environment.grid == 2) / total_cells
        
        # Update node values based on simulation state
        self.nodes["Resource\nCompetition"]["value"] = min(1.0, native_density + invasive_density)
        self.nodes["Invasive\nDominance"]["value"] = invasive_density
        self.nodes["Native\nBiodiversity"]["value"] = native_density
        self.nodes["Ecosystem\nStability"]["value"] = max(0, 1 - abs(native_density - invasive_density))
    
    def render(self, surface, rect):
        """Render the ecological FCM graph"""
        # Create subsurface for FCM
        fcm_surface = pygame.Surface((rect.width, rect.height))
        fcm_surface.fill((255, 255, 255))
        
        # Draw edges with arrows
        for start, end, weight in self.edges:
            start_pos = self.nodes[start]["pos"]
            end_pos = self.nodes[end]["pos"]
            
            # Calculate color based on weight
            if weight > 0:
                color = (0, int(255 * abs(weight)), 0)  # Green for positive
            else:
                color = (int(255 * abs(weight)), 0, 0)  # Red for negative
            
            # Draw arrow with curve
            control_point = (
                (start_pos[0] + end_pos[0]) // 2,
                (start_pos[1] + end_pos[1]) // 2 - 20
            )
            
            # Draw curved line
            points = [start_pos, control_point, end_pos]
            pygame.draw.lines(fcm_surface, color, False, points, 2)
            
            # Draw arrowhead
            angle = math.atan2(end_pos[1] - control_point[1], 
                             end_pos[0] - control_point[0])
            arrow_size = 10
            arrow_points = [
                end_pos,
                (end_pos[0] - arrow_size * math.cos(angle + math.pi/6),
                 end_pos[1] - arrow_size * math.sin(angle + math.pi/6)),
                (end_pos[0] - arrow_size * math.cos(angle - math.pi/6),
                 end_pos[1] - arrow_size * math.sin(angle - math.pi/6))
            ]
            pygame.draw.polygon(fcm_surface, color, arrow_points)
        
        # Draw nodes
        for name, data in self.nodes.items():
            pos = data["pos"]
            value = data["value"]
            color = self.colors[name]
            
            # Draw node circle with size based on value
            radius = int(15 + value * 10)
            pygame.draw.circle(fcm_surface, color, pos, radius)
            
            # Draw node label
            font = pygame.font.SysFont(None, 16)
            for i, line in enumerate(name.split('\n')):
                label = font.render(line, True, (0, 0, 0))
                label_pos = (pos[0] - label.get_width()//2, 
                           pos[1] - 10 + i*15)
                fcm_surface.blit(label, label_pos)
            
            # Draw value
            value_label = font.render(f"{value:.2f}", True, (0, 0, 0))
            value_pos = (pos[0] - value_label.get_width()//2, pos[1] + 20)
            fcm_surface.blit(value_label, value_pos)
        
        # Blit FCM surface to main surface
        surface.blit(fcm_surface, rect)