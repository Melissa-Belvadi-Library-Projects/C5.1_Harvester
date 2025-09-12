# ui/components/date_selector.py
"""Date selector component with state management."""

import calendar
from typing import Dict, Any, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLabel, QComboBox, QSpinBox
from PyQt6.QtCore import Qt, pyqtSignal, QTimer


class DateSelector(QGroupBox):
    """
    Date range selector with state management support.
    Emits signals on user changes, responds to external state updates.
    """

    # High-level signal for date range changes
    dateRangeChanged = pyqtSignal(str, str)  # start, end in YYYY-MM format

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        """Initialize with optional initial state."""
        super().__init__("Select Date Range")

        # State management
        self._updating = False
        self._state = initial_state or {}

        # Debounce timer for rapid changes
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_change)
        self._pending_emit = None

        # Create UI
        self._setup_ui()

        # Apply initial state if provided
        if initial_state:
            self.set_state(initial_state)

    def _setup_ui(self):
        """Create and arrange the date selection controls."""
        layout = QGridLayout()
        layout.setHorizontalSpacing(6)
        layout.setVerticalSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)

        # Month names for dropdowns
        self.months = list(calendar.month_name)[1:]

        # Start date controls
        layout.addWidget(QLabel("Start:"), 0, 0)

        self.start_month = QComboBox()
        self.start_month.addItems(self.months)
        self.start_month.setFixedWidth(95)
        self.start_month.currentIndexChanged.connect(self._on_date_changed)
        layout.addWidget(self.start_month, 0, 1)

        self.start_year = QSpinBox()
        self.start_year.setRange(2000, 2100)
        self.start_year.setFixedWidth(75)
        self.start_year.valueChanged.connect(self._on_date_changed)
        layout.addWidget(self.start_year, 0, 2)

        layout.setColumnMinimumWidth(3, 20)

        # End date controls
        layout.addWidget(QLabel("End:"), 0, 4)

        self.end_month = QComboBox()
        self.end_month.addItems(self.months)
        self.end_month.setFixedWidth(95)
        self.end_month.currentIndexChanged.connect(self._on_date_changed)
        layout.addWidget(self.end_month, 0, 5)

        self.end_year = QSpinBox()
        self.end_year.setRange(2000, 2100)
        self.end_year.setFixedWidth(75)
        self.end_year.valueChanged.connect(self._on_date_changed)
        layout.addWidget(self.end_year, 0, 6)

        layout.setColumnStretch(7, 1)
        self.setLayout(layout)

        # Set defaults
        self._set_default_dates()

    def _set_default_dates(self):
        """Set default date values."""
        today = datetime.now()
        end_date = today - relativedelta(months=1)

        # Get default begin from state or use default value
        default_begin = self._state.get('default_begin', '2025-01')

        try:
            if '-' in default_begin:
                begin_year, begin_month = default_begin.split('-')
                begin_year = int(begin_year)
                begin_month = int(begin_month)
            else:
                begin_year, begin_month = 2025, 1
        except (ValueError, IndexError):
            begin_year, begin_month = 2025, 1

        # Set values without triggering signals
        self._updating = True
        self.start_year.setValue(begin_year)
        self.start_month.setCurrentIndex(begin_month - 1)
        self.end_year.setValue(end_date.year)
        self.end_month.setCurrentIndex(end_date.month - 1)
        self._updating = False

    def get_state(self) -> Dict[str, str]:
        """
        Get current state as a serializable dictionary.

        Returns:
            Dict containing start and end dates in YYYY-MM format
        """
        return {
            "start": self._format_date(self.start_year.value(),
                                       self.start_month.currentIndex() + 1),
            "end": self._format_date(self.end_year.value(),
                                     self.end_month.currentIndex() + 1)
        }

    def set_state(self, state: Dict[str, Any]):
        """
        Update widget state from external source.
        Blocks signals during update to prevent recursive emits.

        Args:
            state: Dictionary with optional 'default_begin', 'start', 'end' keys
        """
        self._updating = True
        self._state.update(state)

        try:
            # Handle default_begin for config compatibility
            if 'default_begin' in state:
                start = state['default_begin']
            elif 'start' in state:
                start = state['start']
            else:
                start = None

            if start and '-' in start:
                year, month = start.split('-')
                self.start_year.setValue(int(year))
                self.start_month.setCurrentIndex(int(month) - 1)

            # Handle end date
            if 'end' in state and state['end'] and '-' in state['end']:
                year, month = state['end'].split('-')
                self.end_year.setValue(int(year))
                self.end_month.setCurrentIndex(int(month) - 1)
            elif 'default_end' not in state:
                # Calculate default end if not provided
                today = datetime.now()
                end_date = today - relativedelta(months=1)
                self.end_year.setValue(end_date.year)
                self.end_month.setCurrentIndex(end_date.month - 1)

        finally:
            self._updating = False

    def _on_date_changed(self):
        """Handle date control changes with debouncing."""
        if self._updating:
            return

        # Store pending emit data
        state = self.get_state()
        self._pending_emit = (state["start"], state["end"])

        # Reset debounce timer (100ms delay)
        self._debounce_timer.stop()
        self._debounce_timer.start(100)

    def _emit_change(self):
        """Emit the dateRangeChanged signal after debounce."""
        if self._pending_emit:
            start, end = self._pending_emit
            self.dateRangeChanged.emit(start, end)
            self._pending_emit = None

    def _format_date(self, year: int, month: int) -> str:
        """Format year and month as YYYY-MM string."""
        return f"{year}-{month:02d}"

    def validate_dates(self) -> tuple[bool, str]:
        """
        Validate that start date is before end date.

        Returns:
            Tuple of (is_valid, error_message)
        """
        state = self.get_state()
        start = datetime.strptime(state["start"] + "-01", "%Y-%m-%d")
        end = datetime.strptime(state["end"] + "-01", "%Y-%m-%d")

        if start > end:
            return False, "Start date must be before end date"

        return True, ""