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
    Modal dialog that displays real-time progress of the harvester operation.
    Provides controls for stopping the process and saving log output.
    Inherits from QDialog to create a modal window that blocks interaction with main window.
    """

    def __init__(self, parent=None):
        """
        Constructor for the progress dialog.

        Args:
            parent: Parent window (typically the main application window)
        """
        # Call parent constructor
        super().__init__(parent)

        # Configure dialog window properties
        self.setWindowTitle("Harvester Progress")
        self.setFixedSize(800, 600)  # Fixed size to prevent resizing

        # Make dialog modal - user must interact with this dialog before returning to main window
        self.setModal(True)

        # Initialize reference to background thread (will be set when harvester starts)
        self.harvester_thread = None

        # Build the user interface
        self.setup_ui()

    def setup_ui(self):
        """
        Creates and arranges all UI elements in the dialog.
        Layout: status label at top, log area in middle, control buttons at bottom.
        """
        # Main vertical layout for the entire dialog
        layout = QVBoxLayout(self)

        # Status label at top - shows current harvester state
        self.status_label = QLabel("Preparing to start harvester...")
       # self.status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.status_label)

        # Large text area for displaying log messages
        self.log_text = QTextEdit()
       # self.log_text.setFont(QFont("Arial", 9))
        self.log_text.setReadOnly(True)  # User cannot edit log content
        layout.addWidget(self.log_text)

        # Horizontal layout for control buttons at bottom
        button_layout = QHBoxLayout()

        # Save Log button on the left side
        self.save_log_button = QPushButton("Save Message Log")
       # self.save_log_button.setFont(QFont("Arial", 10))
        self.save_log_button.clicked.connect(self.save_message_log)
        button_layout.addWidget(self.save_log_button)

        # Stretch pushes remaining buttons to the right
        button_layout.addStretch()

        # Stop button - terminates the running harvester
        self.stop_button = QPushButton("STOP")
       # self.stop_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.stop_button.clicked.connect(self.stop_harvester)
        button_layout.addWidget(self.stop_button)

        # Close button - closes dialog (disabled during harvester execution)
        self.close_button = QPushButton("CLOSE")
       # self.close_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.close_button.setEnabled(False)  # Disabled until harvester finishes
        self.close_button.clicked.connect(self.accept)  # Closes dialog with "accepted" status
        button_layout.addWidget(self.close_button)

        # Add button layout to main layout
        layout.addLayout(button_layout)

    def save_message_log(self):
        """
        Allows user to save the current log messages to a text file.
        Opens a file dialog for user to choose location and filename.
        """
        try:
            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"harvester_log_{timestamp}.txt"

            # Open file save dialog
            filename, _ = QFileDialog.getSaveFileName(
                self,  # Parent widget
                "Save Message Log",  # Dialog title
                default_filename,  # Default filename
                "Text Files (*.txt);;All Files (*)"  # File type filters
            )

            # If user selected a file (didn't cancel)
            if filename:
                # Get all text content from the log display
                log_content = self.log_text.toPlainText()

                # Write to file with header and timestamp
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"SUSHI Harvester Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")  # Separator line
                    f.write(log_content)

                # Update status to show successful save
                self.status_label.setText(f"Log saved to: {os.path.basename(filename)}")

                # Add confirmation message to the log itself
                self.log_message(f"\n--- Log saved to: {filename} ---")

        except Exception as e:
            # Show error dialog if file save fails
            QMessageBox.critical(self, "Save Error", f"Failed to save log file:\n{str(e)}")

    def start_harvester(self, config):
        """
        Initiates the harvester process with the provided configuration.
        Creates and starts the background thread.

        Args:
            config (dict): Dictionary containing user selections (providers, dates, reports)
        """
        # Update status to show harvester is starting
        self.status_label.setText("Starting harvester...")

        # Create harvester thread with user configuration
        self.harvester_thread = HarvesterThread(config)

        # Connect thread signals to dialog methods
        self.harvester_thread.log_signal.connect(self.log_message)  # Log messages from thread
        self.harvester_thread.finished_signal.connect(self.on_harvester_finished)  # Completion notification

        # Start the background thread
        self.harvester_thread.start()

        # Update status to show harvester is now running
        self.status_label.setText("Harvester running...")

    def log_message(self, message):
        """
        Adds a new message to the log display area.
        Called by the harvester thread to provide progress updates.

        Args:
            message (str): Message to add to the log
        """
        # Append message to the text area
        self.log_text.append(message)

        # Automatically scroll to show the newest message
        self.log_text.ensureCursorVisible()

    def stop_harvester(self):
        """
        Forcibly terminates the running harvester process.
        Called when user clicks the STOP button.
        """
        # Check if harvester thread exists and is running
        if self.harvester_thread and self.harvester_thread.isRunning():
            # Update status to show stopping process
            self.status_label.setText("Stopping harvester...")

            # Terminate the thread (forced shutdown)
            self.harvester_thread.terminate()

            # Wait for thread to fully stop
            self.harvester_thread.wait()

            # Call completion handler with failure status
            self.on_harvester_finished(False, -1)  # -1 indicates user-initiated stop

    def on_harvester_finished(self, success, return_code):
        """
        Handles harvester completion, whether successful or failed.
        Updates UI state and shows appropriate messages to user.

        Args:
            success (bool): True if harvester completed successfully
            return_code (int): Exit code from harvester process
        """
        if success:
            # Handle successful completion
            self.status_label.setText("Harvester completed successfully!")
            self.log_message("\n=== HARVESTER COMPLETED SUCCESSFULLY ===")

            # Show success popup to user
            QMessageBox.information(self, "Success", "Harvester run completed successfully!")

        else:
            # Handle failure
            self.status_label.setText("Harvester failed!")
            self.log_message(f"\n=== HARVESTER FAILED (Exit Code: {return_code}) ===")

            # Only show error popup for actual failures (not user stops)
            if return_code != -1:  # -1 is used for user-initiated stops
                QMessageBox.critical(self, "Error", f"Harvester failed with exit code: {return_code}")

        # Update button states - disable stop, enable close
        self.stop_button.setEnabled(False)
        self.close_button.setEnabled(True)

    def closeEvent(self, event):
        """
        Handles user attempting to close the dialog window.
        Prevents accidental closure while harvester is running.

        Args:
            event: Close event from Qt framework
        """
        # Check if harvester is still running
        if self.harvester_thread and self.harvester_thread.isRunning():
            # Ask user to confirm they want to stop the harvester
            reply = QMessageBox.question(
                self,
                "Harvester Running",
                "The harvester is still running. Do you want to stop it and close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # User confirmed - stop harvester and allow close
                self.stop_harvester()
                event.accept()
            else:
                # User cancelled - prevent dialog from closing
                event.ignore()
        else:
            # Harvester not running - allow normal close
            event.accept()