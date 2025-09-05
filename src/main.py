import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import SushiHarvesterGUI

# Defines global QSS styles for the entire GUI. it overrides defaults of windows,frames,buttons
GLOBAL_QSS = """
* {
    font-size: 5px;
    font-family: "Segoe UI";
}

/* Textboxes */
QLineEdit {
    border: 2px solid #ccc;
    border-radius: 6px;
    padding: 4px;
    background-color: #ffffff;
}
QLineEdit:hover {
    border: 10px solid #0078d7;
}
QLineEdit:focus {
    border: 2px solid #005a9e;
    background-color: #f0f8ff;
}
QLineEdit:disabled {
    background-color: #eeeeee;
    border: 2px solid #aaaaaa;
    color: #666666;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px; /* space between box and label */
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #000000;
    background-color: #f0f0f0;
}
QCheckBox::indicator:hover {
    border: 2px solid #0078d7;
}
QCheckBox::indicator:checked {
    background-color: #0078d7;
    border: 2px solid #0078d7;

}
QCheckBox::indicator:checked:hover {
    background-color: #005a9e;
    border: 2px solid #005a9e;
}
QCheckBox::indicator:disabled {
    background-color: #d3d3d3;
    border: 2px solid #a0a0a0;
}

/* Buttons */
QPushButton {
    border-radius: 6px;
    border: 2px solid #0078d7;
    background-color: #0078d7;
    color: white;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #005a9e;
}
QPushButton:disabled {
    background-color: #cccccc;
    border: 2px solid #aaaaaa;
    color: #666666;
}

/* Universal defaults */
* {
    font-size: 14px;
    font-family: "Roboto", "Segoe UI", sans-serif;
}

/* Textboxes */
QLineEdit {
    border: 2px solid #ccc;
    border-radius: 6px;
    padding: 4px;
    background-color: #ffffff;
}
QLineEdit:hover {
    border: 2px solid #0078d7;
}
QLineEdit:focus {
    border: 2px solid #005a9e;
    background-color: #f0f8ff;
}
QLineEdit:disabled {
    background-color: #eeeeee;
    border: 2px solid #aaaaaa;
    color: #666666;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #000000;
    background-color: #f0f0f0;
}
QCheckBox::indicator:hover {
    border: 2px solid #0078d7;
}
QCheckBox::indicator:checked {
    background-color: #0078d7;
    border: 2px solid #0078d7;
    image: url(:/qt-project.org/styles/commonstyle/images/checkmark-16.svg);
}
QCheckBox::indicator:checked:hover {
    background-color: #005a9e;
    border: 2px solid #005a9e;
}
QCheckBox::indicator:disabled {
    background-color: #d3d3d3;
    border: 2px solid #a0a0a0;
}

/* Buttons */
QPushButton {
    border-radius: 6px;
    border: 2px solid #0078d7;
    background-color: #0078d7;
    color: white;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #005a9e;
}
QPushButton:disabled {
    background-color: #cccccc;
    border: 2px solid #aaaaaa;
    color: #666666;
}

/* ComboBox (month dropdowns) */
QComboBox {
    border: 2px solid #ccc;
    border-radius: 6px;
    padding: 4px 8px;
    background-color: #ffffff;
}
QComboBox:hover {
    border: 2px solid #0078d7;
}
QComboBox:focus {
    border: 2px solid #005a9e;
    background-color: #f0f8ff;
}
QComboBox::drop-down {
    border: none;
}
QComboBox::down-arrow {
    image: url(:/qt-project.org/styles/commonstyle/images/downarrow-16.svg);
}

/* SpinBox (year selectors) */
QSpinBox {
    border: 2px solid #ccc;
    border-radius: 6px;
    padding: 4px;
    background-color: #ffffff;
}
QSpinBox:hover {
    border: 2px solid #0078d7;
}
QSpinBox:focus {
    border: 2px solid #005a9e;
    background-color: #f0f8ff;
}
QSpinBox:disabled {
    background-color: #eeeeee;
    border: 2px solid #aaaaaa;
    color: #666666;
}

QGroupBox {
    background-color: #ffffff;   /* pure white instead of gray */
    border: 1px solid #cccccc;
    border-radius: 6px;
    margin-top: 10px;   /* space for the title */
    padding: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    font-weight: bold;
    color: #000000;
}

"""

def main():
    """
    Application entry point function.
    Creates and starts the PyQt6 application.
    """
    # Create QApplication instance - required for all PyQt6 apps
    app = QApplication(sys.argv)

    # Set the visual style to 'Fusion' - modern cross-platform look
    app.setStyle('Fusion')

    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_QSS)

    # Create instance of our main window class
    window = SushiHarvesterGUI()

    # Make the window visible on screen
    window.show()

    # Start the application event loop and exit when window closes
    sys.exit(app.exec())


# only run main() when script is executed directly
if __name__ == "__main__":
    main()
