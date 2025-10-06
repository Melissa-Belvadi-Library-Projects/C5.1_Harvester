"""Progress dialog for long-running harvester operations."""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QFileDialog, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the backend directly
import getcounter


class HarvesterThread(QThread):
    """
    Background thread that calls the harvester backend directly.
    No integration layer - just calls getcounter.run_harvester().
    """

    # Signals for thread-safe communication
    log_signal = pyqtSignal(str)  # Log messages
    finished_signal = pyqtSignal(bool, dict)  # success, results

    def __init__(self, begin_date, end_date, vendors, reports):
        """
        Initialize with harvester parameters.

        Args:
            begin_date: Start date (YYYY-MM)
            end_date: End date (YYYY-MM)
            vendors: List of vendor names
            reports: List of report types
        """
        super().__init__()
        self.begin_date = begin_date
        self.end_date = end_date
        self.vendors = vendors
        self.reports = reports
        self._is_cancelled = False

    def run(self):
        """Execute harvester in background thread."""
        try:
           # self.log_signal.emit("-" * 60)
            self.log_signal.emit("COUNTER 5.1 Harvester Started")
            self.log_signal.emit(f"Date Range: {self.begin_date} to {self.end_date}")
            self.log_signal.emit(f"Providers: {', '.join(self.vendors) if self.vendors else 'All'}")
            self.log_signal.emit(f"Reports: {', '.join(self.reports)}")
            self.log_signal.emit("-" * 90)
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

            # Emit results
            if self._is_cancelled:
                self.log_signal.emit("\n Harvest cancelled-still testing")
                self.finished_signal.emit(False, {'cancelled': True})
            else:
                self.finished_signal.emit(results.get('success', False), results)

        except Exception as e:
            self.log_signal.emit(f"\n Error: {str(e)}")
            import traceback
            self.log_signal.emit(traceback.format_exc())
            self.finished_signal.emit(False, {'error': str(e)})

    def cancel(self):
        """Cancel the running harvest."""
        self._is_cancelled = True
        self.log_signal.emit("\n Cancellation requested...")

    def _handle_progress(self, message):
        """Handle progress messages from harvester backend."""
        self.log_signal.emit(message)


class ProgressDialog(QDialog):
    """
    Modal dialog showing harvester progress with live log output.
    Uses threading to prevent UI freezing during harvesting.
    """

    def __init__(self, config, parent=None):
        """
        Initialize with harvester configuration.

        Args:
            config: HarvesterConfig object with start_date, end_date, vendors, reports
            parent: Parent widget
        """
        super().__init__(parent)

        self.setWindowTitle("Harvester Progress")
        self.setFixedSize(900, 600)
        self.setModal(True)

        # Store configuration
        self.config = config
        self.harvester_thread: Optional[HarvesterThread] = None
        self.results = None

        # Build UI
        self._setup_ui()

        # Start harvester automatically
        self._start_harvester()

    def _setup_ui(self):
        """Create UI layout."""
        layout = QVBoxLayout(self)

        # Title label
        #title_label = QLabel("COUNTER 5.1 Harvester")
        #title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        #title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #layout.addWidget(title_label)

        # Log text area
        log_label = QLabel("Progress Log:")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
            }
        """)
        layout.addWidget(self.log_text)

        # Button layout
        button_layout = QHBoxLayout()

        # Save Log button
        self.save_log_button = QPushButton("Save Progress Log")
        self.save_log_button.setEnabled(False)
        self.save_log_button.clicked.connect(self._save_log)
        button_layout.addWidget(self.save_log_button)

        button_layout.addStretch()

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedWidth(100)
        self.stop_button.clicked.connect(self._stop_harvester)
        button_layout.addWidget(self.stop_button)
        button_layout.addSpacing(5)


        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setFixedWidth(100)
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _start_harvester(self):
        """Start the harvester in a background thread."""

        # Create and configure thread
        self.harvester_thread = HarvesterThread(
            begin_date=self.config.start_date,
            end_date=self.config.end_date,
            vendors=self.config.vendors,
            reports=self.config.reports
        )

        # Connect signals
        self.harvester_thread.log_signal.connect(self._log_message)
        self.harvester_thread.finished_signal.connect(self._on_finished)

        # Start thread
        self.harvester_thread.start()

    def _log_message(self, message: str):
        """Add message to log display."""
        self.log_text.append(message)

        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _stop_harvester(self):
        """Stop the running harvester."""
        if self.harvester_thread and self.harvester_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Stop",
                "Are you sure you want to stop the harvester?\n\n"
                "Any reports in progress will be incomplete.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.harvester_thread.cancel()
                self.stop_button.setEnabled(False)

    def _on_finished(self, success: bool, results: dict):
        """Handle harvester completion."""
        self.results = results

        # Update UI state
        self.stop_button.setEnabled(False)
        self.close_button.setEnabled(True)
        self.save_log_button.setEnabled(True)

        # if results.get('cancelled'):
        #
        #     # User cancelled
        #     self._log_message("\n" + "=" * 60)
        #     self._log_message("HARVESTER CANCELLED")
        #     self._log_message("=" * 60)
        #
        #     QMessageBox.information(
        #         self,
        #         "Cancelled",
        #         "Harvester was cancelled by user."
        #     )
        #
        # elif results.get('errors'):
        #     # Had errors
        #     self._log_message("\n" + "=" * 60)
        #     self._log_message("HARVESTER COMPLETED WITH ERRORS")
        #     self._log_message("=" * 60)
        #     self._log_message(f"Errors encountered: {len(results['errors'])}")
        #     for err in results['errors'][:10]:
        #         self._log_message(f"  - {err}")
        #     self._log_message("=" * 60)
        #
        #     QMessageBox.warning(
        #         self,
        #         "Completed with Errors",
        #         f"Harvester completed but encountered {len(results['errors'])} error(s).\n\n"
        #         f"Check the log for details."
        #     )
        #
        # else:
        #
        #     # Success - no errors
        #     QMessageBox.information(
        #         self,
        #         "Success",
        #         "Harvester completed\n\n"
        #         f"Check infolog for details."
        #     )

    def _save_log(self):
        """Save log to file."""
        try:
            default_filename = f"Progress_log.txt"

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Log File",
                default_filename
            )

            if filename:
                log_content = self.log_text.toPlainText()

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"COUNTER 5.1 Harvester Log\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Date Range: {self.config.start_date} to {self.config.end_date}\n")
                    f.write(f"Providers: {', '.join(self.config.vendors) if self.config.vendors else 'All'}\n")
                    f.write(f"Reports: {', '.join(self.config.reports)}\n")
                    #f.write("=" * 60 + "\n\n")
                    f.write(log_content)

                QMessageBox.information(self, "Success", " Progess Log saved")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save log:\n{e}")

    def closeEvent(self, event):

        """Handle window close event (X button)."""
        if self.harvester_thread and self.harvester_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Harvester Running",
                "The harvester is still running.\n\n"
                "Stop it and close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.harvester_thread.cancel()
                self.harvester_thread.wait(5000)  # Wait up to 5 seconds
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()