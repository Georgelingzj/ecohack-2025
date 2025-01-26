import tkinter as tk
from tkinter import ttk, filedialog, messagebox
try:
    from PIL import Image, ImageTk
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
import re
import json
from pathlib import Path

class InputInterface:
    def __init__(self, on_parameters_ready):
        self.root = tk.Tk()
        self.root.title("Ecological Invasion Simulation - Input Interface")
        self.root.geometry("800x600")
        self.on_parameters_ready = on_parameters_ready
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Custom.TButton', 
                           padding=10, 
                           font=('Helvetica', 12))
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input methods frame
        input_frame = ttk.LabelFrame(main_frame, text="Input Methods", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # PDF Upload (only if PyPDF2 is available)
        if PDF_SUPPORT:
            self.pdf_button = ttk.Button(
                input_frame, 
                text="Upload PDF", 
                command=self.load_pdf,
                style='Custom.TButton'
            )
            self.pdf_button.grid(row=0, column=0, pady=5, padx=5)
        else:
            pdf_warning = ttk.Label(
                input_frame,
                text="PDF support not available. Please install PyPDF2.",
                foreground='red'
            )
            pdf_warning.grid(row=0, column=0, pady=5, padx=5)
        
        # Text input with placeholder
        self.text_input = tk.Text(input_frame, height=10, width=50)
        self.text_input.insert('1.0', "Enter environmental parameters here...\n\n"
                             "Example:\nTemperature: 25\nHumidity: 60\nPollution: 30")
        self.text_input.grid(row=1, column=0, pady=5, padx=5)
        
        # Parameter display frame
        param_frame = ttk.LabelFrame(main_frame, text="Generated Parameters", padding="10")
        param_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Parameter labels
        self.param_labels = {}
        params = ["Temperature", "Humidity", "Pollution", "Species Count"]
        for i, param in enumerate(params):
            label = ttk.Label(param_frame, text=f"{param}: ")
            label.grid(row=i, column=0, pady=2, padx=5)
            value_label = ttk.Label(param_frame, text="--")
            value_label.grid(row=i, column=1, pady=2, padx=5)
            self.param_labels[param] = value_label
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        self.generate_button = ttk.Button(
            button_frame,
            text="Generate Parameters",
            command=self.generate_parameters,
            style='Custom.TButton'
        )
        self.generate_button.grid(row=0, column=0, padx=5)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Simulation",
            command=self.start_simulation,
            style='Custom.TButton'
        )
        self.start_button.grid(row=0, column=1, padx=5)
        self.start_button.state(['disabled'])
        
    def load_pdf(self):
        if not PDF_SUPPORT:
            self.show_error("PDF support not available. Please install PyPDF2.")
            return
            
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    self.text_input.delete('1.0', tk.END)
                    self.text_input.insert('1.0', text)
            except Exception as e:
                self.show_error(f"Error loading PDF: {str(e)}")
    
    def generate_parameters(self):
        text = self.text_input.get('1.0', tk.END).strip()
        if not text or text == "Enter environmental parameters here...":
            self.show_error("Please enter text or upload a PDF first")
            return
        
        # Extract parameters from text
        params = self.extract_parameters(text)
        
        # Update parameter display
        for param, value in params.items():
            if param in self.param_labels:
                self.param_labels[param].config(text=str(value))
        
        # Enable start button
        self.start_button.state(['!disabled'])
        
        # Save parameters
        self.current_params = params
    
    def extract_parameters(self, text):
        """Extract parameters from text using regex and basic NLP"""
        params = {
            "Temperature": 20,  # Default values
            "Humidity": 50,
            "Pollution": 0,
            "Species Count": 3
        }
        
        # Temperature extraction
        temp_pattern = r"temperature.*?(\d+)"
        temp_match = re.search(temp_pattern, text.lower())
        if temp_match:
            params["Temperature"] = min(40, max(0, int(temp_match.group(1))))
        
        # Humidity extraction
        humid_pattern = r"humidity.*?(\d+)"
        humid_match = re.search(humid_pattern, text.lower())
        if humid_match:
            params["Humidity"] = min(100, max(0, int(humid_match.group(1))))
        
        # Pollution extraction
        pollution_pattern = r"pollution.*?(\d+)"
        pollution_match = re.search(pollution_pattern, text.lower())
        if pollution_match:
            params["Pollution"] = min(100, max(0, int(pollution_match.group(1))))
        
        return params
    
    def start_simulation(self):
        if hasattr(self, 'current_params'):
            self.root.destroy()  # Destroy the window instead of just hiding it
            self.on_parameters_ready(self.current_params)
    
    def show_error(self, message):
        messagebox.showerror("Error", message)
    
    def run(self):
        self.root.mainloop() 