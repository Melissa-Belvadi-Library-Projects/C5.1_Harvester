import csv
import webbrowser
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QWidget, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import QAbstractItemView


class VendorManagementDialog(QDialog):
    """Dialog for managing vendors in the TSV file"""

    def __init__(self, parent=None, config_data=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Providers")
        self.setFixedSize(900, 600)
        self.config_data = config_data
        self.vendors_data = []
        self.current_vendor = None

        self.setup_ui()
        self.load_vendors()
        self.toggle_details_panel(False)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = self.create_vendor_list_panel()
        right_panel = self.create_vendor_details_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600])

        main_layout.addWidget(splitter)

        button_layout = QHBoxLayout()
        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self.show_provider_help)
        button_layout.addWidget(help_btn)
        button_layout.addStretch()

        # The Close button is now connected to the dialog's `close` method
        # which triggers the `closeEvent`.
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

    def closeEvent(self, event):
        """Handle the close event to check for unsaved changes."""
        # Check if the save button is enabled (indicating unsaved changes)
        if self.save_changes_btn.isEnabled():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before closing?",

                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
            )

            if reply == QMessageBox.StandardButton.Save:
                # Save the current vendor first
                self.save_current_vendor()
                if not self.save_changes_btn.isEnabled():  # Check if save was successful
                    # Now save all changes to TSV file
                    self.save_all_and_close()
                    return  # save_all_and_close() handles closing
                else:
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Discard:
                # Save to file anyway (without the current unsaved changes)
                self.save_all_and_close()
                return  # save_all_and_close() handles closing
            else:
                event.ignore()
                return
        else:
            # No unsaved changes, but still need to save any previous changes to file
            self.save_all_and_close()
            return  # save_all_and_close() handles closing
    def create_vendor_list_panel(self):

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        list_label = QLabel("Providers:")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(list_label)

        self.vendor_list = QListWidget()
        self.vendor_list.itemClicked.connect(self.on_vendor_selected)
        left_layout.addWidget(self.vendor_list)

        list_buttons = QHBoxLayout()
        list_buttons.addStretch()

        self.add_btn = QPushButton("Add Provider")
        self.remove_btn = QPushButton("Remove Provider")
        self.remove_btn.setEnabled(False)

        self.add_btn.clicked.connect(self.add_vendor)
        self.remove_btn.clicked.connect(self.remove_vendor)

        list_buttons.addWidget(self.add_btn)
        list_buttons.addSpacing(10)
        list_buttons.addWidget(self.remove_btn)
        list_buttons.addStretch()

        left_layout.addLayout(list_buttons)

        return left_panel

    def create_vendor_details_panel(self):
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        details_label = QLabel("Provider Details:")
        details_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addWidget(details_label)

        # Guidance message for the user
        self.guidance_label = QLabel("Select a provider from the list or use 'Add Provider' to begin editing.")
        self.guidance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guidance_label.setFont(QFont("Arial", 10, QFont.Weight.Bold)) # arial font does not matter as it is override  in main_window class
        right_layout.addWidget(self.guidance_label)

        # A widget to contain the form, which we can hide/show
        self.form_widget = QWidget()
        form_layout = QFormLayout(self.form_widget)

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

        form_layout.addRow("Name*:", self.name_edit)
        form_layout.addRow("Base URL*:", self.base_url_edit)
        form_layout.addRow("Customer ID*:", self.customer_id_edit)
        form_layout.addRow("Requestor ID:", self.requestor_id_edit)
        form_layout.addRow("API Key:", self.api_key_edit)
        form_layout.addRow("Platform:", self.platform_edit)
        form_layout.addRow("Version:", self.version_edit)
        form_layout.addRow("Delay (seconds):", self.delay_edit)
        form_layout.addRow("Retry:", self.retry_edit)

        for edit in [self.name_edit, self.base_url_edit, self.customer_id_edit,
                     self.requestor_id_edit, self.api_key_edit, self.platform_edit,
                     self.version_edit, self.delay_edit, self.retry_edit]:
            edit.textChanged.connect(self.on_field_changed)

        # Save changes button is now part of the form widget
        self.save_changes_btn = QPushButton("Save")
        # Set a fixed width and height for the button
        self.save_changes_btn.setFixedSize(100, 30)
        self.save_changes_btn.setEnabled(False)
        self.save_changes_btn.clicked.connect(self.save_current_vendor)

        # Center the Save button
        save_button_layout = QHBoxLayout()
        save_button_layout.addStretch()  # Left stretch
        self.save_changes_btn = QPushButton("Save")
        self.save_changes_btn.setFixedSize(100, 30)
        self.save_changes_btn.setEnabled(False)
        self.save_changes_btn.clicked.connect(self.save_current_vendor)
        save_button_layout.addWidget(self.save_changes_btn)
        save_button_layout.addStretch()  # Right stretch

        # Create a widget to hold the centered button
        save_button_widget = QWidget()
        save_button_widget.setLayout(save_button_layout)
        form_layout.addRow(save_button_widget)

        right_layout.addWidget(self.form_widget)
        right_layout.addStretch()

        return right_panel

    def toggle_details_panel(self, enabled):
        """Enables or disables the details form and shows/hides the guidance message."""
        self.form_widget.setVisible(enabled)
        self.guidance_label.setVisible(not enabled)

    def on_vendor_selected(self, item):
        self.toggle_details_panel(True)

        vendor_name = item.text()
        for vendor in self.vendors_data:
            if vendor.get('Name') == vendor_name:
                self.current_vendor = vendor
                self.populate_form(vendor)
                self.remove_btn.setEnabled(True)
                break

    def add_vendor(self):
        self.toggle_details_panel(True)

        new_vendor = {
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

        self.vendors_data.append(new_vendor)

        item = QListWidgetItem(new_vendor['Name'])
        self.vendor_list.addItem(item)
        self.vendor_list.setCurrentItem(item)

        self.current_vendor = new_vendor
        self.populate_form(new_vendor)
        self.remove_btn.setEnabled(True)

        self.name_edit.selectAll()
        self.name_edit.setFocus()


    def clear_form(self):

        for edit in [self.name_edit, self.base_url_edit, self.customer_id_edit,
                     self.requestor_id_edit, self.api_key_edit, self.platform_edit,
                     self.delay_edit, self.retry_edit]:
            edit.clear()
        self.version_edit.setText("5.1")
        self.save_changes_btn.setEnabled(False)

        # Re-hide the form and show the guidance message
        self.toggle_details_panel(False)

    def load_vendors(self):

        try:
            providers_file = self.config_data.get('providers_file', 'providers.tsv')
            search_paths = [
                Path.cwd() / providers_file,
                Path.cwd().parent / providers_file,
                Path(f"../{providers_file}")
            ]
            vendors_file_path = None
            for path in search_paths:
                if path.exists():
                    vendors_file_path = path
                    break
            if not vendors_file_path:
                QMessageBox.warning(self, "Warning", f"Could not find {providers_file}")
                return
            self.vendors_data.clear()
            self.vendor_list.clear()
            with open(vendors_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    if row.get('Name', '').strip():
                        self.vendors_data.append(dict(row))
                        item = QListWidgetItem(row['Name'])
                        self.vendor_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load vendors: {e}")

    def populate_form(self, vendor_data):

        """Fill form with vendor data"""
        self.name_edit.setText(vendor_data.get('Name', ''))
        self.base_url_edit.setText(vendor_data.get('Base_URL', ''))
        self.customer_id_edit.setText(vendor_data.get('Customer_ID', ''))
        self.requestor_id_edit.setText(vendor_data.get('Requestor_ID', ''))
        self.api_key_edit.setText(vendor_data.get('API_Key', ''))
        self.platform_edit.setText(vendor_data.get('Platform', ''))
        self.version_edit.setText(vendor_data.get('Version', '5.1'))
        self.delay_edit.setText(vendor_data.get('Delay', ''))
        self.retry_edit.setText(vendor_data.get('Retry', ''))

        self.save_changes_btn.setEnabled(False)

    def on_field_changed(self):
        """Enable save button when all required fields are filled."""
        name_filled = bool(self.name_edit.text().strip())
        base_url_filled = bool(self.base_url_edit.text().strip())
        customer_id_filled = bool(self.customer_id_edit.text().strip())

        # The save button is enabled only if all three required fields have content.
        is_ready_to_save = name_filled and base_url_filled and customer_id_filled

        # The button is also only enabled if a vendor is currently selected/being added.
        if self.current_vendor:
            self.save_changes_btn.setEnabled(is_ready_to_save)
        else:
            self.save_changes_btn.setEnabled(False)
    def save_current_vendor(self):
        if not self.current_vendor:
            return
        if not self.validate_current_vendor():
            return
        self.current_vendor['Name'] = self.name_edit.text().strip()
        self.current_vendor['Base_URL'] = self.base_url_edit.text().strip()
        self.current_vendor['Customer_ID'] = self.customer_id_edit.text().strip()
        self.current_vendor['Requestor_ID'] = self.requestor_id_edit.text().strip()
        self.current_vendor['API_Key'] = self.api_key_edit.text().strip()
        self.current_vendor['Platform'] = self.platform_edit.text().strip()
        self.current_vendor['Version'] = self.version_edit.text().strip()
        self.current_vendor['Delay'] = self.delay_edit.text().strip()
        self.current_vendor['Retry'] = self.retry_edit.text().strip()
        current_item = self.vendor_list.currentItem()
        if current_item:
            current_item.setText(self.current_vendor['Name'])
        self.save_changes_btn.setEnabled(False)
        QMessageBox.information(self, "Success", "Vendor updated successfully!")

    def remove_vendor(self):

        current_item = self.vendor_list.currentItem()

        if not current_item:
            return
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove '{current_item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            vendor_name = current_item.text()
            self.vendors_data = [v for v in self.vendors_data if v.get('Name') != vendor_name]
            row = self.vendor_list.row(current_item)
            self.vendor_list.takeItem(row)
            self.current_vendor = None
            self.clear_form()
            self.vendor_list.clearSelection()
            self.remove_btn.setEnabled(False)
            # Immediately persist to file
            self.save_all_and_close()





    def validate_current_vendor(self):

        name = self.name_edit.text().strip()
        base_url = self.base_url_edit.text().strip()
        customer_id = self.customer_id_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Provider name is required!")
            return False
        if not base_url:
            QMessageBox.warning(self, "Validation Error", "Base URL is required!")
            return False
        if not customer_id:
            QMessageBox.warning(self, "Validation Error", "Customer ID is required!")
            return False
        for vendor in self.vendors_data:
            if (vendor != self.current_vendor and
                    vendor.get('Name', '').lower() == name.lower()):
                QMessageBox.warning(self, "Validation Error", "Provider name already exists!")
                return False
        return True

    def show_provider_help(self):

        help_url = "https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester/blob/main/docs/Running%20the%20Harvester.md"
        reply = QMessageBox.question(
            self,

            "Provider Management Help",
            "<b>Provider Help</b><br><br>"
            "This will open your web browser.<br>"
            "Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

       # dlg.setIcon(QMessageBox.Icon.Question)
       # button = dlg.exec()
        if reply == QMessageBox.StandardButton.Yes:
            try:
                webbrowser.open(help_url)
            except Exception as e:
                QMessageBox.information(
                    self, "Help Documentation",
                    f"Please visit the provider management guide at:\n{help_url}\n\n"
                    f"(Could not open browser automatically: {e})"
                )

    def save_all_and_close(self):
        try:
            providers_file = self.config_data.get('providers_file', 'providers.tsv')
            search_paths = [
                Path.cwd() / providers_file,
                Path.cwd().parent / providers_file,
                Path(f"../{providers_file}")
            ]
            vendors_file_path = None
            for path in search_paths:
                if path.exists():
                    vendors_file_path = path
                    break
            if not vendors_file_path:
                vendors_file_path = Path.cwd().parent / providers_file
            fieldnames = ['Name', 'Base_URL', 'Customer_ID', 'Requestor_ID',
                          'API_Key', 'Platform', 'Version', 'Delay', 'Retry']
            with open(vendors_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                for vendor in self.vendors_data:
                    row = {}
                    for field in fieldnames:
                        row[field] = vendor.get(field, '')
                    writer.writerow(row)
            self.accept()
            #QMessageBox.information(self, "Success", f"Providers saved o {vendors_file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save providers: {e}")