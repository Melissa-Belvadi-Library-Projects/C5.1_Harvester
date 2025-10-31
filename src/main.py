# src/main.py
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from ui.main_window import SushiHarvesterGUI
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

# Defines global QSS styles for the entire GUI. it overrides defaults of windows,frames,buttons
GLOBAL_QSS = """

/* Universal defaults */
* {
    font-size: 14px;
    font-family: "Arial";
}

/* Textboxes */
QLineEdit {
    border: 2px solid #ccc;
    border-radius: 6px;
    padding: 4px;
    background-color: #ffffff;
    color: #000000;
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
    color: #000000;
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

/* Buttons - White with black borders */
QPushButton {
    border-radius: 6px;
    border: 2px solid #000000;
    background-color: #ffffff;
    color: #000000;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #f2f2f2;
    border: 2px solid #0078d7;
}
QPushButton:disabled {
    background-color: #f9f9f9;
    border: 2px solid #aaaaaa;
    color: #aaaaaa;
}

/* ComboBox (month dropdowns) */
QComboBox {
    border: 2px solid #ccc;
    border-radius: 6px;
    padding: 4px 8px;
    background-color: #ffffff;
    color: #000000;
}
QComboBox:hover {
    border: 2px solid #0078d7;
}
QComboBox:focus {
    border: 2px solid #005a9e;
    background-color: #f0f0f0;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #000000;
    selection-background-color: #0078d7;
    selection-color: #ffffff;
}

/* SpinBox (year selectors) */
QSpinBox {
    border: 2px solid #ccc;
    border-radius: 6px;
    background-color: #ffffff;
    color: #000000;
    padding: 4px 8px;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 20px;
}
QSpinBox::up-arrow, QSpinBox::down-arrow {
    width: 12px;
    height: 12px;
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

/* Labels */
QLabel {
    color: #000000;
    background-color: transparent;
}

/* App main background */
QMainWindow {
    background-color: #eff2f6;
}
QWidget {
    color: #000000;
}

/* Panels */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 6px;
    margin-top: 20px;
    padding: 8px;
    color: #000000;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    font-weight: bold;
    color: #000000;
}
"""


def set_light_palette(app):
    """Force a light color palette regardless of system theme"""
    palette = QPalette()

    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(239, 242, 246))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))

    # Base colors (for input widgets)
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))

    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))

    # Highlight colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(102, 102, 102))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(102, 102, 102))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(170, 170, 170))

    app.setPalette(palette)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Sets light palette BEFORE applying stylesheet
    set_light_palette(app)

    app.setStyleSheet(GLOBAL_QSS)

    window = SushiHarvesterGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()