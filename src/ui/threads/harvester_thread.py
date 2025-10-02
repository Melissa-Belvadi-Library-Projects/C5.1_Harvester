"""
Background thread that runs the actual COUNTER harvester backend.
Bridges the GUI with the existing CLI functionality.
"""

import sys
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from core.harvester_integration import HarvesterIntegration, HarvesterRequest, adapt_gui_config


class HarvesterThread(QThread):
    """
    Background thread for running the COUNTER harvester.
    Uses the existing backend through the integration layer.
    """

    # Signals for thread-safe communication
    log_signal = pyqtSignal(str)  # Log messages
    status_signal = pyqtSignal(str)  # Status updates
    progress_signal = pyqtSignal(int)  # Progress percentage
    finished_signal = pyqtSignal(bool, dict)  # success, results

    def __init__(self, config):
        """
        Initialize with harvester configuration.

        Args:
            config: HarvesterConfig from GUI
        """
        super().__init__()
        self.config = config
        self.harvester = None
        self._is_cancelled = False

    def run(self):
        """Execute harvester in background thread."""
        try:
            self.log_signal.emit("=" * 60)
            self.log_signal.emit("COUNTER 5.1 Harvester Started")
            self.log_signal.emit(f"Date Range: {self.begin_date} to {self.end_date}")
            self.log_signal.emit(f"Vendors: {', '.join(self.vendors) if self.vendors else 'All'}")
            self.log_signal.emit(f"Reports: {', '.join(self.reports)}")
            self.log_signal.emit("=" * 60)
            self.log_signal.emit("")

            # Call the backend directly
            results = getcounter.run_harvester(
                begin_date=self.begin_date,
                end_date=self.end_date,
                selected_vendors=self.vendors,
                selected_reports=self.reports,
                progress_callback=self._handle_progress,
                is_cancelled_callback=lambda: self._is_cancelled
            )

            # Emit results - success means no errors
            if self._is_cancelled:
                self.log_signal.emit("\n⚠ Harvest cancelled by user")
                self.finished_signal.emit(False, {'cancelled': True})
            else:
                has_errors = bool(results.get('errors'))
                self.finished_signal.emit(not has_errors, results)  # Success if no errors

        except Exception as e:
            self.log_signal.emit(f"\n Error: {str(e)}")
            import traceback
            self.log_signal.emit(traceback.format_exc())
            self.finished_signal.emit(False, {'error': str(e)})
    def cancel(self):
        """Cancel the running harvest."""
        self._is_cancelled = True
        if self.harvester:
            self.harvester.cancel()

    def _handle_progress(self, message: str):
        """Handle progress messages from harvester."""
        self.log_signal.emit(message)

        # Try to extract percentage for progress bar
        if "%" in message and "[" in message:
            try:
                # Extract percentage from messages like "[50%] Fetching..."
                pct_str = message.split("[")[1].split("%")[0]
                percentage = int(float(pct_str))
                self.progress_signal.emit(percentage)
            except:
                pass

    def _handle_status(self, message: str):
        """Handle status updates from harvester."""
        self.status_signal.emit(message)