import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class AIInterface:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.context = """
        You are an ecological simulation assistant. You help analyze and provide insights about 
        invasive species behavior and environmental conditions. The simulation tracks:
        - Native species population
        - Invasive species population
        - Endangered species population
        - Environmental conditions (temperature, humidity, pollution)
        """
    
    async def analyze_conditions(self, current_state):
        """Analyze current simulation state and provide insights"""
        prompt = f"""
        Current simulation state:
        Temperature: {current_state['temperature']}°C
        Humidity: {current_state['humidity']}%
        Native Species: {current_state['native_density']}%
        Invasive Species: {current_state['invasive_density']}%
        Endangered Species: {current_state['endangered_density']}%
        
        Please provide a brief analysis of the ecological situation and suggest possible interventions.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.context},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Analysis unavailable: {str(e)}"
    
    async def get_environmental_parameters(self, research_text):
        """Extract environmental parameters from research text"""
        prompt = f"""
        Based on the following research text, please extract appropriate environmental parameters 
        for the simulation. Focus on temperature ranges, humidity levels, and species interactions.
        
        Research text:
        {research_text}
        
        Please provide parameters in JSON format with:
        - temperature_range
        - humidity_range
        - growth_rates
        - interaction_coefficients
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.context},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Parameter extraction failed: {str(e)}" 