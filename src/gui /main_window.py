import sys
import csv
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QGroupBox, QMenuBar,
    QStatusBar, QMessageBox, QDialog
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
        self.setWindowTitle("HARVESTER GUI")
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
        central_widget = QWidget()  # Container for all content
        self.setCentralWidget(central_widget)  # Tell QMainWindow this is the main content
        main_layout = QVBoxLayout(central_widget)  # Vertical layout manager

        # Create menu bar (File, Help menus)
        self.create_menu_bar()

        # Date Range Selection Section
        # Create a date selector widget using our custom component
        self.date_selector = DateSelector(self.config_data)
        main_layout.addWidget(self.date_selector)  # Add to main layout

        # Line 51-61: Selection Section (Report Types and Providers)
        selection_layout = QHBoxLayout()  # Horizontal layout for side-by-side widgets

        # List of available COUNTER report types
        report_types = [
            "DR", "DR_D1", "DR_D2", "IR", "IR_A1", "IR_M1",
            "PR", "PR_P1", "TR", "TR_B1", "TR_B2", "TR_B3",
            "TR_J1", "TR_J2", "TR_J3", "TR_J4"
        ]

        # Create vendor frame for report type selection
        self.report_frame = VendorFrame("Select Report Types", report_types)
        selection_layout.addWidget(self.report_frame)

        # Load vendor list and create vendor selection frame
        vendors = self.load_vendors()
        self.vendor_frame = VendorFrame("Select Providers", vendors)
        selection_layout.addWidget(self.vendor_frame)

        # Add the selection section to main layout
        main_layout.addLayout(selection_layout)

        # Button Section
        button_layout = QHBoxLayout()

        # START button on the left
        self.start_button = QPushButton("START")
        self.start_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.start_button.clicked.connect(self.on_start)  # Connect to handler function
        button_layout.addWidget(self.start_button)

        # Add stretch to push other buttons to the right
        button_layout.addStretch()

        # Right-aligned buttons
        self.vendors_button = QPushButton("MANAGE PROVIDERS")
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

        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")  # Initial status message
        self.setStatusBar(self.status_bar)  # Attach to main window

    def create_menu_bar(self):
        """
        Creates the application menu bar with File and Help menus.
        """
        # Get the menu bar from QMainWindow
        menubar = self.menuBar()

        #File Menu
        file_menu = menubar.addMenu('File')
        settings_action = QAction('Settings', self)  # Create menu item
        settings_action.triggered.connect(self.open_settings)  # Connect to handler
        file_menu.addAction(settings_action)
        file_menu.addSeparator()  # Visual separator line
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)  # Close application
        file_menu.addAction(exit_action)

        # Line 109-113: Help Menu
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def load_vendors(self):
        """
        Loads vendor/provider list from TSV configuration files.
        Returns list of vendor names for the selection widget.
        """
        vendors = []  # Initialize empty list

        # Line 121: Get providers file name from configuration
        providers_file = self.config_data.get('providers_file', 'providers.tsv')

        # Line 123-124: Define search locations for provider files
        search_paths = [Path.cwd(), Path.cwd().parent / "registry_harvest"]
        config_files = [providers_file, 'registry-entries-2025-05-03.tsv']

        # Line 126-140: Search for and load provider files
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

        # Line 141: Fallback if no vendor file found
        return ["Sample Provider 1", "Sample Provider 2", "EBSCO", "ProQuest", "Springer"]

    def on_start(self):
        """
        Handler for START button click.
        Validates inputs and launches the harvester.
        """
        # Line 148-154: Validate user selections before proceeding
        validator = DateValidator()

        if not validator.validate_selections(
                self.report_frame.get_selected(),  # Selected report types
                self.vendor_frame.get_selected(),  # Selected vendors
                self.date_selector.get_date_range()  # Date range tuple
        ):
            return  # Exit if validation fails

        # Line 156-162: Build configuration for harvester
        user_selections = {
            'start_date': self.date_selector.get_start_date(),
            'end_date': self.date_selector.get_end_date(),
            'reports': self.report_frame.get_selected(),
            'vendors': self.vendor_frame.get_selected()
        }

        # Line 164-166: Create and show progress dialog
        progress_dialog = ProgressDialog(self)
        progress_dialog.start_harvester(user_selections)
        progress_dialog.exec()  # Show as modal dialog

    def open_settings(self):
        """
        Opens the settings configuration dialog.
        Handles configuration changes and UI updates.
        """
        # Line 173-174: Create and show settings dialog
        dialog = SushiConfigDialog(self)
        result = dialog.exec()

        # Line 176-184: Handle settings changes if user clicked Save
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
        # Line 192-193: Load new vendor list and update widget
        vendors = self.load_vendors()
        self.vendor_frame.update_items(vendors)

        # Line 195-196: Show status message to user
        providers_file = self.config_data.get('providers_file', 'providers.tsv')
        self.status_bar.showMessage(f"Reloaded {len(vendors)} providers from {providers_file}", 3000)

    def show_vendors(self):
        """
        Opens the vendor management dialog for editing provider configurations.
        """
        # Line 202-203: Create and show vendor management dialog
        dialog = VendorManagementDialog(self, self.config_data)
        result = dialog.exec()

        # Line 205-211: Handle vendor changes if user saved modifications
        if result == QDialog.DialogCode.Accepted:
            self.reload_vendors()  # Refresh vendor list
            QMessageBox.information(
                self, "Providers Updated",
                "Provider list has been updated. The changes will be used in future harvester runs."
            )

    def show_help(self):
        """
        Shows help information (placeholder implementation).
        """
        # Line 217: Simple message box for help
        QMessageBox.information(self, "Help", "Help documentation coming soon...")

    def show_about(self):
        """
        Shows application about dialog.
        """
        # Line 222-226: About dialog with application information
        QMessageBox.about(self, "About",
                          "SUSHI Harvester GUI\n\n"
                          "A tool for collecting COUNTER usage statistics\n"
                          "from database providers via SUSHI API.")