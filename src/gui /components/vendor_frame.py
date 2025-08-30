from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QScrollArea, QWidget
)
from PyQt6.QtGui import QFont


class VendorFrame(QGroupBox):
    def __init__(self, title, items):
        super().__init__(title)
        self.setMinimumHeight(250)
        self.checkboxes = []
        self.setup_ui(items)

    def setup_ui(self, items):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Deselect All")
        select_all_btn.setFont(QFont("Arial", 10))
        deselect_all_btn.setFont(QFont("Arial", 10))

        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn.clicked.connect(self.deselect_all)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.add_items(items)

        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

    def add_items(self, items):
        """Add items as checkboxes"""
        for item in items:
            checkbox = QCheckBox(item)
            self.checkboxes.append(checkbox)
            self.scroll_layout.addWidget(checkbox)

    def update_items(self, new_items):
        """Update the list with new items"""
        # Clear existing checkboxes
        for checkbox in self.checkboxes:
            checkbox.setParent(None)
        self.checkboxes.clear()

        # Clear the layout
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add new items
        self.add_items(new_items)
        self.scroll_layout.addStretch()

    def get_selected(self):
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

    def select_all(self):
        for cb in self.checkboxes:
            cb.setChecked(True)

    def deselect_all(self):
        for cb in self.checkboxes:
            cb.setChecked(False)