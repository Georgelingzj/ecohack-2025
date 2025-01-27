import gradio as gr
import os
import asyncio
import matplotlib.pyplot as plt
from simulator.simulation import run_simulation
from simulator.utils import get_project_root
from simulator.pdf_digest import process_pdf_file
import json
from simulator.types import CaseModel

# Load existing cases
CASES_PATH = f"{get_project_root()}/data/cases_example.json"
with open(CASES_PATH, 'r', encoding='utf-8') as f:
    cases_data = json.load(f)

# Create mapping of display names to case data
EXISTING_OPTIONS = {
    "The Great Lakes: Mussels": CaseModel(**cases_data["setting-1"]),
    "Cane Toad Vs Northern Quoll in northern Australia": CaseModel(**cases_data["setting-2"])
}

# Create mapping for simulation settings
SETTING_IDS = {
    "The Great Lakes: Mussels": "setting-1",
    "Cane Toad Vs Northern Quoll in northern Australia": "setting-2"
}

async def process_step1(upload_choice, uploaded_file, existing_choice):
    if upload_choice:
        if uploaded_file is None:
            return "Please upload a PDF file"
        
        # Process the uploaded PDF
        success, message, case_data = await process_pdf_file(uploaded_file.name)
        
        if not success:
            return f"Error: {message}"
        
        # Store the case data for later use
        global current_case_data
        current_case_data = case_data
        
        return f"Successfully processed file: {uploaded_file.name}\nFound valid biology invasion case study."
    else:
        if existing_choice is None:
            return "Please select an existing simulation"
        return f"Using existing simulation option: {existing_choice}"

