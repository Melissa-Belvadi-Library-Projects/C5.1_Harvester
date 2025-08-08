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
from tkinter import Toplevel

months = list(calendar.month_name)[1:]


class VendorFrame(ttk.LabelFrame):
    def __init__(self, parent, title, items):
        super().__init__(parent, text=title, padding=10)
        self.vars = []

        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", pady=(0, 5))
        tk.Button(button_frame, text="Select All", command=self.select_all, font=("Arial", 14), padx=5, pady=2).pack(
            side="left", padx=5)
        tk.Button(button_frame, text="Deselect All", command=self.deselect_all, font=("Arial", 14), padx=5,
                  pady=2).pack(side="left", padx=5)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, height=200)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        list_frame = tk.Frame(canvas)

        list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
        self.update_idletasks()  # makes ui slightly faster

    def deselect_all(self):
        for _, var in self.vars:
            var.set(False)
        self.update_idletasks()


class SushiHarvesterSubprocess:
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.process = None
        self.is_running = False
        self._harvester_thread = None

    def log_message(self, message):
        if message.strip():
            self.gui.root.after(0, lambda: self.gui.log_text.insert(tk.END, f"{message}\n"))
            self.gui.root.after(0, lambda: self.gui.log_text.see(tk.END))

    def build_command(self, config):
        harvester_script = config.get('harvester_script', 'getcounter.py')
        cmd = [sys.executable, harvester_script]
        cmd.extend(['--start-date', config['start_date']])
        cmd.extend(['--end-date', config['end_date']])
        if config['reports']:
            cmd.extend(['--reports', ','.join(config['reports'])])
        if config['vendors']:
            cmd.extend(['--vendors', ','.join(config['vendors'])])
        if config.get('output_format'):
            cmd.extend(['--format', config['output_format']])
        if config.get('output_dir'):
            cmd.extend(['--output-dir', config['output_dir']])
        cmd.append('--verbose')
        return cmd

    def _run_harvester_thread(self, config):
        try:
            self.is_running = True
            self.gui.root.after(0, lambda: self.gui.start_button.config(text="RUNNING...", state="disabled"))
            self.gui.root.after(0, lambda: self.gui.stop_button.config(state="normal"))
            self.gui.root.after(0, lambda: self.gui.status_var.set("Running harvester..."))

            self.log_message(f"Starting SUSHI Harvester at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            cmd = self.build_command(config)
            self.log_message(f"Command: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, universal_newlines=True,
                cwd=config.get('working_directory', '.')
            )

            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.log_message(line.rstrip())
                if not self.is_running:
                    break
                if self.process.poll() is not None:
                    break

            if self.process.poll() is None:
                self.process.wait()

            if self.process.returncode == 0:
                self.log_message("✅ Harvester completed successfully!")
                self.gui.root.after(0, lambda: messagebox.showinfo("Success", "Harvester completed successfully!"))
            else:
                self.log_message(f"❌ Harvester failed with exit code: {self.process.returncode}")
                self.gui.root.after(0, lambda: messagebox.showerror("Error",
                                                                    f"Harvester failed with exit code: {self.process.returncode}"))

        except FileNotFoundError:
            self.log_message("❌ Error: Harvester script not found!")
            self.gui.root.after(0, lambda: messagebox.showerror("Error", "Harvester script not found!"))
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            self.gui.root.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))
        finally:
            self.is_running = False
            self.process = None
            self._harvester_thread = None
            self.gui.root.after(0, lambda: self.gui.start_button.config(state="normal", text="START"))
            self.gui.root.after(0, lambda: self.gui.stop_button.config(state="disabled"))
            self.gui.root.after(0, lambda: self.gui.status_var.set("Ready"))

    def run_harvester(self, config):
        if self._harvester_thread and self._harvester_thread.is_alive():
            return
        self._harvester_thread = threading.Thread(target=self._run_harvester_thread, args=(config,))
        self._harvester_thread.daemon = True
        self._harvester_thread.start()

    def stop_harvester(self):
        if self.process and self.is_running:
            self.log_message("🛑 Stopping harvester...")
            self.is_running = False
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.log_message("🛑 Harvester stopped")
            self.gui.root.after(0, lambda: self.gui.start_button.config(state="normal", text="START"))
            self.gui.root.after(0, lambda: self.gui.stop_button.config(state="disabled"))
            self.gui.root.after(0, lambda: self.gui.status_var.set("Stopped"))
            self.process = None


class ConfigDialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Harvester Script:").pack(anchor="w")
        script_frame = ttk.Frame(main_frame)
        script_frame.pack(fill="x", pady=(0, 10))
        self.script_path = tk.StringVar(value="getcounter.py")
        ttk.Entry(script_frame, textvariable=self.script_path).pack(side="left", fill="x", expand=True)
        ttk.Button(script_frame, text="Browse", command=self.browse_script).pack(side="right", padx=(5, 0))

        ttk.Label(main_frame, text="Working Directory:").pack(anchor="w")
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill="x", pady=(0, 10))
        self.working_dir = tk.StringVar(value=os.getcwd())
        ttk.Entry(dir_frame, textvariable=self.working_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side="right", padx=(5, 0))

        ttk.Label(main_frame, text="Output Format:").pack(anchor="w")
        self.output_format = tk.StringVar(value="tsv")
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(fill="x", pady=(0, 20))
        ttk.Radiobutton(format_frame, text="TSV", variable=self.output_format, value="tsv").pack(side="left")
        ttk.Radiobutton(format_frame, text="CSV", variable=self.output_format, value="csv").pack(side="left",
                                                                                                 padx=(10, 0))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side="right")

        x = (self.dialog.winfo_screenwidth() // 2) - 250
        y = (self.dialog.winfo_screenheight() // 2) - 150
        self.dialog.geometry(f"+{x}+{y}")

    def browse_script(self):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if filename:
            self.script_path.set(filename)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.working_dir.set(directory)

    def ok_clicked(self):
        script = self.script_path.get()
        directory = self.working_dir.get()
        if not os.path.exists(script):
            messagebox.showerror("Error", "Harvester script not found!")
            return
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Working directory does not exist!")
            return
        self.result = {
            'harvester_script': script,
            'working_directory': directory,
            'output_format': self.output_format.get()
        }
        self.dialog.destroy()

    def cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


class SushiHarvesterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HARVESTER GUI")
        self.root.geometry("1000x800")

        self.config = {
            'harvester_script': 'getcounter.py',
            'working_directory': os.getcwd(),
            'output_format': 'tsv'
        }

        self.subprocess_handler = SushiHarvesterSubprocess(self)
        self.setup_gui()
        self.load_config()

    def get_default_dates(self):
        today = datetime.now()
        default_end_date = today - relativedelta(months=1)
        return 2025, 0, default_end_date.year, default_end_date.month - 1  # 0-based month indices

    def show_help_modal(self, title, info):
        """Show a help modal dialog with consistent styling"""
        modal = Toplevel(self.root)
        modal.title(title)
        modal.transient(self.root)
        modal.grab_set()
        modal.geometry("450x200")
        modal.resizable(False, False)

        # Main frame with padding
        main_frame = tk.Frame(modal, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Title label
        title_label = tk.Label(main_frame, text=title, font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Info text
        info_label = tk.Label(main_frame, text=info, wraplength=400, justify="left", font=("Arial", 10))
        info_label.pack(fill="both", expand=True, pady=(0, 15))

        # OK button
        ok_button = tk.Button(main_frame, text="OK", command=modal.destroy,
                              font=("Arial", 10), padx=20, pady=5)
        ok_button.pack(pady=(10, 0))

        # Center the modal
        x = self.root.winfo_rootx() + self.root.winfo_width() // 2 - 225
        y = self.root.winfo_rooty() + self.root.winfo_height() // 2 - 100
        modal.geometry(f"+{x}+{y}")

    def create_help_button(self, parent, help_text, title="Help"):
        """Create a consistent help button"""
        help_btn = tk.Button(
            parent,
            text="?",
            font=("Arial", 10, "bold"),
            command=lambda: self.show_help_modal(title, help_text),
            relief="raised",
            width=2,
            height=1,
            bg="#f0f0f0",
            fg="#333333"
        )
        return help_btn

    def setup_gui(self):
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_command(label="Exit", command=self.root.quit)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # Date Range Frame
        date_frame = ttk.LabelFrame(self.root, text="Date Range", padding=10)
        date_frame.pack(fill="x", padx=10, pady=5)

        begin_year, begin_month_idx, end_year, end_month_idx = self.get_default_dates()

        # Date range help button
        date_help_text = ("Select the date range for harvesting COUNTER reports. "
                          "Start date should be earlier than end date. "
                          "Most providers have data available from 2018 onwards.")
        date_help_btn = self.create_help_button(date_frame, date_help_text, "Date Range Help")
        date_help_btn.grid(row=0, column=4, rowspan=2, padx=(15, 0), sticky="n")

        # Date controls
        tk.Label(date_frame, text="Start:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=2)
        self.start_month = ttk.Combobox(date_frame, values=months, state="readonly", width=10)
        self.start_month.set(months[begin_month_idx])
        self.start_month.grid(row=0, column=1, padx=5, pady=2)
        self.start_year = tk.Spinbox(date_frame, from_=2000, to=2100, width=5, value=begin_year)
        self.start_year.grid(row=0, column=2, pady=2)

        tk.Label(date_frame, text="End:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=2)
        self.end_month = ttk.Combobox(date_frame, values=months, state="readonly", width=10)
        self.end_month.set(months[end_month_idx])
        self.end_month.grid(row=1, column=1, padx=5, pady=2)
        self.end_year = tk.Spinbox(date_frame, from_=2000, to=2100, width=5, value=end_year)
        self.end_year.grid(row=1, column=2, pady=2)

        # Selection Frames Container
        selection_container = tk.Frame(self.root)
        selection_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Left side - Report Types
        left_frame = tk.Frame(selection_container)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Report types header with help button
        report_header_frame = tk.Frame(left_frame)
        report_header_frame.pack(fill="x", pady=(0, 5))

        report_label = tk.Label(report_header_frame, text="Report Types", font=("Arial", 12, "bold"))
        report_label.pack(side="left")

        report_help_text = ("COUNTER report types define different usage statistics:\n\n"
                            "• DR: Database Reports\n"
                            "• IR: Item Reports (articles, chapters)\n"
                            "• PR: Platform Reports\n"
                            "• TR: Title Reports (journals, books)\n\n"
                            "Select the report types you need for your analysis.")
        report_help_btn = self.create_help_button(report_header_frame, report_help_text, "Report Types Help")
        report_help_btn.pack(side="right")

        # Report types list
        report_types = [
            "DR", "DR_D1", "DR_D2",
            "IR", "IR_A1", "IR_M1",
            "PR", "PR_P1",
            "TR", "TR_B1", "TR_B2", "TR_B3",
            "TR_J1", "TR_J2", "TR_J3", "TR_J4"
        ]

        self.report_frame = VendorFrame(left_frame, "", report_types)
        self.report_frame.pack(fill="both", expand=True)

        # Right side - Vendors/Providers
        right_frame = tk.Frame(selection_container)
        right_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        # Vendors header with help button
        vendor_header_frame = tk.Frame(right_frame)
        vendor_header_frame.pack(fill="x", pady=(0, 5))

        vendor_label = tk.Label(vendor_header_frame, text="Select Providers", font=("Arial", 12, "bold"))
        vendor_label.pack(side="left")

        vendor_help_text = ("Select the content providers/vendors from whom you want to harvest "
                            "usage statistics. These are typically database providers like "
                            "EBSCO, ProQuest, Springer, etc.\n\n"
                            "You can select multiple providers to harvest data from all of them "
                            "in a single operation.")
        vendor_help_btn = self.create_help_button(vendor_header_frame, vendor_help_text, "Providers Help")
        vendor_help_btn.pack(side="right")

        # Vendors list
        vendors = self.load_vendors()
        self.vendor_frame = VendorFrame(right_frame, "", vendors)
        self.vendor_frame.pack(fill="both", expand=True)

        # Progress Log
        log_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        text_frame = tk.Frame(log_frame)
        text_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(text_frame, height=12, wrap="word", font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Control Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=15)

        # Left side buttons
        self.start_button = tk.Button(
            button_frame,
            text="START",
            command=self.on_start,
            font=("Arial", 14, "bold"),
            padx=15,
            pady=5,
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(
            button_frame,
            text="STOP",
            command=self.on_stop,
            font=("Arial", 14, "bold"),
            padx=15,
            pady=5,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(
            button_frame,
            text="CLEAR",
            command=self.clear_log,
            font=("Arial", 14, "bold"),
            padx=15,
            pady=5,
        )
        self.clear_button.pack(side="left", padx=5)

        # Right side - Settings with help
        settings_frame = tk.Frame(button_frame)
        settings_frame.pack(side="right")

        settings_help_text = ("Configure application settings including:\n\n"
                              "• Harvester script location\n"
                              "• Working directory\n"
                              "• Output format (TSV or CSV)\n"
                              "• Other preferences")
        settings_help_btn = self.create_help_button(settings_frame, settings_help_text, "Settings Help")
        settings_help_btn.pack(side="right", padx=(0, 5))

        self.settings_button = tk.Button(
            settings_frame,
            text="SETTINGS",
            command=self.open_settings,
            font=("Arial", 14, "bold"),
            padx=15,
            pady=5,
        )
        self.settings_button.pack(side="right")

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def clear_log(self):
        """Clear the progress log"""
        self.log_text.delete(1.0, tk.END)

    def load_vendors(self):
        vendors = []
        search_paths = [Path.cwd(), Path.cwd().parent / "registry_harvest"]
        config_files = ['providers.tsv', 'registry-entries-2025-05-03.tsv']

        for path in search_paths:
            for config_file in config_files:
                full_path = path / config_file
                if full_path.exists():
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f, delimiter='\t')
                            next(reader)  # Skip header
                            for line in reader:
                                if len(line) > 0 and line[0] and line[0] != 'required':
                                    vendors.append(line[0])
                        if vendors:
                            return vendors
                    except Exception:
                        continue

        return ["Sample Provider 1", "Sample Provider 2", "EBSCO", "ProQuest", "Springer"]

    def on_start(self):
        if not self.validate_inputs():
            return
        if self.subprocess_handler.is_running:
            messagebox.showwarning("Warning", "Harvester is already running!")
            return

        config = self.config.copy()
        config.update({
            'start_date': self.format_date(self.start_year, self.start_month),
            'end_date': self.format_date(self.end_year, self.end_month),
            'reports': self.report_frame.get_selected(),
            'vendors': self.vendor_frame.get_selected()
        })
        self.subprocess_handler.run_harvester(config)

    def on_stop(self):
        if self.subprocess_handler.is_running:
            self.subprocess_handler.stop_harvester()

    def validate_inputs(self):
        if not self.report_frame.get_selected():
            messagebox.showerror("Error", "Please select at least one report type.")
            return False
        if not self.vendor_frame.get_selected():
            messagebox.showerror("Error", "Please select at least one provider.")
            return False

        # Validate date range
        try:
            start_year = int(self.start_year.get())
            start_month = months.index(self.start_month.get()) + 1
            end_year = int(self.end_year.get())
            end_month = months.index(self.end_month.get()) + 1
            start_dt = datetime(start_year, start_month, 1)
            end_dt = datetime(end_year, end_month, 1)
            if start_dt > end_dt:
                messagebox.showerror("Error", "Start date must be before End date.")
                return False
        except Exception:
            messagebox.showerror("Error", "Invalid date input.")
            return False

        return True

    def format_date(self, year_widget, month_widget):
        year = year_widget.get()
        month_name = month_widget.get()
        month_num = months.index(month_name) + 1
        return f"{year}-{month_num:02d}"

    def open_settings(self):
        dialog = ConfigDialog(self.root)
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            self.config.update(dialog.result)
            self.save_config()

    def show_about(self):
        messagebox.showinfo("About",
                            "SUSHI Harvester GUI\n\nA tool for collecting COUNTER usage statistics\nfrom database providers via SUSHI API.")

    def load_config(self):
        config_file = "gui_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self.config.update(json.load(f))
            except Exception:
                pass

    def save_config(self):
        try:
            with open("gui_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SushiHarvesterGUI()
    app.run()