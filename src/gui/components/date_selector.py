import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLabel, QComboBox, QSpinBox
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy


class DateSelector(QGroupBox):
    """
    Custom widget for selecting date ranges.
    Provides month/year dropdowns for start and end dates.
    Inherits from QGroupBox to get a titled border.
    """

    def __init__(self, config_data):
        """
        Constructor for DateSelector widget.

        Args:
            config_data (dict): Configuration dictionary with default settings
        """
        # Call parent constructor with title
        super().__init__("Select Date Range")

        # Store configuration for accessing defaults
        self.config_data = config_data

        # Build the user interface
        self.setup_ui()

    def setup_ui(self):
        """
        Creates and arranges the date selection controls.
        Uses a grid layout for organized positioning of labels and dropdowns.
        """
        # Grid layout for organized control placement
        date_layout = QGridLayout()

        # Get default dates from configuration
        begin_year, begin_month_idx, end_year, end_month_idx = self.get_default_dates()

        # List of month names for dropdown
        months = list(calendar.month_name)[1:]  # Skip empty first element

        # Set layout spacing
        date_layout.setHorizontalSpacing(6)
        date_layout.setVerticalSpacing(3)
        date_layout.setContentsMargins(5, 5, 5, 5)

        # Start date controls
        date_layout.addWidget(QLabel("Start:"), 0, 0)

        # Start month dropdown
        self.start_month = QComboBox()
        self.start_month.addItems(months)
        self.start_month.setCurrentIndex(begin_month_idx)
        self.start_month.setFixedWidth(95)
        date_layout.addWidget(self.start_month, 0, 1)

        # Start year spinner
        self.start_year = QSpinBox()
        #This line creates an instance of a QSpinBox.
        # A QSpinBox is a widget that lets the user select an integer value by clicking up/down arrows or by typing a number directly.
        self.start_year.setRange(2000, 2100)
        self.start_year.setValue(begin_year)
        self.start_year.setFixedWidth(65)
        date_layout.addWidget(self.start_year, 0, 2) # the first number, 0, is the row index. The second number, 3, is the column index.

        #add spaces as we are inheriting from gridlayout
        date_layout.setColumnMinimumWidth(3, 20)

        # End date controls
        date_layout.addWidget(QLabel("End:"), 0, 4)

        # End month dropdown
        self.end_month = QComboBox()
        self.end_month.addItems(months)
        self.end_month.setCurrentIndex(end_month_idx)
        self.end_month.setFixedWidth(90)
        date_layout.addWidget(self.end_month, 0, 5)

        # End year spinner
        self.end_year = QSpinBox()
        self.end_year.setRange(2000, 2100)
        self.end_year.setValue(end_year)
        self.end_year.setFixedWidth(65)
        date_layout.addWidget(self.end_year, 0, 6)

        # Add stretch to keep widgets left-aligned
        date_layout.setColumnStretch(7, 1)


        # Apply layout to widget
        self.setLayout(date_layout)

    def get_default_dates(self):
        """
        Calculates default start and end dates from configuration.

        Returns:
            tuple: (begin_year, begin_month_idx, end_year, end_month_idx)
        """
        # Calculate default end date (previous month from today)
        today = datetime.now()
        default_end_date = today - relativedelta(months=1)

        # Get default begin date from configuration
        default_begin = self.config_data.get('default_begin', '2025-01')

        try:
            if '-' in default_begin:
                # Parse year-month format
                begin_year, begin_month = default_begin.split('-')
                begin_year = int(begin_year)
                begin_month_idx = int(begin_month) - 1  # Convert to 0-based index
            else:
                # Fallback for unexpected format
                begin_year = 2025
                begin_month_idx = 0
        except (ValueError, IndexError):
            # Fallback for parsing errors
            begin_year = 2025
            begin_month_idx = 0

        return begin_year, begin_month_idx, default_end_date.year, default_end_date.month - 1

    def update_defaults(self, config_data):
        """
        Updates the date widgets when configuration changes.

        Args:
            config_data (dict): Updated configuration data
        """
        # Store new configuration
        self.config_data = config_data

        # Recalculate default dates
        begin_year, begin_month_idx, end_year, end_month_idx = self.get_default_dates()

        # Update start date widgets
        self.start_year.setValue(begin_year)
        self.start_month.setCurrentIndex(begin_month_idx)

        # Update end date widgets
        self.end_year.setValue(end_year)
        self.end_month.setCurrentIndex(end_month_idx)

    def get_start_date(self):
        """
        Returns the selected start date in YYYY-MM format.

        Returns:
            str: Formatted start date
        """
        return self.format_date(self.start_year.value(), self.start_month.currentText())

    def get_end_date(self):
        """
        Returns the selected end date in YYYY-MM format.

        Returns:
            str: Formatted end date
        """
        return self.format_date(self.end_year.value(), self.end_month.currentText())

    def get_date_range(self):
        """
        Returns both start and end dates as a tuple.

        Returns:
            tuple: (start_date, end_date) in YYYY-MM format
        """
        return (self.get_start_date(), self.get_end_date())

    def format_date(self, year, month_name):
        """
        Converts year and month name to YYYY-MM format.

        Args:
            year (int): Year value
            month_name (str): Month name (e.g., "January")

        Returns:
            str: Formatted date string
        """
        months = list(calendar.month_name)[1:]
        month_num = months.index(month_name) + 1
        return f"{year}-{month_num:02d}"