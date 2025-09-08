import sys
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


class HarvesterThread(QThread):
    """
    Background thread that runs the harvester backend without blocking the GUI.
    Inherits from QThread to execute in a separate thread from the main UI.
    Communicates with GUI through Qt signals for thread-safe updates.
    """

    # Qt signals for thread-safe communication with GUI
    log_signal = pyqtSignal(str)  # Emits log messages to display in progress dialog
    finished_signal = pyqtSignal(bool, int)  # Emits completion status (success, return_code)

    def __init__(self, config):
        """
        Constructor for harvester thread.

        Args:
            config (dict): Configuration dictionary from GUI containing user selections
        """
        # Call parent QThread constructor
        super().__init__()

        # Store configuration for use in run() method
        self.config = config

    def run(self):
        """
        Main thread execution method. Called automatically when thread.start() is invoked.
        This method runs in the background thread, separate from the GUI thread.
        """
        try:
            # Calculate path to parent directory (where backend modules are located)
            parent_dir = Path(__file__).parent.parent.parent

            # Add backend directory to Python module search path if not already present
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))

            # Import the main harvester function from backend
            # This import happens at runtime to avoid circular imports and path issues
            from getcounter import run_harvester

            # Send status message to GUI through signal
            self.log_signal.emit("Starting harvester logic...")

            # Execute the harvester backend
            #NOTE: Current implementation calls backend without GUI parameters
            # Future enhancement: pass self.config parameters to run_harvester()
            run_harvester()

            # Send completion message to GUI
            self.log_signal.emit("Harvester logic completed.")

            # Signal successful completion to GUI (success=True, exit_code=0)
            self.finished_signal.emit(True, 0)

        except ImportError as e:
            # Handle case where backend modules cannot be imported
            self.log_signal.emit(f"Cannot import harvester modules: {e}")
            self.finished_signal.emit(False, -1)  # Signal failure to GUI

        except Exception as e:
            # Handle any other errors during harvester execution

            self.log_signal.emit(f"Error: {str(e)}")  # Fixed typo
            self.finished_signal.emit(False, -1)  # Signal failure to GUI