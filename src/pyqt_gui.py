import sys
import csv
import os
import subprocess
import calendar
from datetime import datetime
from pathlib import Path
from dateutil.relativedelta import relativedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QComboBox, QSpinBox, QPushButton, QTextEdit,
    QCheckBox, QScrollArea, QGroupBox, QMenuBar,
    QMessageBox, QFileDialog, QDialog, QLineEdit, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QAction


class VendorFrame(QGroupBox):
    def __init__(self, title, items):
        super().__init__(title)
        self.setMinimumHeight(250)
        self.checkboxes = []

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Deselect All")
        select_all_btn.setFont(QFont("Arial", 10))
        deselect_all_btn.setFont(QFont("Arial", 10))

        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn.clicked.connect(self.deselect_all)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for item in items:
            checkbox = QCheckBox(item)
            self.checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def get_selected(self):
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

    def select_all(self):
        for cb in self.checkboxes:
            cb.setChecked(True)

    def deselect_all(self):
        for cb in self.checkboxes:
            cb.setChecked(False)


class HarvesterThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, int)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.process = None

    def run(self):
        try:
            harvester_script = 'getcounter.py'
            cmd = [sys.executable, harvester_script]
            cmd.extend(['--start-date', self.config['start_date']])
            cmd.extend(['--end-date', self.config['end_date']])

            if self.config['reports']:
                cmd.extend(['--reports', ','.join(self.config['reports'])])
            if self.config['vendors']:
                cmd.extend(['--vendors', ','.join(self.config['vendors'])])

            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, universal_newlines=True
            )

            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.log_signal.emit(line.rstrip())
                if self.process.poll() is not None:
                    break

            if self.process.poll() is None:
                self.process.wait()

            success = self.process.returncode == 0
            self.finished_signal.emit(success, self.process.returncode)

        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False, -1)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)


