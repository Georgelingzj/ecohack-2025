import os
import json
import asyncio
from simulator.agents import BioAgent, EnvAgent
import matplotlib.pyplot as plt

from simulator.utils import get_project_root

from simulator.types import CaseModel

# Load cases but don't process them yet
case_path = os.path.join(get_project_root(), 'data/cases_example.json')
with open(case_path, 'r', encoding='utf-8') as f:
    cases = json.load(f)

async def run_simulation(time_steps=10, setting_id="setting-1"):
    """
    Run simulation with specified setting
    
    Args:
        time_steps: Number of time steps to simulate
        setting_id: ID of the case setting to use (e.g., "setting-1", "setting-2")
    """
    print("Starting simulation in simulator...")
    
    # Get the specific case data
    if setting_id not in cases:
        raise ValueError(f"Unknown setting ID: {setting_id}")
    
    case_data = cases[setting_id]
    CASE = CaseModel(**case_data)
    
    # Add tracking lists for plotting
    time_steps_x = []
    native_population = []
    invasive_population = []
    env_changes = []  # Track environmental changes
    
    print(f'initializing agents...')

    env_agent = EnvAgent()
    env_model = env_agent.initialize_environment(case_model=CASE)

    bio_agent_native = BioAgent()
    bio_agent_native.initialize_life(
        bio_name=CASE.native_specie_name,
        bio_role='native specie',
        bio_num=CASE.native_specie_initial_number,
        bio_density=CASE.native_specie_initial_density
    )

    bio_agent_invasive = BioAgent()
    bio_agent_invasive.initialize_life(
        bio_name=CASE.invasive_specie_name,
        bio_role='invasive specie',
        bio_num=CASE.invasive_specie_initial_number,
        bio_density=CASE.invasive_specie_initial_density
    )

    print(f'agents initialized.')
    print(f'starting simulation...')

    # Get reference rates from case data
    invasive_growth_upper = CASE.invasive_specie_growth_upper if hasattr(CASE, 'invasive_specie_growth_upper') else 25
    invasive_growth_lower = CASE.invasive_specie_growth_lower if hasattr(CASE, 'invasive_specie_growth_lower') else 15
    # Convert positive decline rates to negative for plotting
    native_decline_upper = -abs(CASE.native_specie_decline_upper) if hasattr(CASE, 'native_specie_decline_upper') else -5
    native_decline_lower = -abs(CASE.native_specie_decline_lower) if hasattr(CASE, 'native_specie_decline_lower') else -15

    # Calculate average rates
    invasive_avg_rate = (invasive_growth_upper + invasive_growth_lower) / 2
    native_avg_rate = (native_decline_upper + native_decline_lower) / 2  # Will be negative

    # Reference data points for 12 months
    months = list(range(1, 13))
    
    # Reference data for Invasive species
    invasive_ref_rate = [invasive_avg_rate] * 12
    plt.plot(months, invasive_ref_rate, 'r--', linewidth=1.5, 
             label=f'Reference: {CASE.invasive_specie_name} ({invasive_avg_rate}% monthly growth)')
    
    # Reference data for Native species (already negative)
    native_ref_rate = [native_avg_rate] * 12
    plt.plot(months, native_ref_rate, 'g--', linewidth=1.5, 
             label=f'Reference: {CASE.native_specie_name} ({abs(native_avg_rate)}% monthly decline)')
    
    # Add shaded regions for reference ranges
    plt.fill_between(months, [invasive_growth_lower]*12, [invasive_growth_upper]*12, 
                    color='red', alpha=0.1, 
                    label=f'Reference Range: {CASE.invasive_specie_name} ({invasive_growth_lower}-{invasive_growth_upper}%)')
    plt.fill_between(months, [native_decline_lower]*12, [native_decline_upper]*12, 
                    color='green', alpha=0.1, 
                    label=f'Reference Range: {CASE.native_specie_name} ({abs(native_decline_upper)}-{abs(native_decline_lower)}% decline)')
    
    # run for each time step
    for i in range(time_steps):
        time_steps_x.append(i + 1)
        env_changes.append(1 if i == 6 else 0)  # Mark when we inject environmental change
        print(f'running time step {i + 1} / {time_steps}...')

        bio_agent_invasive_num = bio_agent_invasive.life_memory[-1]['specie_num']
        bio_agent_invasive_density = bio_agent_invasive.life_memory[-1]['specie_density']
        bio_agent_invasive_status_list = bio_agent_invasive.get_current_bio_status_list()

        bio_agent_native_num = bio_agent_native.life_memory[-1]['specie_num']
        bio_agent_native_density = bio_agent_native.life_memory[-1]['specie_density']
        bio_agent_native_status_list = bio_agent_native.get_current_bio_status_list()

        env_current_status = env_agent.get_current_environment_status()

        # collaborative reasoning
        reasoning_tasks = []

        reasoning_tasks.append(
            bio_agent_invasive.predict_life(
                competitor_name=bio_agent_native.bio_name,
                competitor_num=bio_agent_native_num,
                competitor_density=bio_agent_native_density,
                competitor_status_list=bio_agent_native_status_list,
                current_environment=env_current_status
            )
        )

        reasoning_tasks.append(
            bio_agent_native.predict_life(
                competitor_name=bio_agent_invasive.bio_name,
                competitor_num=bio_agent_invasive_num,
                competitor_density=bio_agent_invasive_density,
                competitor_status_list=bio_agent_invasive_status_list,
                current_environment=env_current_status
            )
        )

        # inject more favourable conditions for invasive species: Zebra Mussel
        if i == 6:
            user_instruction = "Environment more favourable for invasive species, suppress native species"

            reasoning_tasks.append(
                env_agent.predict_environment(
                    agent_status_list=[
                        {
                            "bio_name": bio_agent_invasive.bio_name,
                            "bio_num": bio_agent_invasive_num,
                            "bio_density": bio_agent_invasive_density,
                            "characteristics": "invasive",
                            "bio_status_list": bio_agent_invasive_status_list
                        },
                        {
                            "bio_name": bio_agent_native.bio_name,
                            "bio_num": bio_agent_native_num,
                            "bio_density": bio_agent_native_density,
                            "characteristics": "native",
                            "bio_status_list": bio_agent_native_status_list
                        }
                    ],
                    env_change_condition=CASE.weather_changing_description,
                    user_instruction=user_instruction
                )
            )
        else:
            reasoning_tasks.append(
                env_agent.predict_environment(
                    agent_status_list=[
                        {
                            "bio_name": bio_agent_invasive.bio_name,
                            "bio_num": bio_agent_invasive_num,
                            "bio_density": bio_agent_invasive_density,
                            "characteristics": "invasive",
                            "bio_status_list": bio_agent_invasive_status_list
                        },
                        {
                            "bio_name": bio_agent_native.bio_name,
                            "bio_num": bio_agent_native_num,
                            "bio_density": bio_agent_native_density,
                            "characteristics": "native",
                            "bio_status_list": bio_agent_native_status_list
                        }
                    ],
                    env_change_condition=CASE.weather_changing_description,
                    user_instruction=None
                )
            )

        await asyncio.gather(*reasoning_tasks)

        # Store data for plotting
        native_population.append(bio_agent_native.life_memory[-1]['specie_num'])
        invasive_population.append(bio_agent_invasive.life_memory[-1]['specie_num'])
        
        # After processing each step, yield the current state
        current_state = {
            'step': i,
            'native_name': CASE.native_specie_name,
            'invasive_name': CASE.invasive_specie_name,
            'native_population': bio_agent_native.life_memory[-1]['specie_num'],
            'invasive_population': bio_agent_invasive.life_memory[-1]['specie_num'],
            'env_change': 1 if i == 6 else 0
        }
        print(f"Yielding step {i + 1} data")  # Debug print
        yield current_state

        print("\n" + "="*30 + "\n")

    # Create plots after simulation
    plt.figure(figsize=(12, 6))
    
    # Plot species populations
    plt.plot(time_steps_x, native_population, 'g-', linewidth=2, label=f'Native Species ({CASE.native_specie_name})')
    plt.plot(time_steps_x, invasive_population, 'r-', linewidth=2, label=f'Invasive Species ({CASE.invasive_specie_name})')
    
    # Add vertical line for environmental change
    for i, change in enumerate(env_changes):
        if change:
            plt.axvline(x=time_steps_x[i], color='blue', linestyle='--', alpha=0.5, 
                       label='Environmental Change')
    
    plt.xlabel('Time Steps (Months)')
    plt.ylabel('Population')
    plt.title('Species Population Changes Over Time')
    plt.legend(loc='upper right')
    plt.grid(True)
    
    # Save the plot
    output_dir = os.path.join(get_project_root(), 'output')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'simulation_results.png'))
    plt.close()
    
    print(f"Plot saved as 'simulation_results.png' in the output directory")

    # After the simulation loop ends, calculate monthly rates
    native_population_rates = []
    invasive_population_rates = []
    native_density_rates = []
    invasive_density_rates = []
    
    # Calculate monthly rates (percentage change)
    for i in range(1, len(time_steps_x)):
        # Population rates
        native_pop_rate = ((native_population[i] - native_population[i-1]) / native_population[i-1]) * 100
        invasive_pop_rate = ((invasive_population[i] - invasive_population[i-1]) / invasive_population[i-1]) * 100
        
        # Density rates
        native_density_current = bio_agent_native.life_memory[i]['specie_density']
        native_density_prev = bio_agent_native.life_memory[i-1]['specie_density']
        native_density_rate = ((native_density_current - native_density_prev) / native_density_prev) * 100
        
        invasive_density_current = bio_agent_invasive.life_memory[i]['specie_density']
        invasive_density_prev = bio_agent_invasive.life_memory[i-1]['specie_density']
        invasive_density_rate = ((invasive_density_current - invasive_density_prev) / invasive_density_prev) * 100
        
        native_population_rates.append(native_pop_rate)
        invasive_population_rates.append(invasive_pop_rate)
        native_density_rates.append(native_density_rate)
        invasive_density_rates.append(invasive_density_rate)
    
    # Print the final average rates
    print("\nAverage Monthly Growth Rates:")
    print(f"Native Species:")
    print(f"  Population: {sum(native_population_rates)/len(native_population_rates):.2f}%")
    print(f"  Density: {sum(native_density_rates)/len(native_density_rates):.2f}%")
    print(f"Invasive Species:")
    print(f"  Population: {sum(invasive_population_rates)/len(invasive_population_rates):.2f}%")
    print(f"  Density: {sum(invasive_density_rates)/len(invasive_density_rates):.2f}%")

    # Create plot for population growth rates
    plt.figure(figsize=(12, 6))
    
    # Plot simulation results
    plt.plot(time_steps_x[1:], native_population_rates, 'g-', linewidth=2, 
             label=f'Simulation: Native Species ({CASE.native_specie_name})')
    plt.plot(time_steps_x[1:], invasive_population_rates, 'r-', linewidth=2, 
             label=f'Simulation: Invasive Species ({CASE.invasive_specie_name})')
    
    # Add reference data from paper
    # Create reference data points for 12 months
    months = list(range(1, 13))
    
    # Reference data for Invasive species
    plt.plot(months, invasive_ref_rate, 'r--', linewidth=1.5, 
             label=f'Reference: {CASE.invasive_specie_name} ({invasive_avg_rate}% monthly growth)')
    
    # Reference data for Native species (already negative)
    plt.plot(months, native_ref_rate, 'g--', linewidth=1.5, 
             label=f'Reference: {CASE.native_specie_name} ({abs(native_avg_rate)}% monthly decline)')
    
    # Add shaded regions for reference ranges
    plt.fill_between(months, [invasive_growth_lower]*12, [invasive_growth_upper]*12, 
                    color='red', alpha=0.1, 
                    label=f'Reference Range: {CASE.invasive_specie_name} ({invasive_growth_lower}-{invasive_growth_upper}%)')
    plt.fill_between(months, [native_decline_lower]*12, [native_decline_upper]*12, 
                    color='green', alpha=0.1, 
                    label=f'Reference Range: {CASE.native_specie_name} ({abs(native_decline_upper)}-{abs(native_decline_lower)}% decline)')
    
    # Add vertical line for environmental change
    for i, change in enumerate(env_changes[1:], 1):
        if change:
            plt.axvline(x=time_steps_x[i], color='blue', linestyle='--', alpha=0.5,
                       label='Environmental Change')
    
    plt.xlabel('Time Steps (Months)')
    plt.ylabel('Population Growth Rate (%)')
    plt.title('Monthly Population Growth Rates\n(Simulation vs Reference Data)')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    # Adjust layout to prevent legend cutoff
    plt.tight_layout()
    
    # Save the growth rates plot
    output_dir = os.path.join(get_project_root(), 'output')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'monthly_growth_rates.png'), bbox_inches='tight')
    plt.close()
    
    print(f"Monthly growth rates plot saved as 'monthly_growth_rates.png' in the output directory")


if __name__ == '__main__':
    print(f'Initializing environment...')
    
    async def main():
        async for step in run_simulation():
            print(f"Step {step['step'] + 1}: Processing...")
    
    asyncio.run(main())
    print(f'Simulation finished.')
