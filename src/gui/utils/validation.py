import calendar
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox


class DateValidator:
    """
    Utility class for validating user input before starting harvester operations.
    Ensures all required selections are made and date ranges are logically valid.
    Provides user-friendly error messages for invalid inputs.
    """

    def validate_selections(self, reports, vendors, date_range):
        """
        Validates all user selections before allowing harvester to start.
        Checks for required selections and logical consistency of inputs.
        Shows appropriate error dialogs if validation fails.

        Args:
            reports (list): List of selected report types from GUI
            vendors (list): List of selected providers from GUI
            date_range (tuple): Tuple of (start_date, end_date) strings in YYYY-MM format

        Returns:
            bool: True if all validations pass, False if any validation fails
        """

        # Validate that at least one report type is selected
        if not reports:
            QMessageBox.critical(None, "Error", "Please select at least one report type.")
            return False

        # Validate that at least one provider is selected
        if not vendors:
            QMessageBox.critical(None, "Error", "Please select at least one provider.")
            return False

        # Extract start and end dates from the tuple
        start_date, end_date = date_range

        try:
            # Parse date strings into components
            # Expected format: "YYYY-MM" (e.g., "2025-01")
            start_year, start_month = start_date.split('-')
            end_year, end_month = end_date.split('-')

            # Convert string components to datetime objects for comparison
            # Use day=1 since we only care about month/year
            start_dt = datetime(int(start_year), int(start_month), 1)
            end_dt = datetime(int(end_year), int(end_month), 1)

            # Validate logical date order
            if start_dt > end_dt:
                QMessageBox.critical(None, "Error", "Start date must be before End date.")
                return False

        except Exception:
            # Catch any parsing errors (invalid format, non-numeric values, etc.)
            QMessageBox.critical(None, "Error", "Invalid date input.")
            return False

        # All validations passed
        return True