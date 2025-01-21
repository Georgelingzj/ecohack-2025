import numpy as np

class InvasionSimulation:
    def __init__(self, width=100, height=100, species_count=5):
        """
        Initialize the invasion simulation grid
        
        :param width: Width of the grid
        :param height: Height of the grid
        :param species_count: Number of unique species
        """
        self.width = width
        self.height = height
        self.species_count = species_count
        
        # Initialize grid with mostly empty spaces and some species clusters
        self.grid = np.zeros((height, width), dtype=int)
        self._create_initial_clusters()
        
        # Movement and interaction parameters
        self.reproduction_rate = 0.15
        self.movement_rate = 0.3
        self.death_rate = 0.05

    def _create_initial_clusters(self):
        """Create initial species clusters instead of random distribution"""
        clusters_per_species = 3
        cluster_size = 5
        
        for species in range(1, self.species_count + 1):
            for _ in range(clusters_per_species):
                # Random center point for cluster
                center_x = np.random.randint(cluster_size, self.width - cluster_size)
                center_y = np.random.randint(cluster_size, self.height - cluster_size)
                
                # Create cluster around center point
                for dx in range(-cluster_size // 2, cluster_size // 2 + 1):
                    for dy in range(-cluster_size // 2, cluster_size // 2 + 1):
                        if np.random.random() < 0.7:  # 70% chance to place species
                            x, y = center_x + dx, center_y + dy
                            if 0 <= x < self.width and 0 <= y < self.height:
                                self.grid[y, x] = species

    def update(self):
        """
        Enhanced update method with more visible species behavior
        """
        new_grid = self.grid.copy()
        
        for y in range(self.height):
            for x in range(self.width):
                species = self.grid[y, x]
                if species > 0:  # If cell contains a species
                    # Movement
                    if np.random.random() < self.movement_rate:
                        dx = np.random.randint(-2, 3)  # Larger movement range
                        dy = np.random.randint(-2, 3)
                        new_x, new_y = x + dx, y + dy
                        
                        if 0 <= new_x < self.width and 0 <= new_y < self.height:
                            # Move to empty space or interact with other species
                            if new_grid[new_y, new_x] == 0:
                                new_grid[new_y, new_x] = species
                                new_grid[y, x] = 0
                            elif new_grid[new_y, new_x] != species:
                                # Species interaction - stronger species wins
                                if np.random.random() < 0.5:
                                    new_grid[new_y, new_x] = species
                    
                    # Reproduction
                    if np.random.random() < self.reproduction_rate:
                        # Try to reproduce in adjacent cells
                        for _ in range(4):  # Check up to 4 adjacent cells
                            dx = np.random.randint(-1, 2)
                            dy = np.random.randint(-1, 2)
                            new_x, new_y = x + dx, y + dy
                            
                            if (0 <= new_x < self.width and 
                                0 <= new_y < self.height and 
                                new_grid[new_y, new_x] == 0):
                                new_grid[new_y, new_x] = species
                                break
                    
                    # Death
                    if np.random.random() < self.death_rate:
                        new_grid[y, x] = 0

        self.grid = new_grid


class Environment:
    def __init__(self):
        self.energy = 100  # Available energy units
        self.nutrients = 100  # Nutrient levels
        self.pollution = 0  # Pollution index (0-100)
        self.deforestation = 0  # Deforestation percentage (0-100)
        self.climate_change = 0  # Climate change impact (0-100)

    def update(self, player_decisions, species_activity):
        # Update environmental factors based on player decisions
        self.pollution += player_decisions.get("pollution", 0)
        self.deforestation += player_decisions.get("deforestation", 0)
        self.climate_change += self.pollution * 0.01

        # Simulate impact of species activity on resources
        active_species = species_activity.get("active_species", 0)
        self.energy = max(0, self.energy - active_species * 0.1)
        self.nutrients = max(0, self.nutrients - active_species * 0.2)

        # Clamp values
        self.pollution = min(100, self.pollution)
        self.deforestation = min(100, self.deforestation)
        self.climate_change = min(100, self.climate_change)


class InvasionSimulationWithEnvironment(InvasionSimulation):
    def __init__(self, width=100, height=100, species_count=5):
        super().__init__(width, height, species_count)
        self.environment = Environment()
        self.history = []

    def update(self, player_decisions=None):
        player_decisions = player_decisions or {}
        species_activity = {"active_species": np.sum(self.grid > 0)}

        # Update environment
        self.environment.update(player_decisions, species_activity)

        # Run invasion simulation
        super().update()

        # Log history
        self.history.append({
            "grid": self.grid.copy(),
            "environment": vars(self.environment),
        })

    def summarize(self):
        biodiversity = len(np.unique(self.grid)) - 1  # Exclude empty cells
        avg_pollution = np.mean([entry["environment"]["pollution"] for entry in self.history])
        return {
            "biodiversity": biodiversity,
            "avg_pollution": avg_pollution,
            "total_energy": self.environment.energy,
        }
