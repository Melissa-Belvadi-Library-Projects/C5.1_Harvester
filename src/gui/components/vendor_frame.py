from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QScrollArea, QWidget
)
from PyQt6.QtGui import QFont


class VendorFrame(QGroupBox):
    """
    Reusable widget for displaying a list of items with checkboxes.
    Used for both report type selection and provider selection.
    Inherits from QGroupBox to get a titled border around the content.
    """

    def __init__(self, title, items):
        """
        Constructor for VendorFrame widget.

        Args:
            title (str): Title displayed at the top of the frame
            items (list): List of strings to display as checkboxes
        """
        # Call parent constructor with the title
        super().__init__(title)

        # Set minimum height to ensure adequate space for content
        self.setMinimumHeight(250)

        # List to store references to checkbox widgets for later access
        self.checkboxes = []

        # Build the user interface with the provided items
        self.setup_ui(items)

    def setup_ui(self, items):
        """
        Creates and arranges all UI elements within the frame.
        Sets up the layout hierarchy: buttons at top, scrollable checkboxes below.

        Args:
            items (list): List of items to create checkboxes for
        """
        # Main vertical layout - stacks button row above checkbox area
        layout = QVBoxLayout()

        # Horizontal layout for the Select All and Deselect All buttons
        button_layout = QHBoxLayout()

        # Create the control buttons with consistent styling
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Deselect All")
        select_all_btn.setFont(QFont("Arial", 10))
        deselect_all_btn.setFont(QFont("Arial", 10))

        # Connect button clicks to their respective handler methods
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn.clicked.connect(self.deselect_all)

        # Add buttons to horizontal layout
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()  # Pushes buttons to the left side

        # Add the button row to the main vertical layout
        layout.addLayout(button_layout)

        # Create scrollable area for the checkbox list
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()  # Container widget for the scroll content
        self.scroll_layout = QVBoxLayout(self.scroll_widget)  # Layout for checkboxes

        # Populate the scroll area with checkboxes
        self.add_items(items)

        # Add stretch at bottom to keep checkboxes grouped at top
        self.scroll_layout.addStretch()

        # Configure the scroll area
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)  # Allow content to resize with scroll area

        # Add scroll area to main layout
        layout.addWidget(self.scroll_area)

        # Apply the complete layout to this widget
        self.setLayout(layout)

    def add_items(self, items):
        """
        Creates checkbox widgets for each item in the provided list.
        Stores references to checkboxes for later manipulation.

        Args:
            items (list): List of strings to create checkboxes for
        """
        for item in items:
            # Create checkbox with the item text as label
            checkbox = QCheckBox(item)
            # Store reference in our list for later access (select all, get selected, etc.)
            self.checkboxes.append(checkbox)
            # Add checkbox to the scrollable layout
            self.scroll_layout.addWidget(checkbox)

    def update_items(self, new_items):
        """
        Replaces all current checkboxes with a new set of items.
        Used when the underlying data changes (e.g., provider list updated).

        Args:
            new_items (list): New list of items to display as checkboxes
        """
        # Remove all existing checkbox widgets from the UI
        for checkbox in self.checkboxes:
            checkbox.setParent(None)  # Removes widget from parent layout

        # Clear our reference list
        self.checkboxes.clear()

        # Clean up the layout by removing any remaining items
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()  # Properly delete the widget from memory

        # Add the new items as checkboxes
        self.add_items(new_items)

        # Re-add the stretch to keep checkboxes at top
        self.scroll_layout.addStretch()

    def get_selected(self):
        """
        Returns a list of text labels from all currently checked checkboxes.
        Used by parent widgets to determine what items the user has selected.

        Returns:
            list: List of strings representing selected item names
        """
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

    def select_all(self):
        """
        Handler method for Select All button.
        Iterates through all checkboxes and sets them to checked state.
        """
        for cb in self.checkboxes:
            cb.setChecked(True)

    def deselect_all(self):
        """
        Handler method for Deselect All button.
        Iterates through all checkboxes and sets them to unchecked state.
        """
        for cb in self.checkboxes:
            cb.setChecked(False)