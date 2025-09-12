from dataclasses import dataclass
from typing import List, Optional, Callable
from datetime import datetime
import time


@dataclass
class HarvesterConfig:
    """Configuration for a harvester run."""

    start_date: str  # YYYY-MM format
    end_date: str  # YYYY-MM format
    vendors: List[str]
    reports: List[str]
    config: dict  # General app config (db path, etc.)


class HarvesterEngine:
    """Core harvesting logic independent of UI."""

    def __init__(self, progress_callback: Optional[Callable[[str], None]] = None):
        """Initialize with optional progress callback."""
        self.progress_callback = progress_callback or (lambda msg: print(msg))
        self.is_cancelled = False

    def run(self, config: HarvesterConfig) -> bool:
        """
        Execute the harvesting process.

        Returns:
            bool: True if successful, False otherwise
        """
        self.is_cancelled = False

        try:
            self._log(f"Starting harvest from {config.start_date} to {config.end_date}")
            self._log(f"Vendors: {', '.join(config.vendors)}")
            self._log(f"Reports: {', '.join(config.reports)}")

            # Simulate harvesting process
            total_items = len(config.vendors) * len(config.reports)
            completed = 0

            for vendor in config.vendors:
                if self.is_cancelled:
                    self._log("Harvest cancelled by user")
                    return False

                for report in config.reports:
                    if self.is_cancelled:
                        self._log("Harvest cancelled by user")
                        return False

                    self._log(f"Fetching {report} from {vendor}...")

                    # Simulate API call
                    time.sleep(0.5)

                    completed += 1
                    progress = (completed / total_items) * 100
                    self._log(f"Progress: {progress:.1f}%")

            self._log("Harvest completed successfully!")
            return True

        except Exception as e:
            self._log(f"Error during harvest: {e}")
            return False

    def cancel(self):
        """Cancel the running harvest."""
        self.is_cancelled = True

    def _log(self, message: str):
        """Log a message via the callback."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.progress_callback(f"[{timestamp}] {message}")