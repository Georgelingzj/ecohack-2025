import json
from typing import Dict, Any
from datetime import datetime
import os

class InputDataManager:
    def __init__(self, data_dir='input_data'):
        """
        Initialize the input data manager with a specific directory for storing input data.
        
        Args:
            data_dir (str): Directory to store input data files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate the input data dictionary with detailed error reporting.
        
        Args:
            input_data (Dict[str, Any]): Dictionary of input parameters
        
        Returns:
            Dict[str, str]: Empty dict if valid, or dict of error messages
        """
        errors = {}
        
        # Check for required keys
        required_keys = ['species_count', 'environment_type', 'interaction_mode']
        for key in required_keys:
            if key not in input_data:
                errors[key] = f"Missing required parameter: {key}"
        
        # If missing keys, return errors
        if errors:
            return errors
        
        # Validate species count
        try:
            species_count = input_data['species_count']
            if not isinstance(species_count, int):
                errors['species_count'] = "Species count must be an integer"
            elif species_count <= 0:
                errors['species_count'] = "Species count must be a positive number"
        except Exception:
            errors['species_count'] = "Invalid species count"
        
        # Validate environment type
        valid_environments = ['forest', 'desert', 'ocean', 'tundra']
        if input_data['environment_type'] not in valid_environments:
            errors['environment_type'] = f"Invalid environment. Must be one of {valid_environments}"
        
        # Validate interaction mode
        valid_interactions = ['predator_prey', 'cooperative', 'competitive']
        if input_data['interaction_mode'] not in valid_interactions:
            errors['interaction_mode'] = f"Invalid interaction mode. Must be one of {valid_interactions}"
        
        return errors
    
    def save_input(self, input_data: Dict[str, Any]) -> str:
        """
        Save input data to a JSON file with timestamp.
        
        Args:
            input_data (Dict[str, Any]): Dictionary of input parameters
        
        Returns:
            str: Path to the saved input file
        
        Raises:
            ValueError: If input data is invalid, with specific error details
        """
        # Validate input and get any errors
        validation_errors = self.validate_input(input_data)
        
        # If there are any errors, raise a detailed ValueError
        if validation_errors:
            error_message = "Invalid input data:\n" + "\n".join(
                f"- {key}: {value}" for key, value in validation_errors.items()
            )
            raise ValueError(error_message)
        
        # If no errors, proceed with saving
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"input_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(input_data, f, indent=4)
        
        return filepath
    
    def load_latest_input(self) -> Dict[str, Any]:
        """
        Load the most recent input data file.
        
        Returns:
            Dict[str, Any]: Most recent input data
        """
        input_files = [f for f in os.listdir(self.data_dir) if f.startswith('input_') and f.endswith('.json')]
        
        if not input_files:
            return {}
        
        latest_file = max(input_files)
        filepath = os.path.join(self.data_dir, latest_file)
        
        with open(filepath, 'r') as f:
            return json.load(f)