import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import SushiHarvesterGUI


def main():
    """
    Application entry point function.
    Creates and starts the PyQt6 application.
    """
    # Create QApplication instance - required for all PyQt6 apps
    # sys.argv passes command line arguments to Qt
    app = QApplication(sys.argv)

    # Set the visual style to 'Fusion' - modern cross-platform look
    app.setStyle('Fusion')

    # Create instance of our main window class
    window = SushiHarvesterGUI()

    # Make the window visible on screen
    window.show()

    # Start the application event loop and exit when window closes
    # app.exec() handles all user interactions (clicks, keyboard, etc.)
    sys.exit(app.exec())


#  only run main() when script is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    main()