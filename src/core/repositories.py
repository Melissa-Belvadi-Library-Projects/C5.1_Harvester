"""
Repositories Module
This module provides repository classes that handle loading and saving
application data without directly touching the UI.

- ConfigRepository: Manages the current_config.py settings file
- VendorRepository: Manages the providers.tsv vendor database

These act as a middleman between file storage and the rest of the application.
"""

import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
from .state import AppSignals


class ConfigRepository:
    """Handles configuration file persistence."""
    def __init__(self, config_file: Optional[Path] = None, signals: Optional[AppSignals] = None):
        """Initialize with optional config file path."""
        self.config_file = config_file or self._find_config_file()
        self.signals = signals

    def _find_config_file(self) -> Path:
        """Locate the configuration file."""

        #searches multiple places in case user moves file aound..
        #highly unlikely but ensures that it always find the file .

        current_dir = Path(__file__).parent

        candidates = [
            current_dir.parent / "current_config.py",
            Path.cwd() / "current_config.py",
            Path.cwd().parent / "current_config.py",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        # Default location if not found
        return current_dir.parent / "current_config.py"

    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        config = self._get_defaults()
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for line in content.split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip("'\"")

                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False

                        config[key] = value
        except Exception as e:
            if self.signals:
                # The  if self.signals: check is basically saying:
                # Before I  try to use signals, let me make sure they actually exist..
                # If they don't, I'll just skip this part instead of crashing... seems highly unlikely but convering any edge cases
                self.signals.errorOccurred.emit(
                    f"Could not load configuration: {e}\n\n"
                    "Please make sure the file exists and is in the right folder"
                    "Ensure 'current_config.py' exists in the folder"
                )
        return config

    def save(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            content = """#####  Various constant values that you can change as you like

sqlite_filename = '{sqlite_filename}'
error_log_file = '{error_log_file}'
json_dir = '{json_dir}'
tsv_dir = '{tsv_dir}'
providers_file = '{providers_file}'
save_empty_report = {save_empty_report}
always_include_header_metric_types = {always_include_header_metric_types}
default_begin = '{default_begin}'
""".format(**config)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return True
        except PermissionError:
            if self.signals:
                self.signals.errorOccurred.emit(
                    "Permission denied while saving configuration.\n\n"
                    "Save to a folder where you have write access, "
                    "such as Documents or Desktop."
            )
            return False
        except Exception as e:
            if self.signals:
                self.signals.errorOccurred.emit(
                    f"Could not save configuration: {e}\n\n"
                    "Check disk space and verify you have permission to write "
                    "to this location."
            )
            return False

    def _get_defaults(self) -> Dict[str, Any]:
        """
        Get default configuration values from default_config.py.

        Falls back to hardcoded values if default_config.py is not found.
        This ensures the app works even if the file is missing.
        """
        # Try to load defaults from default_config.py
        try:
            # Search for default_config.py
            current_dir = Path(__file__).parent
            candidates = [
                current_dir.parent / "default_config.py",
                Path.cwd() / "default_config.py",
                Path.cwd().parent / "default_config.py",
            ]

            default_config_path = None
            for candidate in candidates:
                if candidate.exists():
                    default_config_path = candidate
                    break

            if default_config_path:
                # Read the default config file
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse it (same logic as load())
                defaults = {}
                for line in content.split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip("'\"")

                        # Convert string booleans
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False

                        defaults[key] = value

                return defaults

        except Exception as e:
            # If reading fails, fall back to hardcoded defaults
            if self.signals:
                self.signals.errorOccurred.emit(
                    f"Could not read default_config.py: {e}\n\n"
                    "Using built-in defaults instead."
                )

        # Fallback: hardcoded defaults (last resort)
        return {
            'sqlite_filename': 'counterdata.db',
            'error_log_file': 'infolog.txt',
            'json_dir': 'json_folder',
            'tsv_dir': 'tsv_folder',
            'providers_file': 'providers.tsv',
            'save_empty_report': False,
            'always_include_header_metric_types': True,
            'default_begin': '2025-01'
        }


class VendorRepository:
    """Handles vendor data persistence."""

    @staticmethod
    def get_vendor_name(vendor):
        """Get vendor name for alphabetical sorting."""
        return vendor.get('Name', '').lower()

    def __init__(self, providers_file: str = 'providers.tsv', signals: Optional[AppSignals] = None):
        """Initialize with providers file name."""
        self.providers_file = providers_file
        self._file_path: Optional[Path] = None
        self.signals = signals

    def _find_file(self) -> Optional[Path]:
        """
        Recursively search for the providers TSV file.
        """
        search_paths = [
            Path.cwd() / self.providers_file, #search 1
            Path.cwd().parent / self.providers_file, # search 2
        ]

        directories_to_check = [Path.cwd(), Path.cwd().parent]

        for base_dir in directories_to_check:
            for folder in base_dir.iterdir():
                if folder.is_dir():
                    subfolder_path = folder / self.providers_file
                    search_paths.append(subfolder_path)

        search_paths = list(set(search_paths))

        for path in search_paths:
            if path.exists():
                self._file_path = path
                return path

        self._file_path = Path.cwd() / self.providers_file
        return self._file_path

    def load(self) -> List[Dict[str, str]]:

        """Load vendors from TSV file."""
        vendors = []
        file_path = self._find_file()

        if file_path and file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f, delimiter='\t')
                    for row in reader:
                        if row.get('Name', '').strip():
                            vendors.append(dict(row))
                vendors.sort(key=VendorRepository.get_vendor_name)
            except UnicodeDecodeError:
                if self.signals:
                    self.signals.errorOccurred.emit(
                        "Providers file could not be read — it may be an Excel file instead of a TSV.\n\n"
                        "Open the file in Excel and re-save it as 'providers.tsv' "
                        "using 'Text (Tab Delimited)' format."
                )
            except Exception as e:
                if self.signals:
                    self.signals.errorOccurred.emit(
                        f"Unexpected error loading vendors: {e}\n\n"
                        "Ensure the providers file is properly formatted as TSV."
                    )
        else:
            self.signals.errorOccurred.emit(
                 f"Providers file not found at {file_path}\n\n"
                 "Ensure the file exists and is in the application folder "
            )
        return vendors

    def save(self, vendors: List[Dict[str, str]]) -> bool:
        """Save vendors to TSV file."""
        file_path = self._find_file()
        if not file_path:
            if self.signals:
                self.signals.errorOccurred.emit(
                    "Could not determine location to save providers file.\n\n"
                    "Check application settings for providers file path."
                )
            return False

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            sorted_vendors = sorted(vendors, key=VendorRepository.get_vendor_name)
            fieldnames = ['Name', 'Base_URL', 'Customer_ID', 'Requestor_ID',
                          'API_Key', 'Platform', 'Version', 'Delay', 'Retry']

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                for vendor in sorted_vendors:
                    row = {field: vendor.get(field, '') for field in fieldnames}
                    writer.writerow(row)

            return True
        except PermissionError:
            if self.signals:
                self.signals.errorOccurred.emit(
                    f"Permission denied writing to {file_path}\n\n"
                    "Save the file in a folder where you have write access, "
                    "like Documents or Desktop."
            )
            return False
        except Exception as e:
            if self.signals:
                self.signals.errorOccurred.emit(
                    f"Could not save vendors: {e}\n\n"
                    "Verify you have permission to write to this location."
                )
            return False