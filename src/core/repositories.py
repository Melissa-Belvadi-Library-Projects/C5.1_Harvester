"""Data persistence layer for the application."""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class ConfigRepository:
    """Handles configuration file persistence."""

    def __init__(self, config_file: Optional[Path] = None):
        """Initialize with optional config file path."""
        self.config_file = config_file or self._find_config_file()

    def _find_config_file(self) -> Path:
        """Locate the configuration file."""
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
                with open(self.config_file, 'r') as f:
                    content = f.read()

                # Parse Python config file
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

                        config[key] = value
        except Exception as e:
            print(f"Error loading config: {e}")

        return config

    def save(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            content = """#####  Various constant values that you can change as you like

sqlite_filename = '{sqlite_filename}'
data_table = '{data_table}'
error_log_file = '{error_log_file}'
json_dir = '{json_dir}'
tsv_dir = '{tsv_dir}'
providers_file = '{providers_file}'
save_empty_report = {save_empty_report}
always_include_header_metric_types = {always_include_header_metric_types}
default_begin = '{default_begin}'
""".format(**config)

            with open(self.config_file, 'w') as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'sqlite_filename': 'counterdata.db',
            'data_table': 'usage_data',
            'error_log_file': 'errorlog.txt',
            'json_dir': 'json_folder',
            'tsv_dir': 'tsv_folder',
            'providers_file': 'providers.tsv',
            'save_empty_report': False,
            'always_include_header_metric_types': True,
            'default_begin': '2025-01'
        }


class VendorRepository:
    """Handles vendor data persistence."""

    def __init__(self, providers_file: str = 'providers.tsv'):
        """Initialize with providers file name."""
        self.providers_file = providers_file
        self._file_path: Optional[Path] = None

    from typing import Optional
    from pathlib import Path
 #made the find file more extensive in case users place file in a different folder. it should still be able to find it
    def _find_file(self) -> Optional[Path]:
        """Locate the providers file."""


        # Most common, direct paths (CWD and parent)
        search_paths = [
            Path.cwd() / self.providers_file,  # Directly in the CWD
            Path.cwd().parent / self.providers_file,  # Directly in the parent directory
        ]

        # folders to search inside
        directories_to_check = [
            Path.cwd(),
            Path.cwd().parent
        ]

        # 3. Dynamically find all subdirectories within the main working areas
        for base_dir in directories_to_check:
            # The glob '**/' finds all subdirectories (recursively) from the base_dir.
            # '*' ensures we only get *direct* subfolders if we only want one level deep.
            for folder in base_dir.iterdir():
                if folder.is_dir():
                    # Check for the file inside each subdirectory
                    subfolder_path = folder / self.providers_file
                    search_paths.append(subfolder_path)

        # Remove duplicates if any (though unlikely with this structure)
        search_paths = list(set(search_paths))

        # Starts search
        for path in search_paths:
            if path.exists():
                self._file_path = path
                print(f"DEBUG: Found providers file at: {path}")
                return path

        # Default location if not found
        self._file_path = Path.cwd() / self.providers_file
        print(f"DEBUG: File not found, using default: {self._file_path}")
        return self._file_path

    def load(self) -> List[Dict[str, str]]:
        """Load vendors from TSV file."""
        print(f"DEBUG: VendorRepository.load() called with providers_file: {self.providers_file}")

        vendors = []
        file_path = self._find_file()

        print(f"DEBUG: Attempting to load from: {file_path}")

        if file_path and file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter='\t')
                    for row in reader:
                        if row.get('Name', '').strip():
                            vendors.append(dict(row))
                print(f"DEBUG: Successfully loaded {len(vendors)} vendors from {file_path}")
            except Exception as e:
                print(f"Error loading vendors: {e}")
        else:
            print(f"DEBUG: File {file_path} does not exist!")

        return vendors


    def save(self, vendors: List[Dict[str, str]]) -> bool:
        """Save vendors to TSV file."""
        file_path = self._find_file()

        if not file_path:
            return False

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            fieldnames = ['Name', 'Base_URL', 'Customer_ID', 'Requestor_ID',
                          'API_Key', 'Platform', 'Version', 'Delay', 'Retry']

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()

                for vendor in vendors:
                    row = {field: vendor.get(field, '') for field in fieldnames}
                    writer.writerow(row)

            return True
        except Exception as e:
            print(f"Error saving vendors: {e}")
            return False