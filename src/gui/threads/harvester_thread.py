import sys
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


class HarvesterThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, int)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            # Add parent directory to Python path if necessary
            parent_dir = Path(__file__).parent.parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))


            from getcounter import run_harvester

            self.log_signal.emit("Starting harvester logic...")

            # This is where you would pass any necessary arguments to run_harvester if it took any.
            # Since the function you've created takes no arguments, you just call it directly.
            run_harvester()

            self.log_signal.emit("Harvester logic completed.")
            self.finished_signal.emit(True, 0)  # Signal success

        except ImportError as e:
            self.log_signal.emit(f"Cannot import harvester modules: {e}")
            self.finished_signal.emit(False, -1)
        except Exception as e:
            self.lopythg_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False, -1)