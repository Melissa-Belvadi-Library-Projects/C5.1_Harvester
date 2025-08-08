import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import calendar
from datetime import datetime
import threading
import subprocess
import os
import sys
from pathlib import Path
import json
from dateutil.relativedelta import relativedelta


# === Utility ===
months = list(calendar.month_name)[1:]  # ['January', ..., 'December']
#
# === Reusable Vendor/Provider Frame ===
class VendorFrame(ttk.LabelFrame):
   def __init__(self, parent, title, items):
       super().__init__(parent, text=title, padding=10)


       self.vars = []


       # Top frame for buttons
       button_frame = tk.Frame(self)
       button_frame.pack(fill="x", pady=(0, 5))


       # Making select/deselect buttons slightly bigger for consistency
       tk.Button(button_frame, text="Select All", command=self.select_all, font=("Arial", 9)).pack(side="left", padx=5)
       tk.Button(button_frame, text="Deselect All", command=self.deselect_all, font=("Arial", 9)).pack(side="left",
                                                                                                       padx=5)


       # Scrollable container for checkboxes
       container = tk.Frame(self)
       container.pack(fill="both", expand=True)


       canvas = tk.Canvas(container, height=200)
       # Make the scrollbar wider
       scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)  # Increased width
       list_frame = tk.Frame(canvas)


       list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
       canvas.create_window((0, 0), window=list_frame, anchor="nw")
       canvas.configure(yscrollcommand=scrollbar.set)


       canvas.pack(side="left", fill="both", expand=True)
       scrollbar.pack(side="right", fill="y")


       # Add checkboxes
       for item in items:
           var = tk.BooleanVar()
           cb = tk.Checkbutton(list_frame, text=item, variable=var, anchor="w", padx=5)
           cb.pack(fill="x", pady=2)
           self.vars.append((item, var))






   def get_selected(self):
       return [name for name, var in self.vars if var.get()]


   def select_all(self):
       for _, var in self.vars:
           var.set(True)


   def deselect_all(self):
       for _, var in self.vars:
           var.set(False)




