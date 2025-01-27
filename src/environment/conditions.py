import random
from datetime import datetime, timedelta
import pygame

class GameConditions:
    def __init__(self):
        """
        Initialize game conditions with simulation-based time and environmental parameters.
        """
        # Simulation time tracking
        self.year = 2025
        self.month = 1  # 1-12
        self.week = 1   # 1-4
        self.weather_conditions = ["Clear", "Cloudy", "Rainy", "Foggy", "Snowy", "Windy"]
        self.current_weather = "Clear"
        
        # Season temperature ranges (min, max)
        self.seasonal_temps = {
            "Winter": (0, 10),    # Dec-Feb
            "Spring": (10, 25),   # Mar-May
            "Summer": (20, 35),   # Jun-Aug
            "Fall": (10, 20)      # Sep-Nov
        }
        
        # Season humidity ranges (min, max)
        self.seasonal_humidity = {
            "Winter": (30, 50),   # Drier in winter
            "Spring": (50, 70),   # Moderate humidity
            "Summer": (60, 80),   # More humid
            "Fall": (40, 60)      # Moderate humidity
        }
        
        # Weather-specific modifiers
        self.weather_modifiers = {
            "Clear": {"temp": 2, "humidity": -10},
            "Cloudy": {"temp": 0, "humidity": 0},
            "Rainy": {"temp": -2, "humidity": 20},
            "Foggy": {"temp": -1, "humidity": 15},
            "Snowy": {"temp": -5, "humidity": 5},
            "Windy": {"temp": -3, "humidity": -15}
        }
        
        # Add current state tracking
        self.current_temperature = None
        self.current_humidity = None
        self.last_update_time = 0
        self.update_interval = 1000  # Update every second
        self.weather_change_probability = 0.15  # 15% chance per update
        
        # Add temperature and humidity change rates
        self.temp_change_rate = 0.2  # Faster temperature changes
        self.humid_change_rate = 0.3  # Faster humidity changes
        
        # Initialize current conditions
        self._initialize_conditions()
    
    def _initialize_conditions(self):
        """Initialize starting conditions"""
        season = self.get_season()
        temp_range = self.seasonal_temps[season]
        humid_range = self.seasonal_humidity[season]
        
        self.current_temperature = sum(temp_range) / 2
        self.current_humidity = sum(humid_range) / 2
        self.update_weather()
    
    def get_season(self):
        if self.month in [12, 1, 2]:
            return "Winter"
        elif self.month in [3, 4, 5]:
            return "Spring"
        elif self.month in [6, 7, 8]:
            return "Summer"
        else:
            return "Fall"
    
    def update(self):
        """Update game conditions"""
        current_time = pygame.time.get_ticks()
        
        # Update time
        self.week += 1
        if self.week > 4:
            self.week = 1
            self.month += 1
            
        if self.month > 12:
            self.month = 1
            self.year += 1
        
        # Update environmental conditions more frequently
        if current_time - self.last_update_time > self.update_interval:
            self._update_environmental_conditions()
            self.last_update_time = current_time
            
            # Update weather with some probability
            if random.random() < self.weather_change_probability:  # 15% chance to change weather
                self.update_weather()
    
    def _update_environmental_conditions(self):
        """Update temperature and humidity gradually"""
        season = self.get_season()
        temp_range = self.seasonal_temps[season]
        humid_range = self.seasonal_humidity[season]
        
        # Calculate target values based on season and current weather
        weather_mod = self.weather_modifiers[self.current_weather]
        target_temp = random.uniform(temp_range[0], temp_range[1]) + weather_mod["temp"]
        target_humidity = random.uniform(humid_range[0], humid_range[1]) + weather_mod["humidity"]
        
        # Gradually move current values toward target values with faster changes
        temp_change = (target_temp - self.current_temperature) * self.temp_change_rate
        humid_change = (target_humidity - self.current_humidity) * self.humid_change_rate
        
        # Apply changes with more significant randomness
        self.current_temperature += temp_change + random.uniform(-1.0, 1.0)
        self.current_humidity += humid_change + random.uniform(-2.0, 2.0)
        
        # Ensure values stay within reasonable ranges
        self.current_temperature = max(0, min(40, self.current_temperature))
        self.current_humidity = max(0, min(100, self.current_humidity))
    
    def update_weather(self):
        """Update weather based on season and random factors"""
        season = self.get_season()
        
        # Determine possible weather conditions based on season
        if season == "Winter":
            weights = [0.2, 0.3, 0.1, 0.1, 0.2, 0.1]  # More cloudy and snowy
        elif season == "Summer":
            weights = [0.4, 0.2, 0.2, 0.05, 0, 0.15]  # More clear and rainy
        elif season == "Spring":
            weights = [0.3, 0.2, 0.3, 0.1, 0, 0.1]    # More rainy
        else:  # Fall
            weights = [0.2, 0.3, 0.2, 0.15, 0, 0.15]  # More cloudy and foggy
        
        self.current_weather = random.choices(
            self.weather_conditions, 
            weights=weights,
            k=1
        )[0]
    
    def update_conditions_after_species_input(self, species):
        """
        Update game conditions based on species input.
        Advances time by one week.
        
        :param species: Species selected by the user
        :return: Dictionary of updated conditions
        """
        self.update()
        
        return {
            "year": self.year,
            "month": self.month,
            "week": self.week,
            "weather": self.current_weather
        }
    
    def get_current_conditions(self):
        """Get current environmental conditions"""
        return {
            "year": self.year,
            "month": self.month,
            "week": self.week,
            "weather": self.current_weather,
            "temperature": round(self.current_temperature, 1),
            "humidity": round(self.current_humidity, 1)
        }