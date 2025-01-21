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
        
        # Weather and climate parameters based on Amsterdam's maritime climate
        self.monthly_weather_patterns = {
            1: {"base_temp": 3, "temp_range": 3, "base_humidity": 85, "humidity_range": 10, "weather_types": ["Cold", "Rainy", "Cloudy", "Windy"]},
            2: {"base_temp": 4, "temp_range": 4, "base_humidity": 80, "humidity_range": 15, "weather_types": ["Cold", "Rainy", "Partly Cloudy", "Windy"]},
            3: {"base_temp": 7, "temp_range": 5, "base_humidity": 75, "humidity_range": 15, "weather_types": ["Cool", "Rainy", "Partly Cloudy", "Windy"]},
            4: {"base_temp": 11, "temp_range": 6, "base_humidity": 70, "humidity_range": 20, "weather_types": ["Cool", "Rainy", "Partly Sunny", "Windy"]},
            5: {"base_temp": 15, "temp_range": 7, "base_humidity": 70, "humidity_range": 15, "weather_types": ["Mild", "Partly Sunny", "Occasional Rain", "Cloudy"]},
            6: {"base_temp": 18, "temp_range": 7, "base_humidity": 70, "humidity_range": 15, "weather_types": ["Warm", "Sunny", "Occasional Rain", "Partly Cloudy"]},
            7: {"base_temp": 20, "temp_range": 8, "base_humidity": 75, "humidity_range": 15, "weather_types": ["Warm", "Sunny", "Occasional Rain", "Partly Cloudy"]},
            8: {"base_temp": 20, "temp_range": 7, "base_humidity": 75, "humidity_range": 15, "weather_types": ["Warm", "Sunny", "Occasional Rain", "Cloudy"]},
            9: {"base_temp": 17, "temp_range": 6, "base_humidity": 80, "humidity_range": 15, "weather_types": ["Mild", "Partly Sunny", "Occasional Rain", "Cloudy"]},
            10: {"base_temp": 13, "temp_range": 5, "base_humidity": 85, "humidity_range": 10, "weather_types": ["Cool", "Rainy", "Cloudy", "Windy"]},
            11: {"base_temp": 8, "temp_range": 4, "base_humidity": 85, "humidity_range": 10, "weather_types": ["Cold", "Rainy", "Cloudy", "Windy"]},
            12: {"base_temp": 4, "temp_range": 3, "base_humidity": 85, "humidity_range": 10, "weather_types": ["Cold", "Rainy", "Snowy", "Cloudy"]}
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
        # Update week
        self.current_week += 1
        if self.current_week > 4:
            self.current_week = 1
            self.current_month += 1
            if self.current_month > 12:
                self.current_month = 1
                self.current_year += 1
        
        # Get current month's weather pattern for more contextual updates
        month_pattern = self.monthly_weather_patterns[self.current_month]
        base_temp = month_pattern["base_temp"]
        temp_range = month_pattern["temp_range"]
        
        # More sophisticated temperature progression
        # Use a combination of correction and seasonal variation
        
        # Determine seasonal correction factor
        # This creates a smoother transition between months
        if self.current_month in [12, 1, 2]:  # Winter months
            seasonal_correction = -0.5
        elif self.current_month in [3, 4, 5]:  # Spring months
            seasonal_correction = 0.3
        elif self.current_month in [6, 7, 8]:  # Summer months
            seasonal_correction = 0.5
        else:  # Autumn months
            seasonal_correction = -0.3
        
        # Calculate temperature deviation
        temp_deviation = self.temperature - base_temp
        
        # Correction mechanism
        # Pulls temperature towards base temp with seasonal influence
        temp_correction = (
            -temp_deviation * 0.2 +  # Gradual pull towards base temp
            seasonal_correction  # Seasonal temperature trend
        )
        
        # Add some randomness, but reduce its impact
        temp_variation = random.uniform(-temp_range/3, temp_range/3)
        
        # Update temperature
        self.temperature += temp_correction + temp_variation
        
        # Ensure temperature stays within a reasonable range for the month
        # Slightly expanded range to allow for more natural variation
        min_temp = base_temp - temp_range * 1.5
        max_temp = base_temp + temp_range * 1.5
        self.temperature = round(max(min(self.temperature, max_temp), min_temp), 1)
        
        # Humidity update with more controlled variation
        humidity_variation = random.uniform(-month_pattern["humidity_range"], month_pattern["humidity_range"])
        self.humidity += humidity_variation
        
        # Keep humidity in reasonable ranges
        self.humidity = round(max(min(self.humidity, 100), 0), 1)
        
        # Update weather based on conditions
        self._update_weather()
    
    def _update_weather(self):
        """
        Update weather conditions based on temperature and humidity.
        Ensures more consistent and predictable weather updates.
        """
        # Primary weather determination based on monthly patterns
        month_pattern = self.monthly_weather_patterns[self.current_month]
        base_weather_types = month_pattern["weather_types"]
        
        # Temperature-based weather refinement
        if self.temperature > 35:
            self.current_weather = "Extremely Hot"
        elif self.temperature > 30:
            self.current_weather = "Hot and Sunny"
        elif self.temperature > 25:
            self.current_weather = "Warm"
        elif self.temperature > 20:
            self.current_weather = "Mild"
        elif self.temperature > 10:
            self.current_weather = "Cool"
        elif self.temperature > 0:
            self.current_weather = "Cold"
        else:
            self.current_weather = "Freezing"
        
        # Humidity-based weather modification
        if self.humidity > 80:
            self.current_weather = "Heavy Rain"
        elif self.humidity > 70:
            self.current_weather = "Rainy"
        elif self.humidity > 50:
            self.current_weather = "Cloudy"
        
        # Ensure the weather is from the month's possible types if possible
        if self.current_weather not in base_weather_types:
            # If the current weather is not in the base types, choose a random base type
            self.current_weather = random.choice(base_weather_types)
        
        # Small chance of unexpected weather
        if random.random() < 0.1:  # Reduced from 0.2 to make it less frequent
            unexpected_weathers = [
                "Windy", "Foggy", "Partly Cloudy", "Overcast"
            ]
            self.current_weather = random.choice(unexpected_weathers)
    
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
            "temperature": self.temperature,
            "humidity": self.humidity,
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