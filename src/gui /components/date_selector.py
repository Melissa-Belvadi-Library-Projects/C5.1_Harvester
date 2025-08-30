import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLabel, QComboBox, QSpinBox
from PyQt6.QtCore import Qt


class DateSelector(QGroupBox):
    def __init__(self, config_data):
        super().__init__("Select Date Range")
        self.config_data = config_data
        self.setup_ui()

    def setup_ui(self):
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

        self.setLayout(date_layout)

    def get_default_dates(self):
        """Get default dates from configuration instead of hardcoded values"""
        today = datetime.now()
        default_end_date = today - relativedelta(months=1)

        # Get default begin date from loaded configuration
        default_begin = self.config_data.get('default_begin', '2025-01')

        try:
            if '-' in default_begin:
                begin_year, begin_month = default_begin.split('-')
                begin_year = int(begin_year)
                begin_month_idx = int(begin_month) - 1  # Convert to 0-based index for combobox
            else:
                # Fallback if format is unexpected
                begin_year = 2025
                begin_month_idx = 0
        except (ValueError, IndexError):
            # Fallback if parsing fails
            begin_year = 2025
            begin_month_idx = 0

        return begin_year, begin_month_idx, default_end_date.year, default_end_date.month - 1

    def update_defaults(self, config_data):
        """Update the date widgets with new default values from config"""
        self.config_data = config_data
        begin_year, begin_month_idx, end_year, end_month_idx = self.get_default_dates()

        # Update start date widgets
        self.start_year.setValue(begin_year)
        self.start_month.setCurrentIndex(begin_month_idx)

        # Optionally update end date as well
        self.end_year.setValue(end_year)
        self.end_month.setCurrentIndex(end_month_idx)

    def get_start_date(self):
        """Get formatted start date"""
        return self.format_date(self.start_year.value(), self.start_month.currentText())

    def get_end_date(self):
        """Get formatted end date"""
        return self.format_date(self.end_year.value(), self.end_month.currentText())

    def get_date_range(self):
        """Get tuple of (start_date, end_date)"""
        return (self.get_start_date(), self.get_end_date())

    def format_date(self, year, month_name):
        months = list(calendar.month_name)[1:]
        month_num = months.index(month_name) + 1
        return f"{year}-{month_num:02d}"