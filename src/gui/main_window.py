import sys
import csv
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QGroupBox, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction

# Import our custom components and dialogs
from .components.vendor_frame import VendorFrame
from .components.date_selector import DateSelector
from .dialogs.settings_dialog import SushiConfigDialog
from .dialogs.vendor_dialog import VendorManagementDialog
from .dialogs.progress_dialog import ProgressDialog
from .utils.config_manager import ConfigManager
from .utils.validation import DateValidator


class SushiHarvesterGUI(QMainWindow):

    """
    Main application window class.
    Inherits from QMainWindow to get menu bar, status bar, and toolbar support.
    """


    def __init__(self):
        """
        Constructor - called when creating a new instance of the class.
        Sets up the window and loads configuration.
        """
        # Call parent class constructor to initialize QMainWindow
        super().__init__()

        # Set window title and initial size/position
        self.setWindowTitle("COUNTER 5.1 Harvester")
        self.setGeometry(100, 100, 1000, 800)  # x, y, width, height

        # Load configuration before creating UI elements
        self.config_manager = ConfigManager()  # Create config manager instance
        self.config_data = self.config_manager.load_config()  # Load settings from file

        # Build the user interface
        self.setup_ui()

    def setup_ui(self):
        """
        Creates and arranges all UI elements in the main window.
        Called once during initialization.
        """
        # Set up the central widget (main content area)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # === Date Range + Help Button Row ===
        date_layout = QHBoxLayout()

        # Date selector
        self.date_selector = DateSelector(self.config_data)
        date_layout.addWidget(self.date_selector)

        # Stretch pushes Help button to far right
        date_layout.addStretch()

        # Help button (moved here)
        self.help_button = QPushButton("Help")
       # self.help_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.help_button.clicked.connect(self.show_help)
        date_layout.addWidget(self.help_button)

        # Add combined row to main layout
        main_layout.addLayout(date_layout)

        # === Report Types + Providers Section ===
        selection_layout = QHBoxLayout()

        # List of available COUNTER report types
        report_types = [
            "DR", "DR_D1", "DR_D2", "IR", "IR_A1", "IR_M1",
            "PR", "PR_P1", "TR", "TR_B1", "TR_B2", "TR_B3",
            "TR_J1", "TR_J2", "TR_J3", "TR_J4"
        ]

        # Providers frame
        vendors = self.load_vendors()
        self.vendor_frame = VendorFrame("Select Providers", vendors)
        selection_layout.addWidget(self.vendor_frame, stretch=2)  # 2/3 width


        # Report types frame
        self.report_frame = VendorFrame("Select Report Types", report_types)
        selection_layout.addWidget(self.report_frame, stretch=1)  # 1/3 width



        # Add to main layout
        main_layout.addLayout(selection_layout)

        # === First Button Row (Start, Manage Providers, Settings) ===
        first_button_layout = QHBoxLayout()

        # Start button
        self.start_button = QPushButton("Start")
       # self.start_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.start_button.clicked.connect(self.on_start)
        first_button_layout.addWidget(self.start_button)

        first_button_layout.addStretch(3)

        self.vendors_button = QPushButton("Manage Providers")
       # self.vendors_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.vendors_button.clicked.connect(self.show_vendors)
        first_button_layout.addWidget(self.vendors_button)

        first_button_layout.addSpacing(5)

        self.settings_button = QPushButton("Settings")
        #self.settings_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.settings_button.clicked.connect(self.open_settings)
        first_button_layout.addWidget(self.settings_button)

        # Add button row
        main_layout.addLayout(first_button_layout)

        main_layout.addSpacing(15)

        # === Exit Button Row ===
        second_button_layout = QHBoxLayout()
        second_button_layout.addStretch()

        self.exit_button = QPushButton("Exit")
       # self.exit_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.exit_button.clicked.connect(self.close)
        second_button_layout.addWidget(self.exit_button)

        main_layout.addLayout(second_button_layout)

    def load_vendors(self):

        """
        Loads vendor/provider list from TSV configuration files.
        Returns list of vendor names for the selection widget.
        """

        vendors = []  # Initialize empty list

        #Gets providers file name from configuration
        providers_file = self.config_data.get('providers_file', 'providers.tsv')

        # Define search locations for provider files
        search_paths = [Path.cwd(), Path.cwd().parent / "registry_harvest"]
        config_files = [providers_file, 'registry-entries-2025-05-03.tsv']

        # Search for and load provider files
        for path in search_paths:  # Try each search location
            for config_file in config_files:  # Try each potential filename
                full_path = path / config_file
                if full_path.exists():  # If file found
                    try:
                        # Open and read TSV file
                        with open(full_path, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f, delimiter='\t')  # Tab-delimited
                            next(reader)  # Skip header row
                            for line in reader:  # Process each data row
                                # Extract vendor name (first column) if valid
                                if len(line) > 0 and line[0] and line[0] != 'required':
                                    vendors.append(line[0])
                        if vendors:  # If we found vendors, return them
                            return vendors
                    except Exception:  # If file reading fails, continue searching
                        continue

        # Fallback if no vendor file found
        return ["Sample Provider 1", "Sample Provider 2", "EBSCO", "ProQuest", "Springer"]

    def on_start(self):
        """
        Handler for START button click.
        Validates inputs and launches the harvester.
        """
        #Validate user selections before proceeding
        validator = DateValidator()

        if not validator.validate_selections(
                self.report_frame.get_selected(),  # Selected report types
                self.vendor_frame.get_selected(),  # Selected vendors
                self.date_selector.get_date_range()  # Date range tuple
        ):
            return  # Exit if validation fails

        #Build configuration for harvester
        user_selections = {
            'start_date': self.date_selector.get_start_date(),
            'end_date': self.date_selector.get_end_date(),
            'reports': self.report_frame.get_selected(),
            'vendors': self.vendor_frame.get_selected()
        }

        #Create and show progress dialog
        progress_dialog = ProgressDialog(self)
        progress_dialog.start_harvester(user_selections)
        progress_dialog.exec()  # Show as modal dialog

    def open_settings(self):
        """
        Opens the settings configuration dialog.
        Handles configuration changes and UI updates.
        """
        #Create and show settings dialog
        dialog = SushiConfigDialog(self)
        result = dialog.exec()

        # Handle settings changes if user clicked Save
        if result == QDialog.DialogCode.Accepted:
            old_config = self.config_data.copy()  # Backup old config
            self.config_data = self.config_manager.load_config()  # Reload config

            # Check if default date changed and update date selector
            if old_config.get('default_begin') != self.config_data.get('default_begin'):
                self.date_selector.update_defaults(self.config_data)

            # Check if providers file changed and reload vendor list
            if old_config.get('providers_file') != self.config_data.get('providers_file'):
                self.reload_vendors()

    def reload_vendors(self):
        """
        Reloads the vendor list when provider configuration changes.
        Updates the vendor selection widget with new data.
        """
        # Load new vendor list and update widget
        vendors = self.load_vendors()
        self.vendor_frame.update_items(vendors)

    def show_vendors(self):
        """Opens the vendor management dialog for editing provider configurations."""
        dialog = VendorManagementDialog(self, self.config_data)
        # The exec() method returns a QDialog.DialogCode
        result = dialog.exec()

        # Check if the dialog was closed by the user accepting the changes.
        # The VendorManagementDialog calls self.accept() upon successful save and close.
        if result == QDialog.DialogCode.Accepted:
            # If the dialog was accepted, reload the list of vendors in the main GUI.
            self.reload_vendors()

    def show_help(self):
        """
        Shows help information (placeholder implementation).
        """
        # Simple message box for help
        QMessageBox.information(self, "Help", "Help documentation coming soon...")

    def show_about(self):
        """
        Shows application about dialog.
        """
        # About dialog with application information
        QMessageBox.about(self, "About",
                          " Counter 5.1 Harvester GUI\n\n"
                          "A tool for collecting COUNTER usage statistics\n"
                          "from database providers via COUNTER API.")