class ProgressDialog(QDialog):
    """
    Modal dialog that shows harvester progress and allows stopping the process.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Harvester Progress")
        self.setFixedSize(800, 600)

        # Make this dialog modal
        self.setModal(True)

        # Reference to harvester thread
        self.harvester_thread = None

        layout = QVBoxLayout(self)

        # Progress label
        self.status_label = QLabel("Preparing to start harvester...")
        self.status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.status_label)

        # Progress text area
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Arial", 9))
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.stop_button = QPushButton("STOP")
        self.stop_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.stop_button.clicked.connect(self.stop_harvester)
        button_layout.addWidget(self.stop_button)

        self.close_button = QPushButton("CLOSE")
        self.close_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.close_button.setEnabled(False)  # Disabled until harvester finishes
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def start_harvester(self, config):
        """Start the harvester with given configuration."""
        self.status_label.setText("Starting harvester...")

        # Create and configure harvester thread
        self.harvester_thread = HarvesterThread(config)
        self.harvester_thread.log_signal.connect(self.log_message)
        self.harvester_thread.finished_signal.connect(self.on_harvester_finished)

        # Start the thread
        self.harvester_thread.start()
        self.status_label.setText("Harvester running...")

    def log_message(self, message):
        """Add a message to the progress log."""
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()

    def stop_harvester(self):
        """Stop the running harvester."""
        if self.harvester_thread and self.harvester_thread.isRunning():
            self.status_label.setText("Stopping harvester...")
            self.harvester_thread.stop()
            self.harvester_thread.wait()
            self.on_harvester_finished(False, -1)

    def on_harvester_finished(self, success, return_code):
        """Handle harvester completion."""
        if success:
            self.status_label.setText("Harvester completed successfully!")
            self.log_message("\n=== HARVESTER COMPLETED SUCCESSFULLY ===")
            QMessageBox.information(self, "Success", "Harvester completed successfully!")
        else:
            self.status_label.setText("Harvester failed!")
            self.log_message(f"\n=== HARVESTER FAILED (Exit Code: {return_code}) ===")
            QMessageBox.critical(self, "Error", f"Harvester failed with exit code: {return_code}")

        # Enable close button and disable stop button
        self.stop_button.setEnabled(False)
        self.close_button.setEnabled(True)

    def closeEvent(self, event):
        """Handle window close event - ensure harvester is stopped."""
        if self.harvester_thread and self.harvester_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Harvester Running",
                "The harvester is still running. Do you want to stop it and close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_harvester()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class SushiConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SUSHI Configuration")
        self.setFixedSize(500, 400)
        self.config_data = self.load_sushi_config()

        main_layout = QVBoxLayout(self)

        # === Fields in Grid Layout ===
        fields_layout = QGridLayout()
        fields_layout.setHorizontalSpacing(12)
        fields_layout.setVerticalSpacing(10)

        self.fields = {}

        row = 0

        # SQLite Database File
        fields_layout.addWidget(QLabel("SQLite Database File:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['sqlite_filename'] = QLineEdit(self.config_data.get('sqlite_filename', 'counterdata.db'))
        self.fields['sqlite_filename'].setFixedWidth(100)
        fields_layout.addWidget(self.fields['sqlite_filename'], row, 1)

        row += 1
        # Data Table Name
        fields_layout.addWidget(QLabel("Data Table Name:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['data_table'] = QLineEdit(self.config_data.get('data_table', 'usage_data'))
        self.fields['data_table'].setFixedWidth(100)
        fields_layout.addWidget(self.fields['data_table'], row, 1)

        row += 1
        # Error Log File
        fields_layout.addWidget(QLabel("Error Log File:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['error_log_file'] = QLineEdit(self.config_data.get('error_log_file', 'errorlog.txt'))
        self.fields['error_log_file'].setFixedWidth(100)
        fields_layout.addWidget(self.fields['error_log_file'], row, 1)

        row += 1
        # JSON Directory
        fields_layout.addWidget(QLabel("JSON Directory:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['json_dir'] = QLineEdit(self.config_data.get('json_dir', 'json_folder'))
        self.fields['json_dir'].setFixedWidth(100)
        fields_layout.addWidget(self.fields['json_dir'], row, 1)

        row += 1
        # TSV Directory
        fields_layout.addWidget(QLabel("TSV Directory:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['tsv_dir'] = QLineEdit(self.config_data.get('tsv_dir', 'tsv_folder'))
        self.fields['tsv_dir'].setFixedWidth(100)
        fields_layout.addWidget(self.fields['tsv_dir'], row, 1)

        row += 1
        # Providers File
        fields_layout.addWidget(QLabel("Providers File:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['providers_file'] = QLineEdit(self.config_data.get('providers_file', 'providers.tsv'))
        self.fields['providers_file'].setFixedWidth(100)
        fields_layout.addWidget(self.fields['providers_file'], row, 1)

        # --- Checkboxes in a separate row for clarity ---
        row += 1
        self.fields['save_empty_report'] = QCheckBox("Save Empty Reports")
        self.fields['save_empty_report'].setChecked(self.config_data.get('save_empty_report', False))
        fields_layout.addWidget(self.fields['save_empty_report'], row, 1, Qt.AlignmentFlag.AlignLeft)

        row += 1
        self.fields['always_include_header_metric_types'] = QCheckBox("Always Include Header Metric Types")
        self.fields['always_include_header_metric_types'].setChecked(
            self.config_data.get('always_include_header_metric_types', True))
        fields_layout.addWidget(self.fields['always_include_header_metric_types'], row, 1, Qt.AlignmentFlag.AlignLeft)

        # --- Default Begin Date: Month and Year Dropdowns ---
        row += 1
        fields_layout.addWidget(QLabel("Default Begin Date:"), row, 0, Qt.AlignmentFlag.AlignRight)

        months = list(calendar.month_name)[1:]  # ["January", ... "December"]
        default_begin = self.config_data.get('default_begin', '2025-01')
        if '-' in default_begin:
            default_year, default_month = default_begin.split('-')
        else:
            default_year, default_month = ('2025', '01')
        # Month dropdown
        month_combo = QComboBox()
        month_combo.addItems(months)
        month_combo.setCurrentIndex(int(default_month) - 1)
        month_combo.setFixedWidth(100)
        # Year spinbox
        year_spin = QSpinBox()
        year_spin.setRange(2000, 2100)
        year_spin.setValue(int(default_year))
        year_spin.setFixedWidth(60)
        # Horizontal layout for date widgets
        date_layout = QHBoxLayout()
        date_layout.addWidget(month_combo)
        date_layout.addWidget(year_spin)
        date_widget = QWidget()
        date_widget.setLayout(date_layout)
        fields_layout.addWidget(date_widget, row, 1, Qt.AlignmentFlag.AlignLeft)
        # Store references
        self.fields['default_begin_month'] = month_combo
        self.fields['default_begin_year'] = year_spin

        # Add column stretch to push widgets to the left
        fields_layout.setColumnStretch(2, 1)

        main_layout.addLayout(fields_layout)

        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        save_btn = QPushButton("Save Changes")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)  # Save is added first
        button_layout.addWidget(cancel_btn)  # Cancel is added second
        main_layout.addLayout(button_layout)

    def load_sushi_config(self):
        config = {}
        try:
            if os.path.exists('sushiconfig.py'):
                with open('sushiconfig.py', 'r') as f:
                    content = f.read()
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip("'\"")
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        config[key] = value
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not load sushiconfig.py: {e}")
        return config

    def save_changes(self):
        try:
            # Build the default_begin value from dropdowns
            months = list(calendar.month_name)[1:]
            default_month = months.index(self.fields['default_begin_month'].currentText()) + 1
            default_year = self.fields['default_begin_year'].value()
            default_begin = f"{default_year}-{default_month:02d}"

            config_content = f"""#####  Various constant values that you can change as you like

