import csv
import webbrowser
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QWidget, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


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

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Vendor list
        left_panel = self.create_vendor_list_panel()

        # Right panel - Vendor details
        right_panel = self.create_vendor_details_panel()

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600])

        main_layout.addWidget(splitter)

        # Dialog buttons - now with Help and Close
        button_layout = QHBoxLayout()

        # Help button on the left
        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self.show_provider_help)
        button_layout.addWidget(help_btn)

        button_layout.addStretch()

        # Close button on the right
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

    def create_vendor_list_panel(self):
        """Create the left panel with vendor list"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        list_label = QLabel("Providers:")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(list_label)

        self.vendor_list = QListWidget()
        self.vendor_list.itemClicked.connect(self.on_vendor_selected)
        left_layout.addWidget(self.vendor_list)

        # Buttons for list management - centered
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
        """Create the right panel with vendor details form"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        details_label = QLabel("Provider Details:")
        details_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addWidget(details_label)

        # Form for vendor details
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.base_url_edit = QLineEdit()
        self.customer_id_edit = QLineEdit()
        self.requestor_id_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.platform_edit = QLineEdit()
        self.version_edit = QLineEdit()
        self.version_edit.setText("5.1")  # Default value
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

        # Connect text changes to update function
        for edit in [self.name_edit, self.base_url_edit, self.customer_id_edit,
                     self.requestor_id_edit, self.api_key_edit, self.platform_edit,
                     self.version_edit, self.delay_edit, self.retry_edit]:
            edit.textChanged.connect(self.on_field_changed)

        right_layout.addLayout(form_layout)

        # Save changes button
        self.save_changes_btn = QPushButton("Save")
        self.save_changes_btn.setEnabled(False)
        self.save_changes_btn.clicked.connect(self.save_current_vendor)
        right_layout.addWidget(self.save_changes_btn)
        right_layout.addWidget(self.save_changes_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        right_layout.addStretch()

        return right_panel



    def load_vendors(self):
        """Load vendors from the TSV file"""
        try:
            providers_file = self.config_data.get('providers_file', 'providers.tsv')

            # Try multiple locations
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

    def on_vendor_selected(self, item):
        """Handle vendor selection from list"""
        vendor_name = item.text()

        # Find vendor data
        for vendor in self.vendors_data:
            if vendor.get('Name') == vendor_name:
                self.current_vendor = vendor
                self.populate_form(vendor)
                self.remove_btn.setEnabled(True)
                break

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
        """Enable save button when fields change"""
        if self.current_vendor:
            self.save_changes_btn.setEnabled(True)

    def save_current_vendor(self):
        """Save changes to current vendor"""
        if not self.current_vendor:
            return

        if not self.validate_current_vendor():
            return

        # Update vendor data
        self.current_vendor['Name'] = self.name_edit.text().strip()
        self.current_vendor['Base_URL'] = self.base_url_edit.text().strip()
        self.current_vendor['Customer_ID'] = self.customer_id_edit.text().strip()
        self.current_vendor['Requestor_ID'] = self.requestor_id_edit.text().strip()
        self.current_vendor['API_Key'] = self.api_key_edit.text().strip()
        self.current_vendor['Platform'] = self.platform_edit.text().strip()
        self.current_vendor['Version'] = self.version_edit.text().strip()
        self.current_vendor['Delay'] = self.delay_edit.text().strip()
        self.current_vendor['Retry'] = self.retry_edit.text().strip()

        # Update list display
        current_item = self.vendor_list.currentItem()
        if current_item:
            current_item.setText(self.current_vendor['Name'])

        self.save_changes_btn.setEnabled(False)
        QMessageBox.information(self, "Success", "Vendor updated successfully!")

    def add_vendor(self):
        """Add new vendor"""
        new_vendor = {
            'Name': 'New Provider',
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

        # Focus on name field
        self.name_edit.selectAll()
        self.name_edit.setFocus()

    def remove_vendor(self):
        """Remove selected vendor"""
        current_item = self.vendor_list.currentItem()
        if not current_item:
            return

        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove '{current_item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from data
            vendor_name = current_item.text()
            self.vendors_data = [v for v in self.vendors_data if v.get('Name') != vendor_name]

            # Remove from list
            row = self.vendor_list.row(current_item)
            self.vendor_list.takeItem(row)

            # Clear form
            self.current_vendor = None
            self.clear_form()
            self.remove_btn.setEnabled(False)

    def clear_form(self):
        """Clear all form fields"""
        for edit in [self.name_edit, self.base_url_edit, self.customer_id_edit,
                     self.requestor_id_edit, self.api_key_edit, self.platform_edit,
                     self.delay_edit, self.retry_edit]:
            edit.clear()
        self.version_edit.setText("5.1")
        self.save_changes_btn.setEnabled(False)

    def validate_current_vendor(self):
        """Validate current vendor data"""
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

        # Check for duplicate names
        for vendor in self.vendors_data:
            if (vendor != self.current_vendor and
                    vendor.get('Name', '').lower() == name.lower()):
                QMessageBox.warning(self, "Validation Error", "Provider name already exists!")
                return False

        return True

    def show_provider_help(self):
        """Show help for managing providers"""
        import webbrowser

        help_url = "https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester/blob/main/docs/Running%20the%20Harvester.md"

        reply = QMessageBox.question(
            self, "Provider Management Help",
            "Open provider management documentation?\n\n"
            "This will explain:\n"
            "• How to add new providers\n"
            "• Required fields and credentials\n"
            "• Provider-specific settings\n"
            "Open in browser?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

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
        """Save all vendors to TSV file and close dialog"""
        try:
            providers_file = self.config_data.get('providers_file', 'providers.tsv')

            # Try to find the file in the same locations as load
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

            # Define field order
            fieldnames = ['Name', 'Base_URL', 'Customer_ID', 'Requestor_ID',
                          'API_Key', 'Platform', 'Version', 'Delay', 'Retry']

            with open(vendors_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()

                for vendor in self.vendors_data:
                    # Ensure all fields exist
                    row = {}
                    for field in fieldnames:
                        row[field] = vendor.get(field, '')
                    writer.writerow(row)

            QMessageBox.information(self, "Success", f"Providers saved to {vendors_file_path}")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save providers: {e}")

