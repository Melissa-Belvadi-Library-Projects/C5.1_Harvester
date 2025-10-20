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
    calls getcounter.run_harvester().
    """

    # Signals for thread-safe communication
    log_signal = pyqtSignal(str)  # Log messages
    finished_signal = pyqtSignal(bool, dict)  # success, results

    def __init__(self, begin_date, end_date, vendors, reports, config_dict):
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
        self.config_dict = config_dict #storing dict
        self._is_cancelled = False
        self._has_started_processing = False # for if the user stops before any report ws retrieved

    def run(self):
        """Execute harvester in background thread."""
        try:
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
                config_dict=self.config_dict,
                progress_callback=self._handle_progress,
                is_cancelled_callback=lambda: self._is_cancelled #pass the cancel function through here
            )

            # Emit results
            if self._is_cancelled:
                #self.log_signal.emit("\nCOUNTER 5.1 Harvester Cancelled")
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
        if self._has_started_processing:
            self.log_signal.emit("Cancellation requested, finishing saving the last report started before the Stop request...")
        else:
            self.log_signal.emit("Cancellation requested")

    def _handle_progress(self, message):
        """Handle progress messages from harvester backend."""
        # Detects when we start processing reports
        if "Retrieving reports:" in message or "Retrieving report:" in message:
            self._has_started_processing = True
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
# Allows users to resize if they need to see more content, but starts at your preferred size.
        self.setWindowTitle("Harvester Progress")
        self.setMinimumSize(900, 600)  # Changed from setFixedSize to setMinimumSize
        self.resize(900, 600)  #  Added this line (sets initial size)
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
            reports=self.config.reports,
            config_dict = self.config.config
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
        """Stop the running harvester and wait for thread to finish."""
        if self.harvester_thread and self.harvester_thread.isRunning():
            self.harvester_thread.cancel()
            self.stop_button.setEnabled(False)
            self.stop_button.setText("Stopping...")

            # Wait for thread to finish (with timeout)
            if not self.harvester_thread.wait(5000):  # 5 second timeout
                self.log_text.append("Please wait a moment.")

            self.stop_button.setText("Stop")



    def _on_finished(self, success: bool, results: dict):
        """Handle harvester completion with simple, friendly messages."""
        self.results = results

        # Update UI state
        self.stop_button.setEnabled(False)
        self.close_button.setEnabled(True)
        self.save_log_button.setEnabled(True)

        # Case 1: Cancelled
        if results.get('cancelled') or (self.harvester_thread and self.harvester_thread._is_cancelled):

            QMessageBox.information(
                self,
                "Harvester Cancelled",
                "Harvester cancelled."
            )
            return

        # Case 2: Success
        QMessageBox.information(
            self,
            "Harvester Finished",
            "Harvester finished"
        )


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
            # Silently ignore - similar to the  close  button behavior
            event.ignore()
            QMessageBox.information(
                self,
                "Harvester Running",
                "Please wait for the harvest to complete, or click Stop first."
            )

        else:
            # Allow close when harvester is done
            if self.harvester_thread:
                self.harvester_thread.wait()
                self.harvester_thread.deleteLater()
            event.accept()