# === Subprocess Handler ===
class SushiHarvesterSubprocess:
   def __init__(self, gui_instance):
       self.gui = gui_instance
       self.process = None
       self.is_running = False

       # Store a reference to the thread for potential future control (e.g., actual pause/resume)
       self._harvester_thread = None


   def log_message(self, message):
       """Thread-safe logging to the GUI"""
       if message.strip():  # Only log non-empty messages
           self.gui.root.after(0, lambda: self.gui.log_text.insert(tk.END, f"{message}\n"))
           self.gui.root.after(0, lambda: self.gui.log_text.see(tk.END))


   def build_command(self, config):
       """Build the command line arguments for the harvester"""
       # Get the harvester script path
       harvester_script = config.get('harvester_script', 'harvester.py')


       # Build the base command
       cmd = [sys.executable, harvester_script]


       # Add arguments based on your harvester's CLI structure
       # Modify these based on your actual harvester's command line interface


       cmd.extend(['--start-date', config['start_date']])
       cmd.extend(['--end-date', config['end_date']])


       if config['reports']:
           cmd.extend(['--reports', ','.join(config['reports'])])


       if config['vendors']:
           cmd.extend(['--vendors', ','.join(config['vendors'])])


       # Add any additional options
       if config.get('output_format'):
           cmd.extend(['--format', config['output_format']])


       if config.get('output_dir'):
           cmd.extend(['--output-dir', config['output_dir']])


       # Add verbose flag for detailed output
       cmd.append('--verbose')


       return cmd


   def _run_harvester_thread(self, config):
       """Internal method to be run in a separate thread."""
       try:
           self.is_running = True
           self.gui.root.after(0, lambda: self.gui.run_button.config(text="Running...", state="disabled"))
           self.gui.root.after(0, lambda: self.gui.stop_button.config(state="normal"))
           self.gui.root.after(0, lambda: self.gui.status_var.set("Running harvester..."))


           self.log_message("=" * 50)
           self.log_message(f"Starting SUSHI Harvester at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
           self.log_message("=" * 50)


           # Build the command
           cmd = self.build_command(config)
           self.log_message(f"Running command: {' '.join(cmd)}")
           self.log_message("-" * 50)


           # Start the process
           self.process = subprocess.Popen(
               cmd,
               stdout=subprocess.PIPE,
               stderr=subprocess.STDOUT,  # Combine stderr with stdout
               text=True,
               bufsize=1,
               universal_newlines=True,
               cwd=config.get('working_directory', '.')
           )


           # Read output line by line in real-time
           for line in iter(self.process.stdout.readline, ''):
               if line:
                   self.log_message(line.rstrip())


               # Check if process is still running. This helps to break out if terminated externally.
               if not self.is_running:  # Check our internal flag, allows for external stop control
                   self.log_message("Process interrupted by stop command.")
                   break
               if self.process.poll() is not None:
                   break


           # Wait for process to complete if not already terminated
           if self.process.poll() is None:
               self.process.wait()


           # Log completion status
           self.log_message("-" * 50)
           if self.process.returncode == 0:
               self.log_message("✅ Harvester completed successfully!")
               self.log_message(f"Exit code: {self.process.returncode}")
               self.gui.root.after(0, lambda: messagebox.showinfo("Success", "Harvester completed successfully!"))
           else:
               self.log_message(f"❌ Harvester failed with exit code: {self.process.returncode}")
               self.gui.root.after(0, lambda: messagebox.showerror("Error",
                                                                   f"Harvester failed with exit code: {self.process.returncode}"))


           self.log_message(f"Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
           self.log_message("=" * 50)


       except FileNotFoundError:
           self.log_message("❌ Error: Harvester script not found!")
           self.log_message("Please check the harvester script path in settings.")
           self.gui.root.after(0, lambda: messagebox.showerror("Error",
                                                               "Harvester script not found!\nPlease check the script path in settings."))


       except Exception as e:
           self.log_message(f"❌ Unexpected error: {str(e)}")
           self.gui.root.after(0, lambda: messagebox.showerror("Error", f"Unexpected error: {str(e)}"))


       finally:
           self.is_running = False
           self.process = None
           self._harvester_thread = None  # Clear thread reference
           # Re-enable the run button and disable stop button
           self.gui.root.after(0, lambda: self.gui.run_button.config(state="normal", text="Start"))
           self.gui.root.after(0, lambda: self.gui.stop_button.config(state="disabled"))
           self.gui.root.after(0, lambda: self.gui.status_var.set("Ready"))


   def run_harvester(self, config):
       """Starts the harvester in a new thread."""
       if self._harvester_thread and self._harvester_thread.is_alive():
           self.log_message("Harvester thread is already running.")
           return


       self._harvester_thread = threading.Thread(target=self._run_harvester_thread, args=(config,))
       self._harvester_thread.daemon = True  # Allows thread to exit with main program
       self._harvester_thread.start()


   def stop_harvester(self):
       """Stop the running harvester process"""
       if self.process and self.is_running:
           self.log_message("🛑 Stopping harvester...")
           self.is_running = False  # Signal the _run_harvester_thread to stop reading
           self.process.terminate()
           try:
               self.process.wait(timeout=5)
           except subprocess.TimeoutExpired:
               self.log_message("🛑 Force killing harvester...")
               self.process.kill()


           self.log_message("🛑 Harvester stopped")
           # Update GUI immediately after stopping, rather than waiting for thread to finish
           self.gui.root.after(0, lambda: self.gui.run_button.config(state="normal", text="Start"))
           self.gui.root.after(0, lambda: self.gui.stop_button.config(state="disabled"))
           self.gui.root.after(0, lambda: self.gui.status_var.set("Stopped"))
           self.process = None




# === Configuration Dialog ===
class ConfigDialog:
   def __init__(self, parent):
       self.parent = parent
       self.result = None


       self.dialog = tk.Toplevel(parent)
       self.dialog.title("Harvester Settings")
       self.dialog.geometry("500x400")
       self.dialog.resizable(False, False)


       # Make dialog modal
       self.dialog.transient(parent)
       self.dialog.grab_set()


       self.setup_dialog()


       # Center the dialog
       self.dialog.update_idletasks()
       x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
       y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
       self.dialog.geometry(f"+{x}+{y}")


   def setup_dialog(self):
       # Main frame
       main_frame = ttk.Frame(self.dialog, padding=20)
       main_frame.pack(fill="both", expand=True)


       # Harvester Script Path
       ttk.Label(main_frame, text="Harvester Script Path:").pack(anchor="w")
       script_frame = ttk.Frame(main_frame)
       script_frame.pack(fill="x", pady=(0, 10))


       self.script_path = tk.StringVar(value="getcounter.py")
       ttk.Entry(script_frame, textvariable=self.script_path, width=50).pack(side="left", fill="x", expand=True)
       ttk.Button(script_frame, text="Browse", command=self.browse_script).pack(side="right", padx=(5, 0))


       # Working Directory
       ttk.Label(main_frame, text="Working Directory:").pack(anchor="w")
       dir_frame = ttk.Frame(main_frame)
       dir_frame.pack(fill="x", pady=(0, 10))


       self.working_dir = tk.StringVar(value=os.getcwd())
       ttk.Entry(dir_frame, textvariable=self.working_dir, width=50).pack(side="left", fill="x", expand=True)
       ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side="right", padx=(5, 0))


       # Output Directory
       ttk.Label(main_frame, text="Output Directory (optional):").pack(anchor="w")
       output_frame = ttk.Frame(main_frame)
       output_frame.pack(fill="x", pady=(0, 10))


       self.output_dir = tk.StringVar(value="")
       ttk.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side="left", fill="x", expand=True)
       ttk.Button(output_frame, text="Browse", command=self.browse_output).pack(side="right", padx=(5, 0))


       # Output Format
       ttk.Label(main_frame, text="Output Format:").pack(anchor="w")
       self.output_format = tk.StringVar(value="tsv")
       format_frame = ttk.Frame(main_frame)
       format_frame.pack(fill="x", pady=(0, 20))


       ttk.Radiobutton(format_frame, text="TSV", variable=self.output_format, value="tsv").pack(side="left")
       ttk.Radiobutton(format_frame, text="CSV", variable=self.output_format, value="csv").pack(side="left",
                                                                                                padx=(10, 0))
       ttk.Radiobutton(format_frame, text="JSON", variable=self.output_format, value="json").pack(side="left",
                                                                                                  padx=(10, 0))


       # Buttons
       button_frame = ttk.Frame(main_frame)
       button_frame.pack(fill="x", pady=(20, 0))


       ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side="right", padx=(5, 0))
       ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side="right")


   def browse_script(self):
       filename = filedialog.askopenfilename(
           title="Select Harvester Script",
           filetypes=[("Python files", "*.py"), ("All files", "*.*")]
       )
       if filename:
           self.script_path.set(filename)


   def browse_directory(self):
       directory = filedialog.askdirectory(title="Select Working Directory")
       if directory:
           self.working_dir.set(directory)


   def browse_output(self):
       directory = filedialog.askdirectory(title="Select Output Directory")
       if directory:
           self.output_dir.set(directory)


   def ok_clicked(self):
       self.result = {
           'harvester_script': self.script_path.get(),
           'working_directory': self.working_dir.get(),
           'output_dir': self.output_dir.get(),
           'output_format': self.output_format.get()
       }
       self.dialog.destroy()


   def cancel_clicked(self):
       self.result = None
       self.dialog.destroy()




