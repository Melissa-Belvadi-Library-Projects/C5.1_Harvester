"""Main application window with centralized state management and scrim overlay system."""

import sys
import uuid
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QDialog, QApplication
)
from PyQt6.QtCore import Qt

# Import core state management
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.state import AppState, AppSignals
from core.repositories import ConfigRepository, VendorRepository

from ui.dialogs.progress_dialog import ProgressDialog

# Import UI components
from ui.components.vendor_frame import VendorFrame
from ui.components.date_selector import DateSelector
from ui.dialogs.settings_dialog import SushiConfigDialog
from ui.dialogs.vendor_dialog import VendorManagementDialog
from help_file import get_help_url
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl



class SushiHarvesterGUI(QMainWindow):
    """
    Main application window with centralized state management and scrim overlay system.
    Acts as the controller, coordinating between UI components and data layer.
    """

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Window properties
        self.setWindowTitle("COUNTER 5.1 Harvester")
        self.setGeometry(100, 100, 1000, 800)

        # Initialize state management
        self.app_state = AppState()
        self.signals = AppSignals()

        # Initialize repositories
        self.config_repo = ConfigRepository()
        self.vendor_repo = VendorRepository()

        # Load initial state
        self._load_initial_state()

        # Create the scrim overlay widget (must be created before UI setup)
        self.scrim = QWidget(self)
        self.scrim.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.scrim.hide()  # Hidden by default

        # Build UI
        self._setup_ui()

        # Wire signals
        self._connect_signals()

        # Apply initial state to components
        self._apply_state_to_ui()

    def resizeEvent(self, event):
        """Ensure scrim covers entire window when resized."""
        super().resizeEvent(event)
        if hasattr(self, 'scrim'):
            self.scrim.resize(self.size())

    def show_modal_with_scrim(self, dialog):
        """Show a dialog with scrim effect."""
        # Resize and show scrim
        self.scrim.resize(self.size())
        self.scrim.show()
        self.scrim.raise_()  # Bring scrim above main content

        # Show dialog
        dialog.raise_()  # Dialog above scrim
        dialog.activateWindow()
        result = dialog.exec()

        # Hide scrim when dialog closes
        self.scrim.hide()

        return result

    def _load_initial_state(self):

        """Load initial configuration and vendor data."""
        # Load configuration
        config = self.config_repo.load()
        self.app_state.config = config


        # Update vendor repository with config
        if 'providers_file' in config:
            self.vendor_repo.providers_file = config['providers_file']

        # Load vendors in the main window
        vendors_data = self.vendor_repo.load()

