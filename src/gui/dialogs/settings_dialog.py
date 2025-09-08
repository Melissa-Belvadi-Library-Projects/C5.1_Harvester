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
    """
    Modal dialog for configuring application settings.
    Features change detection, reset to defaults, and smart close behavior.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setFixedSize(500, 450)

        # Configuration management
        # Uses the  ConfigManager helper to read the config file (current_config.py).
        # Loads those values into fields, so when the dialog opens, everything matches current settings.
        self.config_manager = ConfigManager()
        self.config_data = self.config_manager.load_config()

        # Store original values for change detection
        self.original_values = {}

        # Build user interface
        self.setup_ui()

        # Store original values after UI is built
        self.store_original_values()

    def get_default_config(self):
        """
        Returns the default configuration values.
        Used by Reset to Defaults functionality.
        """
        return {
            'sqlite_filename': 'counterdata.db',
            'data_table': 'usage_data',
            'error_log_file': 'errorlog.txt',
            'json_dir': 'json_folder',
            'tsv_dir': 'tsv_folder',
            'providers_file': 'providers.tsv',
            'save_empty_report': False,
            'always_include_header_metric_types': True,
            'default_begin': '2025-01'
        }

    def setup_ui(self):
        """Creates and arranges all configuration controls."""
        main_layout = QVBoxLayout(self)

        # Grid layout for configuration fields
        fields_layout = QGridLayout()
        fields_layout.setHorizontalSpacing(12)
        fields_layout.setVerticalSpacing(10)

        self.fields = {}
        row = 0

        # SQLite Database File setting
        fields_layout.addWidget(QLabel("SQLite Database File:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['sqlite_filename'] = QLineEdit(self.config_data.get('sqlite_filename', 'counterdata.db'))
        self.fields['sqlite_filename'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['sqlite_filename'], row, 1)

        # Data Table Name setting
        row += 1
        fields_layout.addWidget(QLabel("Data Table Name:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['data_table'] = QLineEdit(self.config_data.get('data_table', 'usage_data'))
        self.fields['data_table'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['data_table'], row, 1)

        # Error Log File setting
        row += 1
        fields_layout.addWidget(QLabel("Error Log File:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['error_log_file'] = QLineEdit(self.config_data.get('error_log_file', 'errorlog.txt'))
        self.fields['error_log_file'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['error_log_file'], row, 1)

        # JSON Directory setting
        row += 1
        fields_layout.addWidget(QLabel("JSON Directory:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['json_dir'] = QLineEdit(self.config_data.get('json_dir', 'json_folder'))
        self.fields['json_dir'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['json_dir'], row, 1)

        # TSV Directory setting
        row += 1
        fields_layout.addWidget(QLabel("TSV Directory:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['tsv_dir'] = QLineEdit(self.config_data.get('tsv_dir', 'tsv_folder'))
        self.fields['tsv_dir'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['tsv_dir'], row, 1)

        # Providers File setting
        row += 1
        fields_layout.addWidget(QLabel("Providers File:"), row, 0, Qt.AlignmentFlag.AlignRight)
        self.fields['providers_file'] = QLineEdit(self.config_data.get('providers_file', ''))
        self.fields['providers_file'].setFixedWidth(150)
        fields_layout.addWidget(self.fields['providers_file'], row, 1)

        # Save Empty Reports checkbox
        row += 1
        self.fields['save_empty_report'] = QCheckBox("Save Empty Reports")
        self.fields['save_empty_report'].setChecked(self.config_data.get('save_empty_report', False))
        fields_layout.addWidget(self.fields['save_empty_report'], row, 1, Qt.AlignmentFlag.AlignLeft)

        # Always Include Header Metric Types checkbox
        row += 1
        self.fields['always_include_header_metric_types'] = QCheckBox("Always Include Header Metric Types")
        self.fields['always_include_header_metric_types'].setChecked(
            self.config_data.get('always_include_header_metric_types', True))
        fields_layout.addWidget(self.fields['always_include_header_metric_types'], row, 1, Qt.AlignmentFlag.AlignLeft)

        # Default Begin Date setting
        row += 1
        fields_layout.addWidget(QLabel("Default Begin Date:"), row, 0, Qt.AlignmentFlag.AlignRight)

        months = list(calendar.month_name)[1:]
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
        year_spin.setFixedWidth(85)

        # Container for date widgets
        date_layout = QHBoxLayout()
        date_layout.addWidget(month_combo)
        date_layout.addWidget(year_spin)
        date_widget = QWidget()
        date_widget.setLayout(date_layout)
        fields_layout.addWidget(date_widget, row, 1, Qt.AlignmentFlag.AlignLeft)

        # Store references to date widgets
        self.fields['default_begin_month'] = month_combo
        self.fields['default_begin_year'] = year_spin

        fields_layout.setColumnStretch(2, 1)
        main_layout.addLayout(fields_layout)

        # Button layout - now with three buttons
        button_layout = QHBoxLayout()

        # Help button on left
        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self.show_settings_help)
        button_layout.addWidget(help_btn)

        # Stretch to center the main buttons
        button_layout.addStretch()

        # Main action buttons
        save_btn = QPushButton("Save")
        reset_btn = QPushButton("Reset to Defaults")
        close_btn = QPushButton("Close")

        # Connect button actions
        save_btn.clicked.connect(self.save_changes)
        reset_btn.clicked.connect(self.reset_to_defaults)
        close_btn.clicked.connect(self.close_dialog)

        # Add buttons with spacing
        button_layout.addWidget(save_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(reset_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

    def store_original_values(self):
        """
        Stores the current field values for change detection.
        Called after UI setup and after successful saves.
        """
        self.original_values = {
            'sqlite_filename': self.fields['sqlite_filename'].text(),
            'data_table': self.fields['data_table'].text(),
            'error_log_file': self.fields['error_log_file'].text(),
            'json_dir': self.fields['json_dir'].text(),
            'tsv_dir': self.fields['tsv_dir'].text(),
            'providers_file': self.fields['providers_file'].text(),
            'save_empty_report': self.fields['save_empty_report'].isChecked(),
            'always_include_header_metric_types': self.fields['always_include_header_metric_types'].isChecked(),
            'default_begin_month': self.fields['default_begin_month'].currentText(),
            'default_begin_year': self.fields['default_begin_year'].value()
        }

    def has_changes(self):
        """
        Checks if any field values have changed from their original values.

        Returns:
            bool: True if changes detected, False otherwise
        """
        current_values = {
            'sqlite_filename': self.fields['sqlite_filename'].text(),
            'data_table': self.fields['data_table'].text(),
            'error_log_file': self.fields['error_log_file'].text(),
            'json_dir': self.fields['json_dir'].text(),
            'tsv_dir': self.fields['tsv_dir'].text(),
            'providers_file': self.fields['providers_file'].text(),
            'save_empty_report': self.fields['save_empty_report'].isChecked(),
            'always_include_header_metric_types': self.fields['always_include_header_metric_types'].isChecked(),
            'default_begin_month': self.fields['default_begin_month'].currentText(),
            'default_begin_year': self.fields['default_begin_year'].value()
        }

        return current_values != self.original_values

    def reset_to_defaults(self):
        """
        Resets all fields to their default values.
        Asks for confirmation before proceeding.
        """
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "<b>Reset to Defaults</b><br><br>"
            "This will reset current settings to their default values and will save that change.<br><br>"
        
            "Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            defaults = self.get_default_config()

            # Reset all text fields
            self.fields['sqlite_filename'].setText(defaults['sqlite_filename'])
            self.fields['data_table'].setText(defaults['data_table'])
            self.fields['error_log_file'].setText(defaults['error_log_file'])
            self.fields['json_dir'].setText(defaults['json_dir'])
            self.fields['tsv_dir'].setText(defaults['tsv_dir'])
            self.fields['providers_file'].setText(defaults['providers_file'])

            # Reset checkboxes
            self.fields['save_empty_report'].setChecked(defaults['save_empty_report'])
            self.fields['always_include_header_metric_types'].setChecked(defaults['always_include_header_metric_types'])

            # Reset date fields
            default_begin = defaults['default_begin']
            if '-' in default_begin:
                default_year, default_month = default_begin.split('-')
                self.fields['default_begin_year'].setValue(int(default_year))
                self.fields['default_begin_month'].setCurrentIndex(int(default_month) - 1)

    def close_dialog(self):
        """
        Handles Close button click with change detection.
        Prompts user if unsaved changes exist.
        """
        if self.has_changes():
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Unsaved Changes")
            msg_box.setText("You have unsaved changes.")
            msg_box.setInformativeText("What would you like to do?")
            msg_box.setIcon(QMessageBox.Icon.Question)

            save_and_close_btn = msg_box.addButton("Save and Close", QMessageBox.ButtonRole.AcceptRole)
            cancel_and_close_btn = msg_box.addButton("Cancel and Close", QMessageBox.ButtonRole.RejectRole)

            msg_box.setDefaultButton(save_and_close_btn)
            msg_box.exec()
            clicked_button = msg_box.clickedButton()

            if clicked_button == save_and_close_btn:
                success, updated_config = self.save_changes()  # <--- GET THE RETURNED DATA
                if success:
                    self.accept()
            elif clicked_button == cancel_and_close_btn:
                self.reject()
        else:
            self.reject()
    def show_settings_help(self):
        """Opens help documentation for configuration settings."""
        help_url = "https://github.com/yourusername/yourrepo/blob/main/docs/sushiconfig-options.md"

        reply = QMessageBox.question(
            self,
            "Settings Help",
            "<b>Setting Help</b><br><br>"
            "This will open the settings page in your web browser.<br>"
            "Do you want to continue?",
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

    def save_changes(self):
        """
        Saves all configuration changes to file.

        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Build default_begin date from dropdowns
            months = list(calendar.month_name)[1:]
            default_month = months.index(self.fields['default_begin_month'].currentText()) + 1
            default_year = self.fields['default_begin_year'].value()
            default_begin = f"{default_year}-{default_month:02d}"

            # Collect all configuration data
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

            # Save configuration
            self.config_manager.save_config(config_data)

            # Update original values after successful save
            self.store_original_values()

            # Show success message
            QMessageBox.information(self, "Success", "Configuration saved successfully!")

            return True, config_data

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")
            return False

    def closeEvent(self, event):
        """
        Handles window close event (X button).
        Redirects to close_dialog for consistent behavior.
        """
        # Cancel the default close event
        event.ignore()

        # Use our custom close handling
        self.close_dialog()