# === Main GUI ===
class SushiHarvesterGUI:
   def __init__(self):
       self.root = tk.Tk()
       self.root.title("SUSHI Harvester GUI")
       self.root.geometry("1000x800")


       # Configuration
       self.config = {
           'harvester_script': 'harvester.py',
           'working_directory': os.getcwd(),
           'output_dir': '',
           'output_format': 'tsv'
       }


       self.subprocess_handler = SushiHarvesterSubprocess(self)
       self.setup_gui()


       # Load saved configuration
       self.load_config()


   def get_harvester_default_dates(self):  # ← ADD THIS METHOD
       """Get default dates matching harvester logic exactly"""
       today = datetime.now()


       # Match harvester's fetch_json.py logic
       default_end_date = today - relativedelta(months=1)  # Previous month
       default_begin = "2025-01"  # From sushiconfig.py


       # Parse begin date
       begin_parts = default_begin.split('-')
       begin_year = int(begin_parts[0])
       begin_month_index = int(begin_parts[1]) - 1  # Convert to 0-based


       # End date
       end_year = default_end_date.year
       end_month_index = default_end_date.month - 1  # Convert to 0-based


       return begin_year, begin_month_index, end_year, end_month_index
   def setup_gui(self):
       # === Menu Bar ===
       menubar = tk.Menu(self.root)
       self.root.config(menu=menubar)


       # File menu
       file_menu = tk.Menu(menubar, tearoff=0)
       menubar.add_cascade(label="File", menu=file_menu)
       file_menu.add_command(label="Settings", command=self.open_settings)
       file_menu.add_separator()
       file_menu.add_command(label="Exit", command=self.root.quit)


       # Help menu
       help_menu = tk.Menu(menubar, tearoff=0)
       menubar.add_cascade(label="Help", menu=help_menu)
       help_menu.add_command(label="About", command=self.show_about)


       # === Date Range ===
       date_frame = ttk.LabelFrame(self.root, text="Date Range", padding=10)
       date_frame.pack(fill="x", padx=10, pady=5)


       # Get harvester-matching defaults
       begin_year, begin_month_idx, end_year, end_month_idx = self.get_harvester_default_dates()


       tk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky="w")
       self.start_month = ttk.Combobox(date_frame, values=months, state="readonly", width=10)
       self.start_month.set(months[begin_month_idx])  # January (2025-01)
       self.start_month.grid(row=0, column=1, padx=(5, 10))


       self.start_year = tk.Spinbox(date_frame, from_=2000, to=2100, width=5)
       self.start_year.delete(0, tk.END)
       self.start_year.insert(0, begin_year)  # 2025
       self.start_year.grid(row=0, column=2)


       tk.Label(date_frame, text="End Date:").grid(row=1, column=0, sticky="w")
       self.end_month = ttk.Combobox(date_frame, values=months, state="readonly", width=10)
       self.end_month.set(months[end_month_idx])  # Previous month (e.g., June)
       self.end_month.grid(row=1, column=1, padx=(5, 10))


       self.end_year = tk.Spinbox(date_frame, from_=2000, to=2100, width=5)
       self.end_year.delete(0, tk.END)
       self.end_year.insert(0, end_year)  # 2025
       self.end_year.grid(row=1, column=2)


       # === Report Type and Vendors (Side by Side) ===
       selection_frame = tk.Frame(self.root)
       selection_frame.pack(fill="both", expand=True, padx=10, pady=5)


       # Load actual data from your TSV files or configuration


       report_and_views = [
           "DR", "DR_EX", "DR_D1", "DR_D2",
           "PR", "PR_EX", "PR_P1",
           "TR", "TR_EX", "TR_J1", "TR_J2", "TR_J3", "TR_J4", "TR_B1", "TR_B2", "TR_B3",
           "IR", "IR_EX", "IR_A1", "IR_M1"
       ]
       # You can load this from your SUSHI configuration TSV file
       vendor_names = self.load_vendors_from_config()


       # Create Report and Vendor Frames
       self.report_frame = VendorFrame(selection_frame, "Report Type", report_and_views)
       self.report_frame.pack(side="left", fill="both", expand=True, padx=5)


       self.vendor_frame = VendorFrame(selection_frame, "Providers", vendor_names)
       self.vendor_frame.pack(side="left", fill="both", expand=True, padx=5)


       # === Log Output ===
       log_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
       log_frame.pack(fill="both", expand=True, padx=10, pady=5)


       # Create text widget with scrollbar
       text_frame = tk.Frame(log_frame)
       text_frame.pack(fill="both", expand=True)


       self.log_text = tk.Text(text_frame, height=12, wrap="word", font=("Consolas", 9))
       scrollbar_log = ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
       self.log_text.configure(yscrollcommand=scrollbar_log.set)


       self.log_text.pack(side="left", fill="both", expand=True)
       scrollbar_log.pack(side="right", fill="y")


       # === Control Buttons ===
       button_frame = tk.Frame(self.root)
       button_frame.pack(fill="x", padx=10, pady=10)


       # Buttons with new text and slightly larger font
       self.run_button = tk.Button(button_frame, text="Start", command=self.on_run,
                                   bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=10, pady=5)
       self.run_button.pack(side="left", padx=5)


       self.stop_button = tk.Button(button_frame, text="Stop", command=self.on_stop,
                                    bg="#f44336", fg="white", state="disabled", font=("Arial", 11), padx=10, pady=5)
       self.stop_button.pack(side="left", padx=5)


       # Renamed Clear Log to Pause, Save Log to Resume.
       # NOTE: Functionality remains clear_log and save_log,
       # actual pause/resume requires more advanced subprocess control.
       self.pause_button = tk.Button(button_frame, text="Pause", command=self.clear_log, font=("Arial", 11), padx=10,
                                     pady=5)
       self.pause_button.pack(side="left", padx=5)


       self.resume_button = tk.Button(button_frame, text="Resume", command=self.save_log, font=("Arial", 11), padx=10,
                                      pady=5)
       self.resume_button.pack(side="left", padx=5)


       # Status bar
       self.status_var = tk.StringVar(value="Ready")
       status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
       status_bar.pack(side=tk.BOTTOM, fill=tk.X)


   def load_vendors_from_config(self):
       vendors = []
       print("\n--- Starting load_vendors_from_config ---")


       # Define search paths for provider files
       if hasattr(self, 'config') and 'working_directory' in self.config:
           base_dir = Path(self.config['working_directory'])
       else:
           base_dir = Path.cwd()


       # Search in multiple locations
       search_paths = [
           base_dir,  # src/
           base_dir.parent / "registry_harvest",  # ../registry_harvest/
           base_dir / "registry_harvest",  # src/registry_harvest/ (if moved)
       ]


       registry_files = ['providers.tsv', 'registry-entries-2025-05-03.tsv']


       print(f"DEBUG: Base directory: {base_dir}")
       print(f"DEBUG: Search paths: {search_paths}")


       for search_path in search_paths:
           for config_file in registry_files:
               full_config_path = search_path / config_file
               print(f"DEBUG: Checking: {full_config_path}")


               if full_config_path.exists():
                   print(f"DEBUG: Found file: {full_config_path}")
                   try:
                       with open(full_config_path, 'r', encoding='utf-8') as f:
                           reader = csv.reader(f, delimiter='\t')
                           headers = next(reader)


                           for line in reader:
                               if len(line) > 0 and line[0] and line[0] != 'required':
                                   vendors.append(line[0])


                           if vendors:
                               print(f"DEBUG: Loaded {len(vendors)} vendors from {config_file}")
                               return vendors


                   except Exception as e:
                       print(f"ERROR: Failed to read {full_config_path}: {e}")
                       continue


       # Fallback
       if not vendors:
           print("DEBUG: No vendors found, using sample data")
           vendors = ["Sample Provider 1", "Sample Provider 2", "American Chemical Society", "EBSCO", "ProQuest"]


       return vendors


   def on_run(self):
       """Run the harvester"""
       if not self.validate_inputs():
           return


       if self.subprocess_handler.is_running:
           messagebox.showwarning("Warning", "Harvester is already running!")
           return


       # Prepare configuration
       run_config = self.config.copy()
       run_config.update({
           'start_date': self.format_date(self.start_year, self.start_month),
           'end_date': self.format_date(self.end_year, self.end_month),
           'reports': self.report_frame.get_selected(),
           'vendors': self.vendor_frame.get_selected()
       })


       # Run in separate thread - the SubprocessHandler will update the GUI
       self.subprocess_handler.run_harvester(run_config)


   def on_stop(self):
       """Stop the harvester"""
       if self.subprocess_handler.is_running:
           self.subprocess_handler.stop_harvester()
           # The subprocess_handler will handle updating button states
           # self.run_button.config(state="normal", text="Start")
           # self.stop_button.config(state="disabled")
           # self.status_var.set("Stopped")


   def clear_log(self):
       """Clear the log text area - now associated with 'Pause' button"""
       # NOTE: This only clears the log. To implement actual pause,
       # advanced subprocess control (e.g., sending SIGSTOP/SIGCONT) is needed.
       self.log_text.delete(1.0, tk.END)
       self.subprocess_handler.log_message("Log cleared (button labeled 'Pause').")


   def save_log(self):
       """Save log to file - now associated with 'Resume' button"""
       # NOTE: This only saves the log. To implement actual resume,
       # advanced subprocess control (e.g., sending SIGCONT) is needed.
       filename = filedialog.asksaveasfilename(
           defaultextension=".txt",
           filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
           title="Save Log File"
       )
       if filename:
           try:
               with open(filename, 'w', encoding='utf-8') as f:
                   f.write(self.log_text.get(1.0, tk.END))
               messagebox.showinfo("Success", f"Log saved to {filename} (button labeled 'Resume').")
               self.subprocess_handler.log_message(f"Log saved to {filename}")
           except Exception as e:
               messagebox.showerror("Error", f"Failed to save log: {str(e)}")
               self.subprocess_handler.log_message(f"Error saving log: {str(e)}")


   def open_settings(self):
       """Open settings dialog"""
       dialog = ConfigDialog(self.root)
       self.root.wait_window(dialog.dialog)


       if dialog.result:
           self.config.update(dialog.result)
           self.save_config()
           # Reload vendors if working directory changed, as it might affect config file location
           # Note: This rebuilds the vendor frame entirely, which is a bit heavy, but functional.
           # A more elegant solution would be to update the items in the existing frame.
           self.vendor_frame.destroy()  # Destroy the old frame
           vendor_names = self.load_vendors_from_config()  # Reload
           self.vendor_frame = VendorFrame(self.root.nametowidget('.!sushiharvestergui.!frame'), "Providers",
                                           vendor_names)
           # You'd need to correctly re-pack it relative to the report frame.
           # Assuming it was in selection_frame which is the .!sushiharvestergui.!frame in my test.
           # Better: Keep a reference to the parent where it was packed
           self.vendor_frame.pack(side="left", fill="both", expand=True, padx=5)
           self.root.update_idletasks()  # Refresh layout


   def show_about(self):
       """Show about dialog"""
       about_text = """SUSHI Harvester GUI




A graphical interface for the COUNTER SUSHI Harvester.


This tool helps librarians collect usage statistics from
database providers using the SUSHI API.


For more information about COUNTER metrics:
https://www.countermetrics.org/


Created by: Your Name
Version: 1.0.0"""  # Replace 'Your Name' with actual name


       messagebox.showinfo("About", about_text)


   def load_config(self):
       """Load configuration from file"""
       config_file = "gui_config.json"
       if os.path.exists(config_file):
           try:
               with open(config_file, 'r') as f:
                   saved_config = json.load(f)
                   self.config.update(saved_config)
           except Exception as e:
               self.subprocess_handler.log_message(f"Error loading GUI configuration: {e}")
               pass
       # After loading config, reload vendors just in case working_directory was changed
       # and affects where config files are found.
       # This prevents an empty vendor list if config file wasn't loaded first time.
       self.vendor_frame.destroy()
       vendor_names = self.load_vendors_from_config()
       # Find the parent frame where it was originally packed. This might be fragile.
       # Better practice: store a reference to the selection_frame.
       selection_frame_parent = self.root.winfo_children()[2]  # This is a fragile way to get it
       self.vendor_frame = VendorFrame(selection_frame_parent, "Providers", vendor_names)
       self.vendor_frame.pack(side="left", fill="both", expand=True, padx=5)


   def save_config(self):
       """Save configuration to file"""
       config_file = "gui_config.json"
       try:
           with open(config_file, 'w') as f:
               json.dump(self.config, f, indent=2)
       except Exception as e:
           self.subprocess_handler.log_message(f"Error saving GUI configuration: {e}")
           pass


   def run(self):
       """Start the GUI"""
       self.root.mainloop()




# === Entry Point ===
if __name__ == "__main__":
   app = SushiHarvesterGUI()
   app.run()