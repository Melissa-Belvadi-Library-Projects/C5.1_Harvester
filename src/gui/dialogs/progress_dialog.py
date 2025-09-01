import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QFont
from ..threads.harvester_thread import HarvesterThread


class ProgressDialog(QDialog):
    """
    Modal dialog that shows harvester progress and allows stopping the process.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Harvester Progress")
        self.setFixedSize(800, 600)

        # Make this dialog modal
        self.setModal(True)

        # Reference to harvester thread
        self.harvester_thread = None

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Progress label
        self.status_label = QLabel("Preparing to start harvester...")
        self.status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.status_label)

        # Progress text area
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Arial", 9))
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Button layout
        button_layout = QHBoxLayout()

        # Left side - Save Log button
        self.save_log_button = QPushButton("Save Message Log")
        self.save_log_button.setFont(QFont("Arial", 10))
        self.save_log_button.clicked.connect(self.save_message_log)
        button_layout.addWidget(self.save_log_button)

        # Add stretch to push STOP and CLOSE to the right
        button_layout.addStretch()

        self.stop_button = QPushButton("STOP")
        self.stop_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.stop_button.clicked.connect(self.stop_harvester)
        button_layout.addWidget(self.stop_button)

        self.close_button = QPushButton("CLOSE")
        self.close_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.close_button.setEnabled(False)  # Disabled until harvester finishes
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def save_message_log(self):
        """Save the current log messages to a file."""
        try:
            # Get current timestamp for default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"harvester_log_{timestamp}.txt"

            # Open file dialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Message Log",
                default_filename,
                "Text Files (*.txt);;All Files (*)"
            )

            if filename:
                # Save the log content
                log_content = self.log_text.toPlainText()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"SUSHI Harvester Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(log_content)

                # Update status to show save success
                self.status_label.setText(f"Log saved to: {os.path.basename(filename)}")

                # Show brief confirmation in the log
                self.log_message(f"\n--- Log saved to: {filename} ---")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save log file:\n{str(e)}")

    def start_harvester(self, config):
        """Start the harvester with given configuration."""
        self.status_label.setText("Starting harvester...")

        # Create and configure harvester thread
        self.harvester_thread = HarvesterThread(config)
        self.harvester_thread.log_signal.connect(self.log_message)
        self.harvester_thread.finished_signal.connect(self.on_harvester_finished)

        # Start the thread
        self.harvester_thread.start()
        self.status_label.setText("Harvester running...")

    def log_message(self, message):
        """Add a message to the progress log."""
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()

    def stop_harvester(self):
        """Stop the running harvester."""
        if self.harvester_thread and self.harvester_thread.isRunning():
            self.status_label.setText("Stopping harvester...")
            self.harvester_thread.terminate()
            self.harvester_thread.wait()
            self.on_harvester_finished(False, -1)

    def on_harvester_finished(self, success, return_code):
        """Handle harvester completion."""
        if success:
            self.status_label.setText("Harvester completed successfully!")
            self.log_message("\n=== HARVESTER COMPLETED SUCCESSFULLY ===")

            # Show success popup with just OK button
            QMessageBox.information(self, "Success", "Harvester run completed successfully!")

        else:
            self.status_label.setText("Harvester failed!")
            self.log_message(f"\n=== HARVESTER FAILED (Exit Code: {return_code}) ===")

            # Only show error popup for actual failures (not user stops)
            if return_code != -1:  # -1 is used for user-initiated stops
                QMessageBox.critical(self, "Error", f"Harvester failed with exit code: {return_code}")

        # Enable close button and disable stop button
        self.stop_button.setEnabled(False)
        self.close_button.setEnabled(True)

    def closeEvent(self, event):
        """Handle window close event - ensure harvester is stopped."""
        if self.harvester_thread and self.harvester_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Harvester Running",
                "The harvester is still running. Do you want to stop it and close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_harvester()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()