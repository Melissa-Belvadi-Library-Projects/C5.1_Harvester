import os
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox


class ConfigManager:
    """
    Handles loading and saving of harvester configuration settings.
    Manages the current_config.py file that contains backend configuration parameters.
    Provides  file location detection and robust error handling.
    """

    def __init__(self):
        """
        Constructor for ConfigManager.
        Automatically locates the current_config.py file on initialization.
        """
        # Find and store the path to current_config.py using  search
        self.config_file = self._find_config_file()

    def _find_config_file(self):
        """
        Intelligently searches for current_config.py in multiple expected locations.
        Handles different deployment scenarios and directory structures.

        Returns:
            Path: Path object pointing to current_config.py file
        """
        # Get the directory containing this config_manager.py file
        current_dir = Path(__file__).parent

        # Define candidate locations in order of preference
        candidates = [
            current_dir.parent.parent / "current_config.py",  # src/current_config.py
            current_dir.parent.parent.parent / "current_config.py",  # parent of src/
            Path.cwd() / "current_config.py",  # current working directory
            Path.cwd().parent / "current_config.py",  # parent of working directory
        ]

        # Search through candidates and return first existing file
        for candidate in candidates:
            if candidate.exists():
                return candidate

        # If no existing file found, return default location for creation
        return current_dir.parent.parent / "current_config.py"

    def load_config(self):
        """
        Loads configuration settings from current_config.py file.
        Provides sensible defaults if file doesn't exist or has missing values.
        Parses Python variable assignments into a dictionary.

        Returns:
            dict: Configuration dictionary with all required settings
        """
        # Define default configuration values
        config = {
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

        try:
            # Check if configuration file exists
            if self.config_file.exists():
                # Read entire file content
                with open(self.config_file, 'r') as f:
                    content = f.read()

                # Parse file line by line
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()  # Remove leading/trailing whitespace

                    # Skip empty lines and comments (lines starting with #)
                    if '=' in line and not line.startswith('#'):
                        # Split on first equals sign to handle values containing '='
                        key, value = line.split('=', 1)

                        # Clean up key and value
                        key = key.strip()
                        value = value.strip().strip("'\"")  # Remove quotes around strings

                        # Convert string booleans to actual boolean values
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False

                        # Store in configuration dictionary
                        config[key] = value

        except Exception as e:
            # Print warning but continue with defaults if file reading fails
            print(f"Warning: Could not load current_config.py from {self.config_file}: {e}")

        return config

    def save_config(self, config_data):
        """
        Saves configuration dictionary back to current_config.py file.
        Creates the file in Python format with proper variable assignments.

        Args:
            config_data (dict): Configuration dictionary to save

        Returns:
            bool: True if save successful

        Raises:
            Exception: If file writing fails
        """
        try:
            # Ensure the parent directory exists (create if necessary)
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Build the Python configuration file content
            config_content = f"""#####  Various constant values that you can change as you like

sqlite_filename = '{config_data['sqlite_filename']}'
data_table = '{config_data['data_table']}'
error_log_file = '{config_data['error_log_file']}'
json_dir = '{config_data['json_dir']}'
tsv_dir = '{config_data['tsv_dir']}'
providers_file = '{config_data['providers_file']}'
save_empty_report = {config_data['save_empty_report']}
always_include_header_metric_types = {config_data['always_include_header_metric_types']}
default_begin = '{config_data['default_begin']}'
"""
            # Write configuration content to file
            with open(self.config_file, 'w') as f:
                f.write(config_content)

            # Log successful save
            print(f"Config saved to: {self.config_file}")
            return True

        except Exception as e:
            # Log error and re-raise for calling code to handle
            print(f"Error saving config to {self.config_file}: {e}")
            raise