async def run_simulation_with_plots(setting_id="setting-1", progress=gr.Progress()):
    print("Starting simulation with plots...")
    try:
        # Create figures once
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        time_steps = 10
        
        # Data storage
        time_steps_x = []
        native_population = []
        invasive_population = []
        native_growth_rates = []
        invasive_growth_rates = []
        env_changes = []
        
        async for step_data in run_simulation(time_steps=time_steps, setting_id=setting_id):
            current_step = step_data['step'] + 1
            
            # Update data
            time_steps_x.append(current_step)
            native_population.append(step_data['native_population'])
            invasive_population.append(step_data['invasive_population'])
            env_changes.append(step_data['env_change'])
            
            # Calculate growth rates
            if len(native_population) > 1:
                native_growth = ((native_population[-1] - native_population[-2]) / native_population[-2]) * 100
                native_growth_rates.append(native_growth)
                invasive_growth = ((invasive_population[-1] - invasive_population[-2]) / invasive_population[-2]) * 100
                invasive_growth_rates.append(invasive_growth)
            
            # Update population plot
            ax1.clear()
            ax1.plot(time_steps_x, native_population, 'g-', label=f'Native ({step_data["native_name"]})')
            ax1.plot(time_steps_x, invasive_population, 'r-', label=f'Invasive ({step_data["invasive_name"]})')
            
            # Add environmental markers
            for i, change in enumerate(env_changes):
                if change:
                    ax1.axvline(time_steps_x[i], color='b', linestyle='--', alpha=0.5)
            
            ax1.set_title('Population Trends')
            ax1.set_xlabel('Time Steps (Months)')
            ax1.set_ylabel('Population')
            ax1.legend()
            ax1.grid(True)
            
            # Update growth rate plot
            ax2.clear()
            if native_growth_rates:
                ax2.plot(time_steps_x[1:], native_growth_rates, 'g--', label=f'Native Growth Rate')
                ax2.plot(time_steps_x[1:], invasive_growth_rates, 'r--', label=f'Invasive Growth Rate')
                ax2.axhline(0, color='k', linestyle='--', alpha=0.3)
                ax2.set_title('Growth Rate Trends')
                ax2.set_xlabel('Time Steps (Months)')
                ax2.set_ylabel('Growth Rate (%)')
                ax2.legend()
                ax2.grid(True)

            # Draw and yield the current state of the plots
            fig1.canvas.draw()
            fig2.canvas.draw()
            yield fig1, fig2, f"Step {current_step}/{time_steps}: Processing..."
        
        yield fig1, fig2, "Simulation complete!"
    except Exception as e:
        print(f"Error: {str(e)}")
        yield None, None, f"Error: {str(e)}"
    finally:
        plt.close(fig1)
        plt.close(fig2)

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# BioSim Demo (EcoHack)")
    
    with gr.Tabs() as tabs:
        with gr.Tab("Step 1: Choose Simulation", id="step1"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Upload New File (This is Beta Feature, "
                                "We cannot guarantee the accuracy of the paper processing using LLM)")
                    upload_choice = gr.Checkbox(label="Use file upload", value=True)
                    file_upload = gr.File(label="Upload PDF", file_types=[".pdf"])
                with gr.Column():
                    gr.Markdown("### Choose Existing Simulation")
                    existing_choice = gr.Radio(
                        choices=list(EXISTING_OPTIONS.keys()),
                        label="Select from existing simulations"
                    )
            submit_btn = gr.Button("Proceed to Confirmation")
            output = gr.Textbox(label="Status")

        with gr.Tab("Confirmation", id="confirm"):
            with gr.Column():
                gr.Markdown("### Confirm Your Selection")
                confirmation_text = gr.Markdown("")
                with gr.Row():
                    back_btn = gr.Button("Back to Selection", variant="secondary")
                    confirm_btn = gr.Button("Proceed to Simulation", variant="primary")

        with gr.Tab("Step 2: Processing", id="step2"):
            with gr.Column():
                gr.Markdown("### Simulation Progress")
                with gr.Row():
                    with gr.Column():
                        plot_pop = gr.Plot(label="Population Trend", every=1)
                    with gr.Column():
                        plot_growth = gr.Plot(label="Growth Rate Trend", every=1)
                with gr.Row():
                    status_output = gr.Textbox(label="Simulation Status")
                    start_sim_btn = gr.Button("Start Simulation", variant="primary")
                    view_results_btn = gr.Button("View Final Results", variant="secondary", visible=False)
                
                # Store the current setting in a Gradio state
                current_setting = gr.State("setting-1")
                
                def update_current_setting(upload_choice, existing_choice):
                    if upload_choice:
                        return "uploaded"
                    if existing_choice is None:
                        return "setting-1"  # default setting
                    return SETTING_IDS[existing_choice]
                
                def on_simulation_complete(pop_plot, growth_plot, status):
                    if "complete" in status.lower():
                        return gr.Button(visible=True)
                    return gr.Button(visible=False)
                
                start_sim_btn.click(
                    run_simulation_with_plots,
                    inputs=[current_setting],
                    outputs=[plot_pop, plot_growth, status_output]
                ).then(
                    on_simulation_complete,
                    inputs=[plot_pop, plot_growth, status_output],
                    outputs=[view_results_btn]
                )

                # Update current_setting when selection changes
                upload_choice.change(
                    update_current_setting,
                    inputs=[upload_choice, existing_choice],
                    outputs=[current_setting]
                )
                existing_choice.change(
                    update_current_setting,
                    inputs=[upload_choice, existing_choice],
                    outputs=[current_setting]
                )

        with gr.Tab("Step 3: Final Results", id="results"):
            with gr.Column():
                gr.Markdown("### Final Simulation Results")
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Population Trends Over Time")
                        results_image = gr.Image(label="Population Trends", interactive=False)
                    with gr.Column():
                        gr.Markdown("#### Monthly Growth Rates")
                        growth_image = gr.Image(label="Growth Rates", interactive=False)
                
                def load_final_results():
                    output_dir = os.path.join(get_project_root(), 'output')
                    population_plot = os.path.join(output_dir, 'simulation_results.png')
                    growth_plot = os.path.join(output_dir, 'monthly_growth_rates.png')
                    return [
                        population_plot if os.path.exists(population_plot) else None,
                        growth_plot if os.path.exists(growth_plot) else None,
                        gr.Tabs(selected="results")
                    ]

                view_results_btn.click(
                    load_final_results,
                    outputs=[results_image, growth_image, tabs]
                )

    async def process_and_switch_to_confirm(upload_choice, uploaded_file, existing_choice):
        status = await process_step1(upload_choice, uploaded_file, existing_choice)
        
        if "Successfully processed" in status or "Using existing" in status:
            if upload_choice:
                confirmation_message = (
                    "### Please confirm your selection:\n\n"
                    f"- Using uploaded file: {uploaded_file.name}\n"
                    f"- Invasive Species: {current_case_data.invasive_specie_name}\n"
                    f"- Native Species: {current_case_data.native_specie_name}\n"
                    "\nClick 'Proceed to Simulation' to continue or 'Back to Selection' to make changes."
                )
            else:
                case_data = EXISTING_OPTIONS[existing_choice]  # Now contains CaseModel instance
                confirmation_message = (
                    "### Please confirm your selection:\n\n"
                    f"- Using existing simulation: {existing_choice}\n"
                    f"- Invasive Species: {case_data.invasive_specie_name}\n"
                    f"- Native Species: {case_data.native_specie_name}\n"
                    "\nClick 'Proceed to Simulation' to continue or 'Back to Selection' to make changes."
                )
            return [status, confirmation_message, gr.Tabs(selected="confirm")]
        return [status, "", gr.Tabs(selected="step1")]

    def go_back_to_step1():
        return gr.Tabs(selected="step1")

    def proceed_to_step2():
        return gr.Tabs(selected="step2")

    # Connect the buttons to their actions
    submit_btn.click(
        process_and_switch_to_confirm,
        inputs=[upload_choice, file_upload, existing_choice],
        outputs=[output, confirmation_text, tabs],
        api_name="process_and_confirm"
    ).then()

    back_btn.click(
        go_back_to_step1,
        outputs=tabs
    )

    confirm_btn.click(
        proceed_to_step2,
        outputs=tabs
    )

if __name__ == "__main__":
    demo.queue().launch()