sqlite_filename = '{self.fields['sqlite_filename'].text()}'
data_table = '{self.fields['data_table'].text()}'
error_log_file = '{self.fields['error_log_file'].text()}'
json_dir = '{self.fields['json_dir'].text()}'
tsv_dir = '{self.fields['tsv_dir'].text()}'
providers_file = '{self.fields['providers_file'].text()}'
save_empty_report = {self.fields['save_empty_report'].isChecked()}
always_include_header_metric_types = {self.fields['always_include_header_metric_types'].isChecked()}
default_begin = '{default_begin}'
"""
            with open('sushiconfig.py', 'w') as f:
                f.write(config_content)

            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")


class SushiHarvesterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HARVESTER GUI")
        self.setGeometry(100, 100, 1000, 800)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.create_menu_bar()

        # === Date Range Section ===
        date_group = QGroupBox("Select Date Range")
        date_layout = QGridLayout()
        begin_year, begin_month_idx, end_year, end_month_idx = self.get_default_dates()
        months = list(calendar.month_name)[1:]

        date_layout.setHorizontalSpacing(6)
        date_layout.setVerticalSpacing(3)
        date_layout.setContentsMargins(5, 5, 5, 5)

        date_layout.addWidget(QLabel("Start:"), 0, 0)
        self.start_month = QComboBox()
        self.start_month.addItems(months)
        self.start_month.setCurrentIndex(begin_month_idx)
        self.start_month.setFixedWidth(90)
        date_layout.addWidget(self.start_month, 0, 1)

        self.start_year = QSpinBox()
        self.start_year.setRange(2000, 2100)
        self.start_year.setValue(begin_year)
        self.start_year.setFixedWidth(65)
        date_layout.addWidget(self.start_year, 0, 2)

        date_layout.addWidget(QLabel("End:"), 1, 0)
        self.end_month = QComboBox()
        self.end_month.addItems(months)
        self.end_month.setCurrentIndex(end_month_idx)
        self.end_month.setFixedWidth(90)
        date_layout.addWidget(self.end_month, 1, 1)

        self.end_year = QSpinBox()
        self.end_year.setRange(2000, 2100)
        self.end_year.setValue(end_year)
        self.end_year.setFixedWidth(65)
        date_layout.addWidget(self.end_year, 1, 2)

        date_layout.setColumnStretch(3, 1)  # This ensures widgets are left-aligned

        date_group.setLayout(date_layout)
        main_layout.addWidget(date_group)

        # === Selection Section ===
        selection_layout = QHBoxLayout()
        report_types = [
            "DR", "DR_D1", "DR_D2", "IR", "IR_A1", "IR_M1",
            "PR", "PR_P1", "TR", "TR_B1", "TR_B2", "TR_B3",
            "TR_J1", "TR_J2", "TR_J3", "TR_J4"
        ]
        self.report_frame = VendorFrame("Select Report Types", report_types)
        selection_layout.addWidget(self.report_frame)

        vendors = self.load_vendors()
        self.vendor_frame = VendorFrame("Select Providers", vendors)
        selection_layout.addWidget(self.vendor_frame)
        main_layout.addLayout(selection_layout)

        # === Button Section ===
        button_layout = QHBoxLayout()

        # START button on the left
        self.start_button = QPushButton("START")
        self.start_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.start_button.clicked.connect(self.on_start)
        button_layout.addWidget(self.start_button)

        # Add stretch to push other buttons to the right
        button_layout.addStretch()

        # Right-aligned buttons: VENDORS, SETTINGS, HELP
        self.vendors_button = QPushButton("VENDORS")
        self.vendors_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.vendors_button.clicked.connect(self.show_vendors)
        button_layout.addWidget(self.vendors_button)

        self.settings_button = QPushButton("SETTINGS")
        self.settings_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)

        self.help_button = QPushButton("HELP")
        self.help_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)

        main_layout.addLayout(button_layout)

        # === Status Bar ===
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        self.setStatusBar(self.status_bar)

    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def get_default_dates(self):
        today = datetime.now()
        default_end_date = today - relativedelta(months=1)
        return 2025, 0, default_end_date.year, default_end_date.month - 1

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
                            next(reader)
                            for line in reader:
                                if len(line) > 0 and line[0] and line[0] != 'required':
                                    vendors.append(line[0])
                        if vendors:
                            return vendors
                    except Exception:
                        continue
        return ["Sample Provider 1", "Sample Provider 2", "EBSCO", "ProQuest", "Springer"]

    def on_start(self):
        """Handle START button click - validate inputs and show progress dialog."""
        if not self.validate_inputs():
            return

        # Build configuration for harvester
        config = {
            'start_date': self.format_date(self.start_year.value(), self.start_month.currentText()),
            'end_date': self.format_date(self.end_year.value(), self.end_month.currentText()),
            'reports': self.report_frame.get_selected(),
            'vendors': self.vendor_frame.get_selected()
        }

        # Create and show progress dialog
        progress_dialog = ProgressDialog(self)
        progress_dialog.start_harvester(config)
        progress_dialog.exec()  # Show modal dialog

    def validate_inputs(self):
        if not self.report_frame.get_selected():
            QMessageBox.critical(self, "Error", "Please select at least one report type.")
            return False
        if not self.vendor_frame.get_selected():
            QMessageBox.critical(self, "Error", "Please select at least one provider.")
            return False
        try:
            start_month = list(calendar.month_name)[1:].index(self.start_month.currentText()) + 1
            end_month = list(calendar.month_name)[1:].index(self.end_month.currentText()) + 1
            start_dt = datetime(self.start_year.value(), start_month, 1)
            end_dt = datetime(self.end_year.value(), end_month, 1)
            if start_dt > end_dt:
                QMessageBox.critical(self, "Error", "Start date must be before End date.")
                return False
        except Exception:
            QMessageBox.critical(self, "Error", "Invalid date input.")
            return False
        return True

    def format_date(self, year, month_name):
        months = list(calendar.month_name)[1:]
        month_num = months.index(month_name) + 1
        return f"{year}-{month_num:02d}"

    def open_settings(self):
        """Open the settings configuration dialog."""
        dialog = SushiConfigDialog(self)
        dialog.exec()

    def show_vendors(self):
        """Show information about vendors (placeholder)."""
        QMessageBox.information(self, "Vendors", "Vendor management  coming soon...")

    def show_help(self):
        """Show help information (placeholder)."""
        QMessageBox.information(self, "Help", "Help documentation coming soon...")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About",
                          "SUSHI Harvester GUI\n\n"
                          "A tool for collecting COUNTER usage statistics\n"
                          "from database providers via SUSHI API.")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = SushiHarvesterGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()