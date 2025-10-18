import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from typing import Optional
from pathlib import Path

"""The repositories as a way to get the data without affecting the ui , 
    its is essentally a middelman where it saves,laods the config data and vendors data and is passed


    """


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

    def __init__(self, providers_file: str = 'providers.tsv'):
        """Initialize with providers file name."""
        self.providers_file = providers_file
        self._file_path: Optional[Path] = None


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

        #  Dynamically find all subdirectories within the main working areas
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
                return path

        # Default location if not found
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
            except Exception as e:
                print(f"Error loading vendors: {e}")
        else:
            print(f"DEBUG: File {file_path} does not exist!")

        return vendors

    # load using the load provider logic
    # def load(self) -> List[Dict[str, str]]:
    #     """Load vendors from TSV file with robust error handling."""
    #     vendors = []
    #     file_path = self._find_file()
    #
    #     # Check if file exists
    #     if not file_path:
    #         print("ERROR: Could not determine providers file location")
    #         return []
    #
    #     if not file_path.exists():
    #         print(f"ERROR: Providers file not found: {file_path}")
    #         return []
    #
    #     try:
    #         with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
    #             # Sniff delimiter to ensure it's tab-delimited
    #             try:
    #                 sample = f.read(2048)
    #                 if not sample.strip():
    #                     print("ERROR: Providers file is empty")
    #                     return []
    #
    #                 dialect = csv.Sniffer().sniff(sample, delimiters='\t,;')
    #                 f.seek(0)  # Rewind after sniffing
    #
    #                 if dialect.delimiter != '\t':
    #                     print(
    #                         f"ERROR: Providers file must be tab-delimited (TSV), but found '{dialect.delimiter}' delimiter")
    #                     return []
    #
    #             except csv.Error as e:
    #                 print(f"ERROR: Cannot determine file format: {e}")
    #                 return []
    #
    #             # Read with DictReader
    #             reader = csv.DictReader(f, delimiter='\t')
    #
    #             # Validate headers exist
    #             if not reader.fieldnames:
    #                 print("ERROR: No headers found in providers file")
    #                 return []
    #
    #             # Validate required headers
    #             required = ['Name', 'Base_URL', 'Customer_ID', 'Version']
    #             missing = [h for h in required if h not in reader.fieldnames]
    #             if missing:
    #                 print(f"ERROR: Providers file missing required columns: {', '.join(missing)}")
    #                 print(f"       Found headers: {reader.fieldnames}")
    #                 return []
    #
    #             # Read rows
    #             row_count = 0
    #             for row_num, row in enumerate(reader, start=2):
    #                 # Skip completely empty rows
    #                 if not any(row.values()):
    #                     continue
    #
    #                 # Skip rows with no name
    #                 name = row.get('Name', '').strip()
    #                 if not name:
    #                     continue
    #
    #                 # Warn about non-5.1 versions (but still include)
    #                 version = row.get('Version', '').strip()
    #                 if version and version != '5.1':
    #                     print(f"WARNING: {name} has Version '{version}', expected '5.1'")
    #
    #                 vendors.append(dict(row))
    #                 row_count += 1
    #
    #             print(f"INFO: Loaded {row_count} providers from {file_path.name}")
    #
    #             if row_count == 0:
    #                 print("WARNING: No valid providers found in file")
    #                 return []
    #
    #             # Sort alphabetically (case-insensitive)
    #             vendors.sort(key=lambda v: v.get('Name', '').lower())
    #
    #     except UnicodeDecodeError as e:
    #         print(f"ERROR: File encoding issue - file might not be UTF-8 text")
    #         print(f"       It could be a binary Excel file (.xlsx)")
    #         return []
    #
    #     except FileNotFoundError:
    #         print(f"ERROR: File not found: {file_path}")
    #         return []
    #
    #     except PermissionError:
    #         print(f"ERROR: Permission denied reading: {file_path}")
    #         return []
    #
    #     except Exception as e:
    #         print(f"ERROR: Unexpected error loading providers: {e}")
    #         return []
    #
    #     return vendors

    def save(self, vendors: List[Dict[str, str]]):

        """Save vendors to TSV file."""

        file_path = self._find_file()

        if not file_path:
            return False

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            sorted_vendors = sorted(vendors, key=VendorRepository.get_vendor_name)

            fieldnames = ['Name', 'Base_URL', 'Customer_ID', 'Requestor_ID',
                          'API_Key', 'Platform', 'Version', 'Delay', 'Retry']

            #  Open file for writing
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()  # Writes header row
                # Write each vendor
                for vendor in sorted_vendors:
                    row = {field: vendor.get(field, '') for field in fieldnames}
                    writer.writerow(row)

            return True
        except Exception as e:
            print(f"Error saving vendors: {e}")
            return False