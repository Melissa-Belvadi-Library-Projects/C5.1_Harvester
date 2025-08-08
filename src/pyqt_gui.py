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

class SushiConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SUSHI Configuration")
        self.setFixedSize(500, 400)
        self.config_data = self.load_sushi_config()

        layout = QVBoxLayout()

        self.fields = {}

        layout.addWidget(QLabel("SQLite Database File:"))
        self.fields['sqlite_filename'] = QLineEdit(self.config_data.get('sqlite_filename', 'counterdata.db'))
        layout.addWidget(self.fields['sqlite_filename'])

        layout.addWidget(QLabel("Data Table Name:"))
        self.fields['data_table'] = QLineEdit(self.config_data.get('data_table', 'usage_data'))
        layout.addWidget(self.fields['data_table'])

        layout.addWidget(QLabel("Error Log File:"))
        self.fields['error_log_file'] = QLineEdit(self.config_data.get('error_log_file', 'errorlog.txt'))
        layout.addWidget(self.fields['error_log_file'])

        layout.addWidget(QLabel("JSON Directory:"))
        self.fields['json_dir'] = QLineEdit(self.config_data.get('json_dir', 'json_folder'))
        layout.addWidget(self.fields['json_dir'])

        layout.addWidget(QLabel("TSV Directory:"))
        self.fields['tsv_dir'] = QLineEdit(self.config_data.get('tsv_dir', 'tsv_folder'))
        layout.addWidget(self.fields['tsv_dir'])

        layout.addWidget(QLabel("Providers File:"))
        self.fields['providers_file'] = QLineEdit(self.config_data.get('providers_file', 'providers.tsv'))
        layout.addWidget(self.fields['providers_file'])

        self.fields['save_empty_report'] = QCheckBox("Save Empty Reports")
        self.fields['save_empty_report'].setChecked(self.config_data.get('save_empty_report', False))
        layout.addWidget(self.fields['save_empty_report'])

        self.fields['always_include_header_metric_types'] = QCheckBox("Always Include Header Metric Types")
        self.fields['always_include_header_metric_types'].setChecked(
            self.config_data.get('always_include_header_metric_types', True))
        layout.addWidget(self.fields['always_include_header_metric_types'])

        layout.addWidget(QLabel("Default Begin Date (YYYY-MM):"))
        self.fields['default_begin'] = QLineEdit(self.config_data.get('default_begin', '2025-01'))
        layout.addWidget(self.fields['default_begin'])

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

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
            config_content = f"""#####  Various constant values that you can change as you like

sqlite_filename = '{self.fields['sqlite_filename'].text()}'
data_table = '{self.fields['data_table'].text()}'
error_log_file = '{self.fields['error_log_file'].text()}'
json_dir = '{self.fields['json_dir'].text()}'
tsv_dir = '{self.fields['tsv_dir'].text()}'
providers_file = '{self.fields['providers_file'].text()}'
save_empty_report = {self.fields['save_empty_report'].isChecked()}
always_include_header_metric_types = {self.fields['always_include_header_metric_types'].isChecked()}
default_begin = '{self.fields['default_begin'].text()}'
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
        self.harvester_thread = None
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.create_menu_bar()

        date_group = QGroupBox("Date Range")
        date_layout = QGridLayout()
        begin_year, begin_month_idx, end_year, end_month_idx = self.get_default_dates()
        months = list(calendar.month_name)[1:]

        date_layout.addWidget(QLabel("Start:"), 0, 0)
        self.start_month = QComboBox()
        self.start_month.addItems(months)
        self.start_month.setCurrentIndex(begin_month_idx)
        date_layout.addWidget(self.start_month, 0, 1)

        self.start_year = QSpinBox()
        self.start_year.setRange(2000, 2100)
        self.start_year.setValue(begin_year)
        date_layout.addWidget(self.start_year, 0, 2)

        date_layout.addWidget(QLabel("End:"), 1, 0)
        self.end_month = QComboBox()
        self.end_month.addItems(months)
        self.end_month.setCurrentIndex(end_month_idx)
        date_layout.addWidget(self.end_month, 1, 1)

        self.end_year = QSpinBox()
        self.end_year.setRange(2000, 2100)
        self.end_year.setValue(end_year)
        date_layout.addWidget(self.end_year, 1, 2)


        date_group.setLayout(date_layout)
        main_layout.addWidget(date_group)

        selection_layout = QHBoxLayout()
        report_types = [
            "DR", "DR_D1", "DR_D2", "IR", "IR_A1", "IR_M1",
            "PR", "PR_P1", "TR", "TR_B1", "TR_B2", "TR_B3",
            "TR_J1", "TR_J2", "TR_J3", "TR_J4"
        ]
        self.report_frame = VendorFrame("Report Types", report_types)
        selection_layout.addWidget(self.report_frame)

        vendors = self.load_vendors()
        self.vendor_frame = VendorFrame("Select Providers", vendors)
        selection_layout.addWidget(self.vendor_frame)
        main_layout.addLayout(selection_layout)

        log_group = QGroupBox("Progress")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Arial", 9))
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("START")
        self.start_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.start_button.clicked.connect(self.on_start)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("STOP")
        self.stop_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.on_stop)
        button_layout.addWidget(self.stop_button)

        self.clear_button = QPushButton("CLEAR")
        self.clear_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()

        self.help_button = QPushButton("HELP")
        self.help_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)

        self.settings_button = QPushButton("SETTINGS")
        self.settings_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)

        main_layout.addLayout(button_layout)

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
        if not self.validate_inputs():
            return
        if self.harvester_thread and self.harvester_thread.isRunning():
            QMessageBox.warning(self, "Warning", "Harvester is already running!")
            return
        config = {
            'start_date': self.format_date(self.start_year.value(), self.start_month.currentText()),
            'end_date': self.format_date(self.end_year.value(), self.end_month.currentText()),
            'reports': self.report_frame.get_selected(),
            'vendors': self.vendor_frame.get_selected()
        }
        self.harvester_thread = HarvesterThread(config)
        self.harvester_thread.log_signal.connect(self.log_message)
        self.harvester_thread.finished_signal.connect(self.on_harvester_finished)
        self.harvester_thread.start()
        self.start_button.setText("RUNNING...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_bar.showMessage("Running harvester...")

    def on_stop(self):
        if self.harvester_thread and self.harvester_thread.isRunning():
            self.harvester_thread.stop()
            self.harvester_thread.wait()
            self.on_harvester_finished(False, -1)

    def on_harvester_finished(self, success, return_code):
        if success:
            QMessageBox.information(self, "Success", "Harvester completed successfully!")
        else:
            QMessageBox.critical(self, "Error", f"Harvester failed with exit code: {return_code}")
        self.start_button.setText("START")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage("Ready")

    def log_message(self, message):
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()

    def clear_log(self):
        self.log_text.clear()

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
        dialog = SushiConfigDialog(self)
        dialog.exec()

    def show_help(self):
        QMessageBox.information(self, "Help", "Help documentation coming soon...")

    def show_about(self):
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