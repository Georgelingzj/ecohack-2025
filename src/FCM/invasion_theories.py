from enum import Enum
import random
import numpy as np

class InvasionTheory(Enum):
    ENEMY_RELEASE = "enemy_release"
    EVOLUTION_INCREASED_COMPETITIVE = "evolution_increased_competitive"
    NOVEL_WEAPONS = "novel_weapons"
    EMPTY_NICHE = "empty_niche"

class InvasionStrategy:
    def __init__(self, theory_type=InvasionTheory.ENEMY_RELEASE):
        self.theory = theory_type
        self.setup_theory_parameters()
    
    def setup_theory_parameters(self):
        """Set up parameters based on invasion theory"""
        if self.theory == InvasionTheory.ENEMY_RELEASE:
            # Enemy Release Hypothesis: Stronger in new environment due to lack of natural enemies
            self.params = {
                'growth_rate': 0.06,        # Higher growth rate
                'death_rate': 0.01,         # Lower death rate
                'competition_strength': 1.5, # Strong competition with natives
                'env_tolerance': 0.8,       # Good environmental tolerance
                'recovery_rate': 0.04       # Good recovery rate
            }
        
        elif self.theory == InvasionTheory.EVOLUTION_INCREASED_COMPETITIVE:
            # EICA: Evolved to be more competitive
            self.params = {
                'growth_rate': 0.05,        # Moderate growth rate
                'death_rate': 0.02,         # Moderate death rate
                'competition_strength': 2.0, # Very strong competition
                'env_tolerance': 0.6,       # Moderate environmental tolerance
                'recovery_rate': 0.03       # Moderate recovery rate
            }
        
        elif self.theory == InvasionTheory.NOVEL_WEAPONS:
            # Novel Weapons: Has mechanisms that natives aren't adapted to
            self.params = {
                'growth_rate': 0.04,        # Moderate growth rate
                'death_rate': 0.02,         # Moderate death rate
                'competition_strength': 1.8, # Strong competition through allelopathy
                'env_tolerance': 0.7,       # Good environmental tolerance
                'recovery_rate': 0.035      # Moderate recovery rate
            }
        
        elif self.theory == InvasionTheory.EMPTY_NICHE:
            # Empty Niche: Exploits unused resources
            self.params = {
                'growth_rate': 0.07,        # Very high growth rate
                'death_rate': 0.03,         # Higher death rate
                'competition_strength': 1.0, # Lower direct competition
                'env_tolerance': 0.9,       # Very good environmental tolerance
                'recovery_rate': 0.05       # High recovery rate
            }
    
    def modify_growth_rate(self, base_rate, env_conditions):
        """Modify growth rate based on theory and conditions"""
        theory_multiplier = self.params['growth_rate'] / 0.05  # Normalize to base rate
        env_effect = min(1.0, env_conditions['suitability'] * self.params['env_tolerance'])
        return base_rate * theory_multiplier * env_effect
    
    def calculate_competition_effect(self, native_density, invasive_density):
        """Calculate competition effect based on theory"""
        competition_strength = self.params['competition_strength']
        if self.theory == InvasionTheory.NOVEL_WEAPONS:
            # Stronger effect at higher invasive densities
            return competition_strength * (1 + invasive_density)
        elif self.theory == InvasionTheory.EMPTY_NICHE:
            # Less affected by native density
            return competition_strength * (0.5 + 0.5 * native_density)
        else:
            # Standard competition
            return competition_strength * native_density 