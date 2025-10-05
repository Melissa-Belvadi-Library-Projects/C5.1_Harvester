# ui/dialogs/settings_dialog.py
"""Settings dialog with state management."""

import calendar
import webbrowser
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QComboBox, QSpinBox, QPushButton,
    QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPalette, QColor

from help_file import get_help_url


class SushiConfigDialog(QDialog):
    """
    Settings dialog with state-based approach.
    Emits signals instead of directly saving to files.
    """

    # Signal emitted when configuration changes
    configChanged = pyqtSignal(dict)

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None, parent=None):
        #Optional[Dict[str, Any]]mMeans this parameter can either be: A dictionary (Dict[str, Any]) — e.g. config values Or None (no state provided).
        """Initialize with optional initial state."""
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setFixedSize(500, 450)

        # State management
        #state = the current values of the UI and the data it represents.

        self._state = initial_state.copy() if initial_state else {}
        self._original_state = {}
        self._updating = False

        # Build UI
        self._setup_ui()

        # Apply initial state
        if initial_state:
            self.set_state(initial_state)

    def _setup_ui(self):
        """Create and arrange configuration controls."""
        main_layout = QVBoxLayout(self)

        # Grid layout for fields
        fields_layout = QGridLayout()
        fields_layout.setHorizontalSpacing(12)
        fields_layout.setVerticalSpacing(10)

        self.fields = {}
        row = 0

        # SQLite Database File
        fields_layout.addWidget(QLabel("SQLite Database File:"), row, 0,
                                Qt.AlignmentFlag.AlignRight)
        self.fields['sqlite_filename'] = QLineEdit()
        self.fields['sqlite_filename'].setFixedWidth(170)
        fields_layout.addWidget(self.fields['sqlite_filename'], row, 1)

        # Data Table Name
        row += 1
        fields_layout.addWidget(QLabel("Data Table Name:"), row, 0,
                                Qt.AlignmentFlag.AlignRight)
        self.fields['data_table'] = QLineEdit()
        self.fields['data_table'].setFixedWidth(170)
        fields_layout.addWidget(self.fields['data_table'], row, 1)

        # Error Log File
        row += 1
        fields_layout.addWidget(QLabel("Info Log File:"), row, 0,
                                Qt.AlignmentFlag.AlignRight)
        self.fields['error_log_file'] = QLineEdit()
        self.fields['error_log_file'].setFixedWidth(170)
        fields_layout.addWidget(self.fields['error_log_file'], row, 1)

        # JSON Directory
        row += 1
        fields_layout.addWidget(QLabel("JSON Directory:"), row, 0,
                                Qt.AlignmentFlag.AlignRight)
        self.fields['json_dir'] = QLineEdit()
        self.fields['json_dir'].setFixedWidth(170)
        fields_layout.addWidget(self.fields['json_dir'], row, 1)

        # TSV Directory
        row += 1
        fields_layout.addWidget(QLabel("TSV Directory:"), row, 0,
                                Qt.AlignmentFlag.AlignRight)
        self.fields['tsv_dir'] = QLineEdit()
        self.fields['tsv_dir'].setFixedWidth(170)
        fields_layout.addWidget(self.fields['tsv_dir'], row, 1)

        # Providers File
        row += 1
        fields_layout.addWidget(QLabel("Providers File:"), row, 0,
                                Qt.AlignmentFlag.AlignRight)
        self.fields['providers_file'] = QLineEdit()
        self.fields['providers_file'].editingFinished.connect(self._on_providers_file_changed) #updates the main window providers once saved
        self.fields['providers_file'].setFixedWidth(170)
        fields_layout.addWidget(self.fields['providers_file'], row, 1)

        # Save Empty Reports checkbox
        row += 1
        self.fields['save_empty_report'] = QCheckBox("Save Empty Reports")
        fields_layout.addWidget(self.fields['save_empty_report'], row, 1,
                                Qt.AlignmentFlag.AlignLeft)

        # Always Include Header Metric Types checkbox
        row += 1
        self.fields['always_include_header_metric_types'] = QCheckBox(
            "Always Include Header Metric Types"
        )
        fields_layout.addWidget(self.fields['always_include_header_metric_types'],
                                row, 1, Qt.AlignmentFlag.AlignLeft)

        # Default Begin Date
        row += 1
        fields_layout.addWidget(QLabel("Default Begin Date:"), row, 0,
                                Qt.AlignmentFlag.AlignRight)

        # Month dropdown
        self.month_combo = QComboBox()
        months = list(calendar.month_name)[1:]
        self.month_combo.addItems(months)
        self.month_combo.setFixedWidth(100)

        # Year spinbox
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setFixedWidth(85)

        # Container for date widgets
        date_layout = QHBoxLayout()
        date_layout.addWidget(self.month_combo)
        date_layout.addWidget(self.year_spin)
        date_widget = QWidget()
        date_widget.setLayout(date_layout)
        fields_layout.addWidget(date_widget, row, 1, Qt.AlignmentFlag.AlignLeft)

        fields_layout.setColumnStretch(2, 1)
        main_layout.addLayout(fields_layout)

        # Connect change signals AFTER creating all widgets
        for key, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._on_field_changed)
            elif isinstance(widget, QCheckBox):
                widget.toggled.connect(self._on_field_changed)

        self.month_combo.currentIndexChanged.connect(self._on_field_changed)
        self.year_spin.valueChanged.connect(self._on_field_changed)

        # Button layout
        button_layout = QHBoxLayout()

        # Help button
        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)

        button_layout.addStretch()

        # Main action buttons
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_changes)
        self.save_btn.setEnabled(False)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self._handle_close)

        button_layout.addWidget(self.save_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(reset_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

        # Store original state after UI is built
        self._original_state = self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """
        Get current state as a dictionary.

        Returns:
            Dict containing all configuration values that the user enters
        """
        # Build default_begin from dropdowns
        month_idx = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()
        default_begin = f"{year}-{month_idx:02d}"

        return {
            'sqlite_filename': self.fields['sqlite_filename'].text(),
            'data_table': self.fields['data_table'].text(),
            'error_log_file': self.fields['error_log_file'].text(),
            'json_dir': self.fields['json_dir'].text(),
            'tsv_dir': self.fields['tsv_dir'].text(),
            'providers_file': self.fields['providers_file'].text(),
            'save_empty_report': self.fields['save_empty_report'].isChecked(),
            'always_include_header_metric_types':
                self.fields['always_include_header_metric_types'].isChecked(),
            'default_begin': default_begin
        }

    def set_state(self, state: Dict[str, Any]):
        """
        Update widget state from external source.

        Args:
            state: Dictionary with configuration values
        """
        self._updating = True
        self._state = state.copy()

        try:
            # Update text fields
            for key in ['sqlite_filename', 'data_table', 'error_log_file',
                        'json_dir', 'tsv_dir', 'providers_file']:
                if key in state and key in self.fields:
                    self.fields[key].setText(str(state[key]))

            # Update checkboxes
            if 'save_empty_report' in state:
                self.fields['save_empty_report'].setChecked(state['save_empty_report'])

            if 'always_include_header_metric_types' in state:
                self.fields['always_include_header_metric_types'].setChecked(
                    state['always_include_header_metric_types']
                )

            # Update date fields
            if 'default_begin' in state:
                default_begin = state['default_begin']
                if '-' in default_begin:
                    year, month = default_begin.split('-')
                    self.year_spin.setValue(int(year))
                    self.month_combo.setCurrentIndex(int(month) - 1)

        finally:
            self._updating = False
            self._original_state = self.get_state()
            self.save_btn.setEnabled(False)

    def _on_field_changed(self):
        """Handle field value changes."""
        if self._updating:
            return

        # Enable save button if values changed
        current_state = self.get_state()
        has_changes = current_state != self._original_state # notices if there are some changes  with the intial state

        #enables  that the user cannot save an empty field
        required = ["sqlite_filename", "data_table", "providers_file","error_log_file", "json_dir", "tsv_dir"]
        all_filled = all(current_state[field].strip() for field in required)


        self.save_btn.setEnabled(has_changes and all_filled)


    def _on_providers_file_changed(self):

        """Emit configChanged immediately when providers_file changes."""

        providers_file = self.fields['providers_file'].text()

        # Build current config and emit it
        config = self.get_state()

        #self.configChanged.emit(config) removed automatic emission


    def _save_changes(self):
        """Save configuration changes."""
        config = self.get_state()

        # Emit signal instead of saving directly
        self.configChanged.emit(config)

        # Update original state
        self._original_state = config.copy()
        self.save_btn.setEnabled(False)
        # note the changeshappen with the method on_field_changed

    def _reset_to_defaults(self):
        """Reset all fields to default values."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Reset to Defaults")
        msg_box.setText("All settings reset to their to their default values\n"
                        "Do you want to reset?")
        #msg_box.setIcon(QMessageBox.Icon.Question)

        # Adds custom clean buttons (no mnemonics, no underlines)
        yes_btn = msg_box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        no_btn = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)

        msg_box.setDefaultButton(no_btn)
        msg_box.exec()

        if msg_box.clickedButton() == yes_btn:
            defaults = self._get_defaults()
            self.set_state(defaults)
            self._on_field_changed()
            self.save_btn.setEnabled(True)

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values from default_config.py file."""
        try:
            # Imports the ConfigRepository that already handles config file parsing
            from core.repositories import ConfigRepository

            # Create a repository pointing to default_config.py( almost like an arrow looking to fetch info from it)
            default_repo = ConfigRepository()

            # Try to find default_config.py specifically
            from pathlib import Path

            search_paths = [
                Path(__file__).parent.parent / "default_config.py",
                Path(__file__).parent.parent.parent / "default_config.py",
                Path.cwd() / "default_config.py",
            ]

            for path in search_paths:
                if path.exists():
                    default_repo.config_file = path
                    break

            # Load and return the defaults
            return default_repo.load()

        except Exception as e:
            # Fallback to hardcoded if something goes wrong
            print(f"Warning: Using hardcoded defaults: {e}")
            return {
                'sqlite_filename': 'counterdata.db',
                'data_table': 'usage_data',
                'error_log_file': 'infolog.txt',
                'json_dir': 'json_folder',
                'tsv_dir': 'tsv_folder',
                'providers_file': 'providers.tsv',
                'save_empty_report': False,
                'always_include_header_metric_types': True,
                'default_begin': '2025-01'
            }

    def _handle_close(self):
        """Handle close button click."""

        FIELD_LABELS = {
            "sqlite_filename": "SQLite Database File",
            "data_table": "Data Table Name",
            "error_log_file": "Info Log File",
            "json_dir": "JSON Directory",
            "tsv_dir": "TSV Directory",
            "providers_file": "Providers File"
        }

        required = ["sqlite_filename", "data_table", "providers_file", "error_log_file", "json_dir", "tsv_dir"]

        current_state = self.get_state()
        empty_fields = [field for field in required if not current_state[field].strip()]
        missing_labels = [FIELD_LABELS.get(field, field) for field in empty_fields]


        if empty_fields:
            # Notifies user which fields are missing
            QMessageBox.information(
                self, "Missing Required Fields",
                f"You must fill these fields before closing:\n"
                f"{', '.join(missing_labels)}"
            )
            return  # Don’t close at all


        if self.save_btn.isEnabled():
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Unsaved Changes")
            msg_box.setText("You have unsaved changes\n"
                            "What would you like to do?")
            #msg_box.setIcon(QMessageBox.Icon.Question)

            # Add custom buttons with clear text
            save_close_btn = msg_box.addButton("Save and Close", QMessageBox.ButtonRole.AcceptRole)
            close_without_save_btn = msg_box.addButton("Close Without Saving", QMessageBox.ButtonRole.DestructiveRole)

            msg_box.setDefaultButton(save_close_btn)
            msg_box.exec()

            if msg_box.clickedButton() == save_close_btn:
                self._save_changes()
                self.accept()
            elif msg_box.clickedButton() == close_without_save_btn:
                self.reject()
            # If cancel, do nothing (dialog stays open)
        else:
            self.reject()

    def _show_help(self):
        """Show help documentation for settings dialog."""

        help_url = get_help_url('settings')

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Settings Help")
        msg_box.setText("Open Settings Help documentation in browser?")
        #msg_box.setIcon(QMessageBox.Icon.Question)


        yes_btn = msg_box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        no_btn = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)

        msg_box.setDefaultButton(yes_btn)
        msg_box.exec()

        if msg_box.clickedButton() == yes_btn:
            try:
                webbrowser.open(help_url)
            except Exception as e:
                QMessageBox.information(
                    self, "Help",
                    f"Please visit:\n{help_url}\n\n"
                    f"(Could not open browser: {e})"
                )

    def closeEvent(self, event):
        """Handle window close event (X button)."""
        if self.save_btn.isEnabled():
            event.ignore()
            self._handle_close()
        else:
            event.accept()