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

# Import from core
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.engine import HarvesterEngine, HarvesterConfig
from core.state import AppState


class HarvesterThread(QThread):
    """
    Background thread for running the harvester.
    Ensures UI remains responsive during long operations.
    """

    # Signals for thread-safe communication
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)  # Progress percentage
    finished_signal = pyqtSignal(bool, int)  # success, return_code

    def __init__(self, config: HarvesterConfig):
        """Initialize with harvester configuration."""
        super().__init__()
        self.config = config
        self.engine = HarvesterEngine(progress_callback=self._handle_progress)
        self._is_cancelled = False

    def run(self):
        """Execute harvester in background thread."""
        try:
            success = self.engine.run(self.config)
            if self._is_cancelled:
                self.finished_signal.emit(False, -1)
            else:
                self.finished_signal.emit(success, 0 if success else 1)
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False, -2)

    def cancel(self):
        """Cancel the running harvest."""
        self._is_cancelled = True
        self.engine.cancel()

    def _handle_progress(self, message: str):
        """Handle progress messages from engine."""
        self.log_signal.emit(message)

        # Extract percentage if present
        if "Progress:" in message and "%" in message:
            try:
                pct_str = message.split("Progress:")[1].split("%")[0].strip()
                percentage = int(float(pct_str))
                self.progress_signal.emit(percentage)
            except:
                pass


class ProgressDialog(QDialog):
    """
    Modal dialog showing harvester progress.
    Uses threading to prevent UI freezing.
    """

    def __init__(self, config: HarvesterConfig, app_state: AppState, parent=None):
        """Initialize with harvester config and app state."""
        super().__init__(parent)

        self.setWindowTitle("Harvester Progress")
        self.setFixedSize(800, 600)
        self.setModal(True)

        # Store references
        self.config = config
        self.app_state = app_state
        self.harvester_thread: Optional[HarvesterThread] = None

        # Build UI
        self._setup_ui()

        # Start harvester automatically
        self._start_harvester()

    def _setup_ui(self):
        """Create UI layout."""
        layout = QVBoxLayout(self)

        # Status label
        self.status_label = QLabel("Preparing to start harvester...")
        self.status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Courier", 9))
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Button layout
        button_layout = QHBoxLayout()

        # Save Log button
        self.save_log_button = QPushButton("Save Progress Output")
        self.save_log_button.setEnabled(False)
        self.save_log_button.clicked.connect(self._save_log)
        button_layout.addWidget(self.save_log_button)

        button_layout.addStretch()

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self._stop_harvester)
        button_layout.addWidget(self.stop_button)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _start_harvester(self):
        """Start the harvester in a background thread."""
        self.status_label.setText("Starting harvester...")

        # Log configuration
        self._log_message("=" * 60)
        self._log_message("COUNTER 5.1 Harvester Started")
        self._log_message(f"Date Range: {self.config.start_date} to {self.config.end_date}")
        self._log_message(f"Vendors: {', '.join(self.config.vendors)}")
        self._log_message(f"Reports: {', '.join(self.config.reports)}")
        self._log_message("=" * 60)

        # Create and start thread
        self.harvester_thread = HarvesterThread(self.config)

        # Connect signals
        self.harvester_thread.log_signal.connect(self._log_message)
        self.harvester_thread.progress_signal.connect(self._update_progress)
        self.harvester_thread.finished_signal.connect(self._on_finished)

        # Start thread
        self.harvester_thread.start()

        self.status_label.setText("Harvester running...")

    def _log_message(self, message: str):
        """Add message to log display."""
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()

    def _update_progress(self, percentage: int):
        """Update progress bar."""
        self.progress_bar.setValue(percentage)

    def _stop_harvester(self):
        """Stop the running harvester."""
        if self.harvester_thread and self.harvester_thread.isRunning():
            self.status_label.setText("Stopping harvester...")
            self.harvester_thread.cancel()

            # Disable stop button
            self.stop_button.setEnabled(False)

    def _on_finished(self, success: bool, return_code: int):
        """Handle harvester completion."""
        if success:
            self.status_label.setText("Harvester completed successfully!")
            self._log_message("\n" + "=" * 60)
            self._log_message("HARVESTER COMPLETED SUCCESSFULLY")
            self._log_message("=" * 60)
            self.progress_bar.setValue(100)

            QMessageBox.information(self, "Success",
                                    "Harvester completed successfully!")
        else:
            if return_code == -1:
                self.status_label.setText("Harvester cancelled by user")
                self._log_message("\n" + "=" * 60)
                self._log_message("HARVESTER CANCELLED")
                self._log_message("=" * 60)
            else:
                self.status_label.setText("Harvester failed!")
                self._log_message("\n" + "=" * 60)
                self._log_message(f"HARVESTER FAILED (Code: {return_code})")
                self._log_message("=" * 60)

                QMessageBox.critical(self, "Error",
                                     f"Harvester failed with code: {return_code}")

        # Update button states
        self.stop_button.setEnabled(False)
        self.close_button.setEnabled(True)
        self.save_log_button.setEnabled(True)

    def _save_log(self):
        """Save log to file."""
        try:
            default_filename = f"Harvester_progress.txt"

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Log File",
                default_filename,
                "Text Files (*.txt);;All Files (*)"
            )

            if filename:
                log_content = self.log_text.toPlainText()

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"COUNTER 5.1 Harvester Log\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(log_content)

                self.status_label.setText(f"Log saved to: {Path(filename).name}")
                QMessageBox.information(self, "Success", "Log saved successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save log: {e}")

    def closeEvent(self, event):
        """Handle window close event."""
        if self.harvester_thread and self.harvester_thread.isRunning():
            reply = QMessageBox.question(
                self, "Harvester Running",
                "The harvester is still running. Stop it and close?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._stop_harvester()
                self.harvester_thread.wait()  # Wait for thread to finish
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()