#ensures each vendor has its unique ID
        for vendor in vendors_data:
            if 'Id' not in vendor or not vendor.get('Id'):
                vendor['Id'] = str(uuid.uuid4())

        self.app_state.vendors_data = vendors_data


        # Set default dates based on config
        self.app_state.dates = self.app_state._get_default_dates()

    def _setup_ui(self):

        """Create and arrange UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # === Date Range + Help Button Row ===
        date_layout = QHBoxLayout()

        # Date selector with initial state
        self.date_selector = DateSelector(initial_state=self.app_state.config)
        date_layout.addWidget(self.date_selector)

        date_layout.addStretch()

        # Help button
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self._show_help)
        date_layout.addWidget(self.help_button)

        main_layout.addLayout(date_layout)

        # === Report Types + Providers Section ===
        selection_layout = QHBoxLayout()

        # Available report types
        report_types = [
            "DR", "DR_D1", "DR_D2", "IR", "IR_A1", "IR_M1",
            "PR", "PR_P1", "TR", "TR_B1", "TR_B2", "TR_B3",
            "TR_J1", "TR_J2", "TR_J3", "TR_J4"
        ]

        # Get vendor names from state
        vendor_names = [v['Name'] for v in self.app_state.vendors_data
                        if v.get('Name', '').strip()]

        # Create selection frames
        self.vendor_frame = VendorFrame("Select Providers", vendor_names)
        selection_layout.addWidget(self.vendor_frame, stretch=2)

        self.report_frame = VendorFrame("Select Report Types", report_types)
        selection_layout.addWidget(self.report_frame, stretch=1)

        main_layout.addLayout(selection_layout)


        # Control Buttons
        first_button_layout = QHBoxLayout()

        # Push everything to the right
        first_button_layout.addStretch()

        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self._on_start)
        first_button_layout.addWidget(self.start_button)

        first_button_layout.addSpacing(15)  # Space between Start and Manage Providers

        # Manage Providers button
        self.vendors_button = QPushButton("Manage Providers")
        self.vendors_button.clicked.connect(self._show_vendors)
        first_button_layout.addWidget(self.vendors_button)

        first_button_layout.addSpacing(15)  # Space between Manage Providers and Settings

        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self._open_settings)
        first_button_layout.addWidget(self.settings_button)

        main_layout.addLayout(first_button_layout)
        main_layout.addSpacing(15)

        #  Exit Button Row
        second_button_layout = QHBoxLayout()
        second_button_layout.addStretch()

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self._handle_exit)
        second_button_layout.addWidget(self.exit_button)

        main_layout.addLayout(second_button_layout)

    def _connect_signals(self):
        """Wire up signals between components and state."""

        # Date selector signals
        self.date_selector.dateRangeChanged.connect(self._on_date_range_changed)

        # App-wide signals
        self.signals.configChanged.connect(self._on_config_changed)
        self.signals.vendorsChanged.connect(self._on_vendors_changed)
        self.signals.vendorsDataChanged.connect(self._on_vendors_data_changed)
        self.signals.reportsChanged.connect(self._on_reports_changed)
        self.signals.errorOccurred.connect(self._on_error)
        self.signals.saveRequested.connect(self._save_all_state)

    def _apply_state_to_ui(self):
        """Apply current state to all UI components."""
        # Update date selector
        self.date_selector.set_state({
            'default_begin': self.app_state.config.get('default_begin', '2025-01'),
            'start': self.app_state.dates.get('start'),
            'end': self.app_state.dates.get('end')
        })

        # Update vendor list
        vendor_names = [v['Name'] for v in self.app_state.vendors_data
                        if v.get('Name', '').strip()]


        # Check if vendor_frame has update_items method, otherwise recreate
        if hasattr(self.vendor_frame, 'update_items'):
            self.vendor_frame.update_items(vendor_names)
        else:
            # Fallback: recreate the frame if update method doesn't exist
            old_frame = self.vendor_frame
            self.vendor_frame = VendorFrame("Select Providers", vendor_names)


        # Apply selected items if any
        if self.app_state.selected_vendors:
            for vendor in self.app_state.selected_vendors:
                self.vendor_frame.select_item(vendor)

        if self.app_state.selected_reports:
            for report in self.app_state.selected_reports:
                self.report_frame.select_item(report)

    def _on_date_range_changed(self, start: str, end: str):
        """Handle date range changes from DateSelector."""
        # Update app state
        self.app_state.dates['start'] = start
        self.app_state.dates['end'] = end

        # Emit global signal
        self.signals.dateRangeChanged.emit(start, end)

    def _on_config_changed(self, config: dict):
        """Handle configuration changes."""



        # Update app state
        self.app_state.update_config(config)


        # Save to file
        self.config_repo.save(config)

        # Update vendor repository if providers file changed
        if 'providers_file' in config:

            self.vendor_repo.providers_file = config['providers_file']

            # Reload vendors

            vendors_data = self.vendor_repo.load()
            self.app_state.vendors_data = vendors_data
            #self._on_vendors_data_changed(vendors_data)


            vendor_names = [v['Name'] for v in vendors_data if v.get('Name', '').strip()]
            if hasattr(self.vendor_frame, 'update_items'):
                self.vendor_frame.update_items(vendor_names)

        # Update UI components
        self.date_selector.set_state({
            'default_begin': config.get('default_begin', '2025-01'),
            'start': self.app_state.dates.get('start'),
            'end': self.app_state.dates.get('end')
        })

    def _on_vendors_changed(self, vendor_names: list):
        """Handle vendor selection changes."""
        self.app_state.selected_vendors = vendor_names

    def _on_vendors_data_changed(self, vendors_data: list):
        """Handle vendor data changes."""
        # Update state
        self.app_state.vendors_data = vendors_data

#ensures all vendors have id before saving
        for vendor in vendors_data:
            if 'Id' not in vendor or not vendor.get('Id'):
                vendor['Id'] = str(uuid.uuid4())

        # Save to file
        self.vendor_repo.save(vendors_data)

        # Update UI
        vendor_names = [v['Name'] for v in vendors_data
                        if v.get('Name', '').strip()]

        # Check if update_items method exists
        if hasattr(self.vendor_frame, 'update_items'):

            self.vendor_frame.update_items(vendor_names)


    def _on_reports_changed(self, report_names: list):
        """Handle report selection changes."""
        self.app_state.selected_reports = report_names

    def _on_error(self, message: str):
        """Handle error messages."""
        QMessageBox.critical(self, "Error", message)

    def _save_all_state(self):
        """Save all current state to disk."""
        try:
            # Save config
            self.config_repo.save(self.app_state.config)

            # Save vendors
            self.vendor_repo.save(self.app_state.vendors_data)

            QMessageBox.information(self, "Success",
                                    "All settings saved")
        except Exception as e:
            self.signals.errorOccurred.emit(f"Failed to save: {e}")

    def _on_start(self):
        """Handle Start button click."""
        # Update selections in state
        self.app_state.selected_vendors = self.vendor_frame.get_selected()
        self.app_state.selected_reports = self.report_frame.get_selected()

        # Validate selections
        if not self.app_state.selected_reports:
            QMessageBox.critical(self, "Error",
                                 "Please select at least one report type.")
            return

        if not self.app_state.selected_vendors:
            QMessageBox.critical(self, "Error",
                                 "Please select at least one provider.")
            return

        # Validate dates
        is_valid, error_msg = self.date_selector.validate_dates()
        if not is_valid:
            QMessageBox.critical(self, "Error", error_msg)
            return

        # Create harvester config - simpler now!
        from dataclasses import dataclass

        @dataclass
        class HarvesterConfig:
            start_date: str
            end_date: str
            vendors: list
            reports: list
            config: dict

        config = HarvesterConfig(
            start_date=self.app_state.dates['start'],
            end_date=self.app_state.dates['end'],
            vendors=self.app_state.selected_vendors,
            reports=self.app_state.selected_reports,
            config=self.app_state.config
        )

        # Show progress dialog with scrim - it handles everything
        progress_dialog = ProgressDialog(config=config, parent=self)
        self.show_modal_with_scrim(progress_dialog)

        # When we get here, harvest is complete
        # Dialog has already shown success/failure messages

    def _show_vendors(self):
        """Show vendor management dialog with scrim."""
        dialog = VendorManagementDialog(
            initial_state={"vendors": self.app_state.vendors_data},
            parent=self
        )

        # Connect dialog signals
        #dialog.vendorsDataChanged.connect(self._on_vendors_data_changed)

        result = self.show_modal_with_scrim(dialog)

        if result == QDialog.DialogCode.Accepted:
            # Get final state and update
            state = dialog.get_state()
            self._on_vendors_data_changed(state['vendors'])

    def _open_settings(self):
        """Open settings dialog with scrim."""
        dialog = SushiConfigDialog(
            initial_state=self.app_state.config,
            parent=self
        )

        # Connect dialog signals
        dialog.configChanged.connect(self._on_config_changed)

        self.show_modal_with_scrim(dialog)



    def _show_help(self):
        """Show help information."""
        help_url = get_help_url('main')

        msg = QMessageBox(self)
        msg.setWindowTitle("Help")
        msg.setText(
            "COUNTER 5.1 Harvester\n\n"
            "1. Select date range\n"
            "2. Choose providers and report types\n"
            "3. Click start to begin harvesting\n"

        )

        #  standard Close button
        msg.setStandardButtons(QMessageBox.StandardButton.Close)

        # Add a custom "Get More Info" button
        more_info_button = msg.addButton("Learn More", QMessageBox.ButtonRole.ActionRole)

        # Execute the message box
        msg.exec()

        # Check if user clicked "Get More Info"
        if msg.clickedButton() == more_info_button:
            QDesktopServices.openUrl(QUrl(help_url))


    def _handle_exit(self):
        """Handle application exit."""
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SushiHarvesterGUI()
    window.show()
    sys.exit(app.exec())