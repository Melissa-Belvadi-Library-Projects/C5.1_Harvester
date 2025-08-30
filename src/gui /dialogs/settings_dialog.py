import calendar
import webbrowser
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QComboBox, QSpinBox, QPushButton,
    QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from ..utils.config_manager import ConfigManager


class SushiConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SUSHI Configuration")
        self.setFixedSize(500, 400)

        self.config_manager = ConfigManager()
        self.config_data = self.config_manager.load_config()

        self.setup_ui()

    def setup_ui(self):
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
        self.fields['sqlite_filename'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['sqlite_filename'], row, 1)

        row += 1
        # Data Table Name
        fields_layout.addWidget(QLabel("Data Table Name:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['data_table'] = QLineEdit(self.config_data.get('data_table', 'usage_data'))
        self.fields['data_table'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['data_table'], row, 1)

        row += 1
        # Error Log File
        fields_layout.addWidget(QLabel("Error Log File:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['error_log_file'] = QLineEdit(self.config_data.get('error_log_file', 'errorlog.txt'))
        self.fields['error_log_file'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['error_log_file'], row, 1)

        row += 1
        # JSON Directory
        fields_layout.addWidget(QLabel("JSON Directory:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['json_dir'] = QLineEdit(self.config_data.get('json_dir', 'json_folder'))
        self.fields['json_dir'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['json_dir'], row, 1)

        row += 1
        # TSV Directory
        fields_layout.addWidget(QLabel("TSV Directory:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['tsv_dir'] = QLineEdit(self.config_data.get('tsv_dir', 'tsv_folder'))
        self.fields['tsv_dir'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['tsv_dir'], row, 1)

        row += 1
        # Providers File
        fields_layout.addWidget(QLabel("Providers File:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['providers_file'] = QLineEdit(self.config_data.get('providers_file'))
        self.fields['providers_file'].setFixedWidth(150)
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

        # Help button on the left
        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self.show_settings_help)
        button_layout.addWidget(help_btn)

        button_layout.addStretch()

        # Save and Cancel buttons on the right with spacing
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.save_changes)

        button_layout.addWidget(save_btn)
        button_layout.addSpacing(10)  # Add space between Save and Cancel
        button_layout.addWidget(cancel_btn)

        main_layout.addLayout(button_layout)

    def save_changes(self):
        try:
            # Build the default_begin value from dropdowns
            months = list(calendar.month_name)[1:]
            default_month = months.index(self.fields['default_begin_month'].currentText()) + 1
            default_year = self.fields['default_begin_year'].value()
            default_begin = f"{default_year}-{default_month:02d}"

            config_data = {
                'sqlite_filename': self.fields['sqlite_filename'].text(),
                'data_table': self.fields['data_table'].text(),
                'error_log_file': self.fields['error_log_file'].text(),
                'json_dir': self.fields['json_dir'].text(),
                'tsv_dir': self.fields['tsv_dir'].text(),
                'providers_file': self.fields['providers_file'].text(),
                'save_empty_report': self.fields['save_empty_report'].isChecked(),
                'always_include_header_metric_types': self.fields['always_include_header_metric_types'].isChecked(),
                'default_begin': default_begin
            }

            self.config_manager.save_config(config_data)
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

    def show_settings_help(self):
        """Show help for configuration settings"""
        import webbrowser

        help_url = "https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester/blob/main/docs/sushiconfig-options.md"

        reply = QMessageBox.question(
            self, "Configuration Help",
            "Open configuration documentation?\n\n"
            "Open in browser?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                webbrowser.open(help_url)
            except Exception as e:
                QMessageBox.information(
                    self, "Help Documentation",
                    f"Please visit the configuration guide at:\n{help_url}\n\n"
                    f"(Could not open browser automatically: {e})"
                )