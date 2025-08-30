import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import SushiHarvesterGUI


def main():
    """
    Application entry point function.
    Creates and starts the PyQt6 application.
    """
    # Line 8: Create QApplication instance - required for all PyQt6 apps
    # sys.argv passes command line arguments to Qt
    app = QApplication(sys.argv)

    # Line 11: Set the visual style to 'Fusion' - modern cross-platform look
    app.setStyle('Fusion')

    # Line 13: Create instance of our main window class
    window = SushiHarvesterGUI()

    # Line 15: Make the window visible on screen
    window.show()

    # Line 17: Start the application event loop and exit when window closes
    # app.exec() handles all user interactions (clicks, keyboard, etc.)
    sys.exit(app.exec())


# Line 20-21: Python idiom - only run main() when script is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    main()