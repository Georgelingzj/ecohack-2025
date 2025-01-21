import random
from datetime import datetime, timedelta

class GameConditions:
    def __init__(self):
        """
        Initialize game conditions with simulation-based time and environmental parameters.
        """
        # Simulation time tracking
        self.current_year = 2025
        self.current_month = 1  # January
        self.current_week = 1
        self.temperature = 20.0
        self.humidity = 60.0
        self.current_weather = "Clear"  # Only use current_weather
        
        # Weather and climate parameters based on Amsterdam's maritime climate
        self.monthly_weather_patterns = {
            1: {"base_temp": 3, "temp_range": 3, "base_humidity": 85, "humidity_range": 10, 
                "weather_types": ["Clear", "Rainy", "Cloudy", "Foggy", "Snowy"]},
            2: {"base_temp": 4, "temp_range": 4, "base_humidity": 80, "humidity_range": 15, 
                "weather_types": ["Clear", "Rainy", "Cloudy", "Foggy", "Windy"]},
            3: {"base_temp": 7, "temp_range": 5, "base_humidity": 75, "humidity_range": 15, 
                "weather_types": ["Clear", "Rainy", "Cloudy", "Foggy", "Windy"]},
            4: {"base_temp": 11, "temp_range": 6, "base_humidity": 70, "humidity_range": 20, 
                "weather_types": ["Clear", "Rainy", "Cloudy", "Windy"]},
            5: {"base_temp": 15, "temp_range": 7, "base_humidity": 70, "humidity_range": 15, 
                "weather_types": ["Clear", "Rainy", "Cloudy", "Windy"]},
            6: {"base_temp": 18, "temp_range": 7, "base_humidity": 70, "humidity_range": 15, 
                "weather_types": ["Clear", "Rainy", "Cloudy"]},
            7: {"base_temp": 20, "temp_range": 8, "base_humidity": 75, "humidity_range": 15, 
                "weather_types": ["Clear", "Rainy", "Cloudy"]},
            8: {"base_temp": 20, "temp_range": 7, "base_humidity": 75, "humidity_range": 15, 
                "weather_types": ["Clear", "Rainy", "Cloudy"]},
            9: {"base_temp": 17, "temp_range": 6, "base_humidity": 80, "humidity_range": 15, 
                "weather_types": ["Clear", "Rainy", "Cloudy", "Windy"]},
            10: {"base_temp": 13, "temp_range": 5, "base_humidity": 85, "humidity_range": 10, 
                "weather_types": ["Clear", "Rainy", "Cloudy", "Foggy", "Windy"]},
            11: {"base_temp": 8, "temp_range": 4, "base_humidity": 85, "humidity_range": 10, 
                "weather_types": ["Clear", "Rainy", "Cloudy", "Foggy", "Windy"]},
            12: {"base_temp": 4, "temp_range": 3, "base_humidity": 85, "humidity_range": 10, 
                "weather_types": ["Clear", "Rainy", "Cloudy", "Foggy", "Snowy"]}
        }
        
        # Initial conditions
        self._update_conditions()
    
    def _update_conditions(self):
        """
        Update game conditions based on current month.
        """
        # Get current month's weather pattern
        month_pattern = self.monthly_weather_patterns[self.current_month]
        
        # Calculate temperature with some randomness
        self.temperature = round(
            month_pattern["base_temp"] + random.uniform(-month_pattern["temp_range"], month_pattern["temp_range"]), 
            1
        )
        
        # Calculate humidity with some randomness
        self.humidity = round(
            month_pattern["base_humidity"] + random.uniform(-month_pattern["humidity_range"], month_pattern["humidity_range"]), 
            1
        )
        
        # Select weather type
        self.current_weather = random.choice(month_pattern["weather_types"])
    
    def update(self):
        # Update time
        self.current_week += 1
        if self.current_week > 4:
            self.current_week = 1
            self.current_month += 1
            if self.current_month > 12:
                self.current_month = 1
                self.current_year += 1
        
        # Update weather conditions
        self._update_weather()
        
        # Update temperature (simplified)
        self.temperature = max(5, min(35, self.temperature + random.uniform(-2, 2)))
        
        # Update humidity (simplified)
        self.humidity = max(30, min(90, self.humidity + random.uniform(-5, 5)))
    
    def _update_weather(self):
        """
        Update weather conditions based on temperature and humidity.
        """
        month_pattern = self.monthly_weather_patterns[self.current_month]
        
        # Higher chance of specific weather based on conditions
        if self.temperature < 5 and self.humidity > 80:
            if "Snowy" in month_pattern["weather_types"]:
                if random.random() < 0.6:
                    self.current_weather = "Snowy"
                    return
                    
        if self.temperature < 10 and self.humidity > 80:
            if "Foggy" in month_pattern["weather_types"]:
                if random.random() < 0.6:
                    self.current_weather = "Foggy"
                    return
        
        if self.humidity > 75:
            if random.random() < 0.4:
                self.current_weather = "Rainy"
                return
        
        # Otherwise choose from available weather types for the month
        self.current_weather = random.choice(month_pattern["weather_types"])
    
    def update_conditions_after_species_input(self, species):
        """
        Update game conditions based on species input.
        Advances time by one week.
        
        :param species: Species selected by the user
        :return: Dictionary of updated conditions
        """
        self.update()
        
        return {
            "year": self.current_year,
            "month": self._get_month_name(),
            "week": self.current_week,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "weather": self.current_weather
        }
    
    def get_current_conditions(self):
        """
        Retrieve current game conditions.
        
        :return: Dictionary of current conditions
        """
        return {
            "year": self.current_year,
            "month": self._get_month_name(),
            "week": self.current_week,
            "temperature": round(self.temperature, 1),
            "humidity": round(self.humidity, 1),
            "weather": self.current_weather
        }
    
    def _get_month_name(self):
        """
        Convert month number to month name.
        
        :return: Month name as string
        """
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        return month_names[self.current_month - 1]