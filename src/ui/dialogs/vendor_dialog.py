# ui/dialogs/vendor_dialog.py
"""Vendor management dialog with state management."""

import webbrowser
from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QWidget, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import uuid
from typing import Optional, List, Dict
from help_file import get_help_url


class VendorManagementDialog(QDialog):
    """
    Dialog for managing vendors with state-based approach.
    No direct file I/O - emits signals when vendors are changed.
    Signals: vendorsChanged (names list), vendorsDataChanged (full data)

    """

    # Signal emitted when vendors list changes
    vendorsChanged = pyqtSignal(list)  # List of vendor names
    vendorsDataChanged = pyqtSignal(object)  # Full vendor data

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None, parent=None):
        """Initialize with optional initial state."""
        super().__init__(parent)

        self.setWindowTitle("Manage Providers")
        self.resize(1000, 500)

        # State management
        self._vendors_data: List[Dict[str, str]] = []
        self._current_vendor: Optional[Dict[str, str]] = None
        self._has_unsaved_changes = False
        self._updating = False

        # Build UI
        self._setup_ui()

        # Apply initial state if provided
        if initial_state:
            self.set_state(initial_state)

        self.toggle_details_panel(False)

    def _setup_ui(self):
        """Create the UI layout."""
        main_layout = QVBoxLayout(self)

        # Create splitter for two-panel layout
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # left panel is the list of vendors
        left_panel = self._create_vendor_list_panel()

        # right panel is where the user cna modify the provider details
        right_panel = self._create_vendor_details_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600])

        main_layout.addWidget(splitter)

        # Bottom buttons
        button_layout = QHBoxLayout()

        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self._handle_close)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

    def _create_vendor_list_panel(self) -> QWidget:
        """Create the left panel with vendor list."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        list_label = QLabel("Providers:")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(list_label)

        self.vendor_list = QListWidget()
        self.vendor_list.itemClicked.connect(self._on_vendor_selected)
        layout.addWidget(self.vendor_list)

        # List control buttons
        list_buttons = QHBoxLayout()
        list_buttons.addStretch()

        self.add_btn = QPushButton("Add Provider")
        self.remove_btn = QPushButton("Remove Provider")
        self.remove_btn.setEnabled(False)

        self.add_btn.clicked.connect(self._add_vendor)
        self.remove_btn.clicked.connect(self._remove_vendor)

        list_buttons.addWidget(self.add_btn)
        list_buttons.addSpacing(10)
        list_buttons.addWidget(self.remove_btn)
        list_buttons.addStretch()

        layout.addLayout(list_buttons)

        return panel

    def _create_vendor_details_panel(self) -> QWidget:

        """Creates the right panel with vendor details form."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        details_label = QLabel("Provider Details:")
        details_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(details_label)

        # Guidance message
        self.guidance_label = QLabel(
            "Select a provider from the list or use 'Add Provider' to begin editing."
        )
        self.guidance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guidance_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.guidance_label)

        # Form widget
        self.form_widget = QWidget()
        form_layout = QFormLayout(self.form_widget)

        # Create form fields
        self.name_edit = QLineEdit()
        self.base_url_edit = QLineEdit()
        self.customer_id_edit = QLineEdit()
        self.requestor_id_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.platform_edit = QLineEdit()
        self.version_edit = QLineEdit()
        self.version_edit.setText("5.1")
        self.delay_edit = QLineEdit()
        self.retry_edit = QLineEdit()

        # Add fields to form
        form_layout.addRow("Name*:", self.name_edit)
        form_layout.addRow("Base URL*:", self.base_url_edit)
        form_layout.addRow("Customer ID*:", self.customer_id_edit)
        form_layout.addRow("Requestor ID:", self.requestor_id_edit)
        form_layout.addRow("API Key:", self.api_key_edit)
        form_layout.addRow("Platform:", self.platform_edit)
        form_layout.addRow("Version:", self.version_edit)
        form_layout.addRow("Delay (seconds):", self.delay_edit)
        form_layout.addRow("Retry:", self.retry_edit)

        # Connect field changes
        for edit in [self.name_edit, self.base_url_edit, self.customer_id_edit,
                     self.requestor_id_edit, self.api_key_edit, self.platform_edit,
                     self.version_edit, self.delay_edit, self.retry_edit]:
            edit.textChanged.connect(self._on_field_changed)

        # Save button for current vendor
        save_button_layout = QHBoxLayout()
        save_button_layout.addStretch()

        self.save_vendor_btn = QPushButton("Save Provider")
        self.save_vendor_btn.setFixedSize(120, 30)
        self.save_vendor_btn.setEnabled(False)
        self.save_vendor_btn.clicked.connect(self._save_current_vendor)

        save_button_layout.addWidget(self.save_vendor_btn)
        save_button_layout.addStretch()

        save_button_widget = QWidget()
        save_button_widget.setLayout(save_button_layout)
        form_layout.addRow(save_button_widget)

        layout.addWidget(self.form_widget)
        layout.addStretch()

        return panel

    def get_state(self) -> Dict[str, Any]:
        """
        Get current state as a dictionary.

        Returns:
            Dict with 'vendors' key containing list of vendor dictionaries
        """
        return {
            "vendors": self._vendors_data.copy()
        }

    def set_state(self, state: Dict[str, Any]):
        self._updating = True
        try:
            if "vendors" in state:
                self._vendors_data = [v.copy() for v in state["vendors"]]

                # Ensure all vendors have IDs
                for vendor in self._vendors_data:
                    if 'Id' not in vendor or not vendor.get('Id'):
                        vendor['Id'] = str(uuid.uuid4())

                self._refresh_vendor_list()
        finally:
            self._updating = False

    def _refresh_vendor_list(self):
        """Refresh the vendor list widget."""
        self.vendor_list.clear()

        for vendor in self._vendors_data:
            if vendor.get('Name', '').strip():
                item = QListWidgetItem(vendor['Name'])
                vendor_id = vendor.get('Id')
                item.setData(Qt.ItemDataRole.UserRole, vendor.get('Id'))
                self.vendor_list.addItem(item)

    def toggle_details_panel(self, enabled: bool):
        """Show/hide the details form."""
        self.form_widget.setVisible(enabled)
        self.guidance_label.setVisible(not enabled)

    def _on_vendor_selected(self, item: QListWidgetItem):
        """Handle vendor selection from list."""

        vendor_id = item.data(Qt.ItemDataRole.UserRole)

        if self._has_unsaved_changes:

            if not self._validate_current_vendor():
                return

            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Save changes to current provider?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard
            )

            if reply == QMessageBox.StandardButton.Save:
                if not self._save_current_vendor():
                    return

        self.toggle_details_panel(True)

        found = False
        for vendor in self._vendors_data:
            if vendor.get('Id') == vendor_id:
                self._current_vendor = vendor
                self._populate_form(vendor)
                self.remove_btn.setEnabled(True)
                found = True
                break
        if not found:
            print(f"DEBUG: NO MATCH FOUND for ID {vendor_id}")

    def _add_vendor(self):
        """Add a new vendor."""
        if self._has_unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Save changes to current provider?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard
            )

            if reply == QMessageBox.StandardButton.Save:
                if not self._save_current_vendor():
                    return

        self.toggle_details_panel(True)

        new_vendor = {
            'Id': str(uuid.uuid4()),
            'Name': '',
            'Base_URL': '',
            'Customer_ID': '',
            'Requestor_ID': '',
            'API_Key': '',
            'Platform': '',
            'Version': '5.1',
            'Delay': '',
            'Retry': ''
        }

        self._vendors_data.append(new_vendor)

        item = QListWidgetItem(new_vendor['Name'])
        item.setData(Qt.ItemDataRole.UserRole, new_vendor['Id'])  # ID
        self.vendor_list.addItem(item)
        self.vendor_list.setCurrentItem(item)

        self._current_vendor = new_vendor
        self._populate_form(new_vendor)
        self.remove_btn.setEnabled(True)

        self.name_edit.selectAll()
        self.name_edit.setFocus()
    def _remove_vendor(self):
        """Remove selected vendor."""
        current_item = self.vendor_list.currentItem()
        if not current_item:
            return
        vendor_name = current_item.text()

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Removal")
        msg_box.setText(f"Are you sure you want to remove {vendor_name}?")

        msg_box.setIcon(QMessageBox.Icon.Question)

        yes_btn = msg_box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        no_btn = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(no_btn)

        msg_box.exec()

        if msg_box.clickedButton() == yes_btn:
            vendor_id = current_item.data(Qt.ItemDataRole.UserRole)

            # Remove from data
            self._vendors_data = [
                v for v in self._vendors_data
                if v.get('Id') != vendor_id
            ]

            # Remove from list widget
            row = self.vendor_list.row(current_item)
            self.vendor_list.takeItem(row)

            self._current_vendor = None
            self._clear_form()
            self.vendor_list.clearSelection()
            self.remove_btn.setEnabled(False)

            # Check if emission happens
            if not self._updating:
                self._emit_vendors_changed()

    def _populate_form(self, vendor_data: Dict[str, str]):
        """Fill form with vendor data."""
        self._updating = True

        self.name_edit.setText(vendor_data.get('Name', ''))
        self.base_url_edit.setText(vendor_data.get('Base_URL', ''))
        self.customer_id_edit.setText(vendor_data.get('Customer_ID', ''))
        self.requestor_id_edit.setText(vendor_data.get('Requestor_ID', ''))
        self.api_key_edit.setText(vendor_data.get('API_Key', ''))
        self.platform_edit.setText(vendor_data.get('Platform', ''))
        self.version_edit.setText(vendor_data.get('Version', '5.1'))
        self.delay_edit.setText(vendor_data.get('Delay', ''))
        self.retry_edit.setText(vendor_data.get('Retry', ''))

        self.save_vendor_btn.setEnabled(False)
        self._has_unsaved_changes = False
        self._updating = False

    def _clear_form(self):
        """Clear all form fields."""
        self._updating = True

        for edit in [self.name_edit, self.base_url_edit, self.customer_id_edit,
                     self.requestor_id_edit, self.api_key_edit, self.platform_edit,
                     self.delay_edit, self.retry_edit]:
            edit.clear()

        self.version_edit.setText("5.1")
        self.save_vendor_btn.setEnabled(False)
        self._has_unsaved_changes = False

        self.toggle_details_panel(False)
        self._updating = False

    def _on_field_changed(self):
        """Handle field value changes."""
        if self._updating:
            return

        self._has_unsaved_changes = True

        # Enable save if required fields are filled
        name_filled = bool(self.name_edit.text().strip())
        url_filled = bool(self.base_url_edit.text().strip())
        id_filled = bool(self.customer_id_edit.text().strip())

        self.save_vendor_btn.setEnabled(
            name_filled and url_filled and id_filled and (self._current_vendor is not None)
        )

    def _save_current_vendor(self) -> bool:

        """Save current vendor to memory (not file)."""
        if not self._current_vendor:
            return False

        if not self._validate_current_vendor():
            return False

        new_name = self.name_edit.text().strip()

        # Update vendor data
        self._current_vendor['Name'] = self.name_edit.text().strip()
        self._current_vendor['Base_URL'] = self.base_url_edit.text().strip()
        self._current_vendor['Customer_ID'] = self.customer_id_edit.text().strip()
        self._current_vendor['Requestor_ID'] = self.requestor_id_edit.text().strip()
        self._current_vendor['API_Key'] = self.api_key_edit.text().strip()
        self._current_vendor['Platform'] = self.platform_edit.text().strip()
        self._current_vendor['Version'] = self.version_edit.text().strip()
        self._current_vendor['Delay'] = self.delay_edit.text().strip()
        self._current_vendor['Retry'] = self.retry_edit.text().strip()

        # Update list item
        # current_item = self.vendor_list.currentItem()
        # if current_item:
        #     current_item.setText(self._current_vendor['Name'])

        # Sort vendors alphabetically
        self._vendors_data.sort(key=lambda v: v.get('Name', '').lower())

        # Refreshes the list to show sorted order
        current_vendor_id = self._current_vendor.get('Id')
        self._refresh_vendor_list()

        # Re-select the current vendor
        for i in range(self.vendor_list.count()):
            item = self.vendor_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == current_vendor_id:
                self.vendor_list.setCurrentItem(item)
                break

        self.save_vendor_btn.setEnabled(False)
        self._has_unsaved_changes = False

        # This ensures app state is always current
        self._emit_vendors_changed()
        return True

    def _validate_current_vendor(self):
        """Validate current vendor data."""
        name = self.name_edit.text().strip()
        base_url = self.base_url_edit.text().strip()
        customer_id = self.customer_id_edit.text().strip()

        missing_fields = []
        if not name:
            missing_fields.append("Name")

        if not base_url:
            missing_fields.append("Base URL")

        if not customer_id:
            missing_fields.append("Customer ID")

        if missing_fields:
            QMessageBox.warning(
                self, "Validation Error",
                f"The following required fields are missing:\n\n" +
                "\n".join(f"• {field}" for field in missing_fields)
            )
            return False

        new_name = self.name_edit.text().strip()
        if new_name:  # Only check if name is filled
            for vendor in self._vendors_data:
                if vendor != self._current_vendor and vendor.get('Name') == new_name:
                    QMessageBox.warning(
                        self, "Duplicate Name",
                        f"A provider named '{new_name}' already exists.\n"
                        f"Please use a unique name."
                    )
                    return False

        return True

    def _save_all(self):
        """Save all vendors and emit signal."""
        if self._has_unsaved_changes:
            if not self._save_current_vendor():
                return False

        self._emit_vendors_changed()
        return True

    def _emit_vendors_changed(self):
        """Emit vendor change signals."""
        vendor_names = [v['Name'] for v in self._vendors_data
                        if v.get('Name', '').strip()]
        self.vendorsChanged.emit(vendor_names)
        self.vendorsDataChanged.emit(self._vendors_data)

    def _handle_close(self):
        """Handle close button click."""
        if self._has_unsaved_changes:

            if not self._validate_current_vendor():
                return

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Unsaved Changes")
            msg_box.setText("You have unsaved changes.")
            msg_box.setInformativeText("Would you like to save before closing?")
            msg_box.setIcon(QMessageBox.Icon.Question)

            # Just two clear options
            save_btn = msg_box.addButton("Save And Close", QMessageBox.ButtonRole.AcceptRole)
            discard_btn = msg_box.addButton("Close Without Saving", QMessageBox.ButtonRole.RejectRole)
            # cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

            msg_box.setDefaultButton(save_btn)
            msg_box.exec()

            if msg_box.clickedButton() == save_btn:
                if self._save_all():
                    self.accept()

            elif msg_box.clickedButton() == discard_btn:
                self.reject()

        else:
            self.accept()

    # def _show_help(self):
    #     """Show help documentation."""
    #     help_url = get_help_url("providers")
    #
    #     reply = QMessageBox.question(
    #         self, "Provider Management Help",
    #         "Open Provider help documentation in browser?",
    #         QMessageBox.StandardButton.Yes |
    #         QMessageBox.StandardButton.No
    #     )
    #
    #     if reply == QMessageBox.StandardButton.Yes:
    #         try:
    #             webbrowser.open(help_url)
    #         except Exception as e:
    #             QMessageBox.information(
    #                 self, "Help",
    #                 f"Please visit:\n{help_url}\n\n"
    #                 f"(Could not open browser: {e})"
    #             )
    def _show_help(self):
        """Show help documentation for settings dialog."""

        help_url = get_help_url('providers')

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Provider Management Help")
        msg_box.setText("Open the Provider Help page in your browser?")
        # msg_box.setIcon(QMessageBox.Icon.Question)

        yes_btn = msg_box.addButton("Open", QMessageBox.ButtonRole.YesRole)
        no_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.NoRole)

        msg_box.setDefaultButton(yes_btn)
        msg_box.exec()

        if msg_box.clickedButton() == yes_btn:
            try:
                webbrowser.open(help_url)
            except Exception as e:
                QMessageBox.information(
                    self, "Help",
                    f"Please visit:\n{help_url}\n\n"
                    f"(Could not open browser: {e})"
                )



    def closeEvent(self, event):
        """Handle window close event (X button)."""
        if self._has_unsaved_changes:
            event.ignore()  # Don't close yet
            self._handle_close()  # Use existing close logic
        else:
            event.accept()  # Allow close
