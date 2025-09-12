"""Central state management for COUNTER 5.1 Harvester application."""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt6.QtCore import QObject, pyqtSignal
import json


@dataclass
class AppState:
    """Single source of truth for application state."""

    config: Dict[str, Any] = field(default_factory=dict)
    dates: Dict[str, str] = field(default_factory=dict)  # {"start": "YYYY-MM", "end": "YYYY-MM"}
    selected_vendors: List[str] = field(default_factory=list)
    selected_reports: List[str] = field(default_factory=list)
    vendors_data: List[Dict[str, str]] = field(default_factory=list)  # Full vendor records

    def __post_init__(self):
        """Initialize default dates if not provided."""
        if not self.dates:
            self.dates = self._get_default_dates()

    def _get_default_dates(self) -> Dict[str, str]:
        """Calculate default date range."""
        today = datetime.now()
        end_date = today - relativedelta(months=1)

        # Get start from config or use default
        default_begin = self.config.get('default_begin', '2025-01')

        return {
            "start": default_begin,
            "end": f"{end_date.year}-{end_date.month:02d}"
        }

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration and cascade changes."""
        self.config.update(new_config)

        # Update dates if default_begin changed
        if 'default_begin' in new_config:
            self.dates["start"] = new_config['default_begin']

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppState':
        """Deserialize state from dictionary."""
        return cls(**data)


class AppSignals(QObject):
    """Central event bus for application-wide signals."""

    # Core state change signals
    configChanged = pyqtSignal(dict)  # Full config dict
    dateRangeChanged = pyqtSignal(str, str)  # start, end
    vendorsChanged = pyqtSignal(list)  # List of vendor names
    vendorsDataChanged = pyqtSignal(list)  # Full vendor data
    reportsChanged = pyqtSignal(list)  # List of report names

    # Application events
    errorOccurred = pyqtSignal(str)  # Error message
    busyChanged = pyqtSignal(bool)  # True when busy
    statusChanged = pyqtSignal(str)  # Status message

    # Persistence events
    saveRequested = pyqtSignal()  # Request to save all state
    loadRequested = pyqtSignal()  # Request to reload state