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
            # Create harvester with callbacks
            self.harvester = HarvesterIntegration(
                progress_callback=self._handle_progress,
                status_callback=self._handle_status
            )

            # Convert GUI config to harvester request
            request = adapt_gui_config(self.config)

            # Log configuration
            self.log_signal.emit("=" * 60)
            self.log_signal.emit("COUNTER 5.1 Harvester Started")
            self.log_signal.emit(f"Date Range: {request.begin_date} to {request.end_date}")
            self.log_signal.emit(f"Vendors: {', '.join(request.selected_vendors)}")
            self.log_signal.emit(
                f"Reports: {', '.join(request.selected_reports) if request.selected_reports else 'All supported'}")
            if request.single_report_type:
                self.log_signal.emit(f"Single Report Type: {request.single_report_type}")
            self.log_signal.emit("=" * 60)

            # Run the harvester
            results = self.harvester.run(request)

            # Emit results
            if self._is_cancelled:
                self.log_signal.emit("\n⚠Harvest cancelled by user")
                self.finished_signal.emit(False, {'cancelled': True})
            else:
                # Log summary
                self.log_signal.emit("\n" + "=" * 60)
                self.log_signal.emit("HARVEST COMPLETE - SUMMARY")
                self.log_signal.emit("=" * 60)
                self.log_signal.emit(f" Reports fetched: {results.get('reports_fetched', 0)}")
                self.log_signal.emit(f" Reports failed: {results.get('reports_failed', 0)}")

                if results.get('json_files'):
                    self.log_signal.emit(f"\nJSON files created: {len(results['json_files'])}")
                    for f in results['json_files'][:5]:  # Show first 5
                        self.log_signal.emit(f"   - {Path(f).name}")
                    if len(results['json_files']) > 5:
                        self.log_signal.emit(f"   ... and {len(results['json_files']) - 5} more")

                if results.get('tsv_files'):
                    self.log_signal.emit(f"\n TSV files created: {len(results['tsv_files'])}")
                    for f in results['tsv_files'][:5]:  # Show first 5
                        self.log_signal.emit(f"   - {Path(f).name}")
                    if len(results['tsv_files']) > 5:
                        self.log_signal.emit(f"   ... and {len(results['tsv_files']) - 5} more")

                if results.get('errors'):
                    self.log_signal.emit(f"\n⚠Errors encountered:")
                    for err in results['errors']:
                        self.log_signal.emit(f"   - {err}")

                self.log_signal.emit("=" * 60)

                self.finished_signal.emit(results.get('success', False), results)

        except Exception as e:
            self.log_signal.emit(f" Error: {str(e)}")
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