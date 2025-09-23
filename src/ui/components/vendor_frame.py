from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QScrollArea, QWidget
)
from PyQt6.QtGui import QFont


class VendorFrame(QGroupBox):
    """
    Reusable widget for displaying a list of items with checkboxes.
    Used for both report type selection and provider selection.
    """

    def __init__(self, title, items):
        super().__init__(title)  # Use QGroupBox title directly (keeps alignment consistent)
        self.checkboxes = []
        self.setup_ui(items)

    def setup_ui(self, items):
        # Main vertical layout for the group box
        main_layout = QVBoxLayout(self)

        # === Top row with buttons aligned left ===
        button_layout = QHBoxLayout()

        # Create buttons first
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Clear All")

        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn.clicked.connect(self.deselect_all)

        # Add buttons to left side
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()  # Fill remaining space, keeps buttons at natural size

        # Add the button row to main layout
        main_layout.addLayout(button_layout)

        # === Scrollable checkbox list ===
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.add_items(items)
        self.scroll_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        # Add scroll area below buttons
        main_layout.addWidget(self.scroll_area)

        # Keep panel background white
        self.scroll_area.setStyleSheet("QScrollArea { background-color: white; border:1px solid black; }")
        self.scroll_widget.setStyleSheet("QWidget { background-color: white; }")

    def add_items(self, items):
        """Add checkboxes for each item in the list."""
        for item in items:
            checkbox = QCheckBox(item)
            self.checkboxes.append(checkbox)
            self.scroll_layout.addWidget(checkbox)

    def update_items(self, new_items):
        """Replace all checkboxes with a new list of items."""
        for checkbox in self.checkboxes:
            checkbox.setParent(None)
        self.checkboxes.clear()

        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.add_items(new_items)
        self.scroll_layout.addStretch()

    def get_selected(self):
        """Return list of selected (checked) item labels."""
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

    def select_all(self):
        """Check all checkboxes."""
        for cb in self.checkboxes:
            cb.setChecked(True)

    def deselect_all(self):
        """Uncheck all checkboxes."""
        for cb in self.checkboxes:
            cb.setChecked(False)

    def select_item(self, item_text):
        """Select (check) a checkbox by its text."""
        for checkbox in self.checkboxes:
            if checkbox.text() == item_text:
                checkbox.setChecked(True)
                break

