import calendar
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox


class DateValidator:
    def validate_selections(self, reports, vendors, date_range):
        """Validate user selections before starting harvester"""
        if not reports:
            QMessageBox.critical(None, "Error", "Please select at least one report type.")
            return False

        if not vendors:
            QMessageBox.critical(None, "Error", "Please select at least one provider.")
            return False

        start_date, end_date = date_range

        try:
            # Parse dates
            start_year, start_month = start_date.split('-')
            end_year, end_month = end_date.split('-')

            start_dt = datetime(int(start_year), int(start_month), 1)
            end_dt = datetime(int(end_year), int(end_month), 1)

            if start_dt > end_dt:
                QMessageBox.critical(None, "Error", "Start date must be before End date.")
                return False

        except Exception:
            QMessageBox.critical(None, "Error", "Invalid date input.")
            return False

        return True