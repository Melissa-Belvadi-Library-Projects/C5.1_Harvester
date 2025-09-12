"""
Integration layer between GUI and existing COUNTER harvester backend.
This module bridges the GUI state management with the existing CLI functionality.
"""

import sys
import os
import sqlite3
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import existing backend modules
from logger import log_error, clear_log_error
from create_tables import create_data_table
from load_providers import load_providers
from fetch_json import fetch_json, validate_date
from process_item_details import process_item_details
from current_config import sqlite_filename, providers_file, error_log_file


@dataclass
class HarvesterRequest:
    """Configuration for a harvester run."""
    begin_date: str  # YYYY-MM format
    end_date: str  # YYYY-MM format
    selected_vendors: List[str]  # List of vendor names
    selected_reports: List[str]  # List of report types (e.g., ['TR', 'DR'])
    single_report_type: Optional[str] = None  # If user wants only one specific report
    save_empty_reports: bool = True
    create_database: bool = True
    output_json: bool = True
    output_tsv: bool = True


class HarvesterIntegration:
    """
    Integration layer that adapts the existing CLI harvester for GUI use.
    Maintains compatibility with original backend while providing progress callbacks.
    """

    def __init__(self, progress_callback: Optional[Callable[[str], None]] = None,
                 status_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the harvester integration.

        Args:
            progress_callback: Function to call with progress messages
            status_callback: Function to call with status updates
        """
        self.progress_callback = progress_callback or print
        self.status_callback = status_callback or (lambda x: None)
        self.is_cancelled = False
        self.providers_data = []
        self.providers_dict = {}

    def run(self, request: HarvesterRequest) -> Dict[str, Any]:
        """
        Execute the harvesting process using the existing backend.

        Args:
            request: HarvesterRequest with all configuration

        Returns:
            Dictionary with results and statistics
        """
        self.is_cancelled = False
        results = {
            'success': False,
            'providers_processed': 0,
            'reports_fetched': 0,
            'reports_failed': 0,
            'json_files': [],
            'tsv_files': [],
            'errors': []
        }

        try:
            # Clear error log
            clear_log_error()

            # Log start
            current_time = datetime.now()
            self._log(f"Start of harvester run: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            log_error(f'INFO: GUI-initiated harvester run: {current_time}')

            # Validate dates
            if not validate_date(request.begin_date):
                raise ValueError(f"Invalid begin date format: {request.begin_date}")
            if not validate_date(request.end_date):
                raise ValueError(f"Invalid end date format: {request.end_date}")

            # Load providers
            self._log("Loading providers from TSV file...")
            self.providers_data = self._load_filtered_providers(request.selected_vendors)

            if not self.providers_data:
                raise ValueError("No valid providers found matching selection")

            self._log(f"Loaded {len(self.providers_data)} providers")

            # Fetch provider API info (this gets the supported reports list)
            self._log("Fetching provider API information...")
            self.providers_dict = self._fetch_provider_info(
                self.providers_data,
                request.begin_date,
                request.end_date,
                request.single_report_type
            )

            if not self.providers_dict:
                raise ValueError("Failed to get provider information from API")

            # Filter reports based on selection
            if request.selected_reports:
                self._filter_reports(self.providers_dict, request.selected_reports)

            # Process each provider and report
            if request.create_database:
                self._initialize_database()

            # Process reports
            results.update(self._process_reports(self.providers_dict, request))

            results['success'] = True
            results['providers_processed'] = len(self.providers_dict)

            self._log(f"\nHarvest complete: {results['reports_fetched']} reports fetched, "
                      f"{results['reports_failed']} failed")

        except Exception as e:
            error_msg = f"Harvester error: {str(e)}"
            self._log(f"ERROR: {error_msg}")
            log_error(f"ERROR: {error_msg}\n{traceback.format_exc()}")
            results['errors'].append(error_msg)
            results['success'] = False

        return results

    def cancel(self):
        """Cancel the running harvest."""
        self.is_cancelled = True
        self._log("Cancellation requested...")

    def _load_filtered_providers(self, selected_vendors: List[str]) -> List[Dict]:
        """Load providers and filter by selection."""
        all_providers = load_providers(providers_file)

        if not selected_vendors:
            return all_providers

        # Filter to only selected vendors
        filtered = [p for p in all_providers if p.get('Name') in selected_vendors]
        return filtered

    def _fetch_provider_info(self, providers: List[Dict],
                             begin_date: str, end_date: str,
                             single_report: Optional[str] = None) -> Dict:
        """
        Adapt the existing fetch_json function to work with GUI parameters.
        This mimics the interactive prompts with provided values.
        """
        # Monkey-patch the get_dates and get_report_type functions
        import fetch_json

        original_get_dates = fetch_json.get_dates
        original_get_report = fetch_json.get_report_type

        def mock_get_dates():
            self._log(f"Date range: {begin_date} to {end_date}")
            return begin_date, end_date

        def mock_get_report():
            if single_report:
                self._log(f"Fetching report type: {single_report}")
                return single_report
            else:
                self._log("Fetching all supported report types")
                return None

        try:
            fetch_json.get_dates = mock_get_dates
            fetch_json.get_report_type = mock_get_report

            # Call the original fetch_json
            providers_dict = fetch_json.fetch_json(providers)

        finally:
            # Restore original functions
            fetch_json.get_dates = original_get_dates
            fetch_json.get_report_type = original_get_report

        return providers_dict

    def _filter_reports(self, providers_dict: Dict, selected_reports: List[str]):
        """Filter provider reports to only selected types."""
        for provider_name, provider_info in providers_dict.items():
            if 'Report_URLS' in provider_info:
                filtered_urls = {}
                for report_id, url in provider_info['Report_URLS'].items():
                    # Check if base report type matches selection
                    base_type = report_id.replace('_EX', '')
                    if base_type in selected_reports:
                        filtered_urls[report_id] = url

                provider_info['Report_URLS'] = filtered_urls

    def _initialize_database(self):
        """Initialize SQLite database."""
        self._log("Initializing database...")
        conn = sqlite3.connect(sqlite_filename)
        cursor = conn.cursor()
        create_data_table(cursor)
        conn.commit()
        conn.close()

    def _process_reports(self, providers_dict: Dict, request: HarvesterRequest) -> Dict:
        """Process all reports for all providers."""
        results = {
            'reports_fetched': 0,
            'reports_failed': 0,
            'json_files': [],
            'tsv_files': []
        }

        total_reports = sum(len(p.get('Report_URLS', {}))
                            for p in providers_dict.values())
        current_report = 0

        for provider_name, provider_info in providers_dict.items():
            if self.is_cancelled:
                self._log("Processing cancelled by user")
                break

            self._status(f"Processing {provider_name}")

            for report_id, report_url in provider_info.get('Report_URLS', {}).items():
                if self.is_cancelled:
                    break

                current_report += 1
                progress_pct = (current_report / total_reports * 100) if total_reports > 0 else 0

                self._log(f"[{progress_pct:.0f}%] Fetching {provider_name}: {report_id}")
                log_error(f"INFO: Retrieving {provider_name}: {report_id}: {report_url}")

                try:
                    # Call the existing process_item_details function
                    result = process_item_details(provider_info, report_id, report_url)

                    if result and result != -1:
                        results['reports_fetched'] += 1

                        # Track output files (these are created by process_item_details)
                        # The function saves files to json_dir and tsv_dir
                        from current_config import json_dir, tsv_dir

                        vendor_name = provider_name.replace(' ', '_')

                        # Look for created files
                        json_path = Path(json_dir) / vendor_name
                        tsv_path = Path(tsv_dir) / vendor_name

                        if json_path.exists():
                            for f in json_path.glob(f"*{report_id}*.json"):
                                results['json_files'].append(str(f))

                        if tsv_path.exists():
                            for f in tsv_path.glob(f"*{report_id}*.tsv"):
                                results['tsv_files'].append(str(f))
                    else:
                        results['reports_failed'] += 1
                        self._log(f"  Failed to process {report_id}")

                except Exception as e:
                    results['reports_failed'] += 1
                    error_msg = f"Error processing {provider_name}:{report_id}: {str(e)}"
                    self._log(f"  ERROR: {error_msg}")
                    log_error(f"ERROR: {error_msg}")

        return results

    def _log(self, message: str):
        """Send log message to callback."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.progress_callback(f"[{timestamp}] {message}")

    def _status(self, message: str):
        """Send status update to callback."""
        self.status_callback(message)


# Adapter for GUI's HarvesterConfig to work with the integration
def adapt_gui_config(config) -> HarvesterRequest:
    """
    Adapt the GUI's HarvesterConfig to HarvesterRequest.

    Args:
        config: HarvesterConfig from GUI

    Returns:
        HarvesterRequest for the integration layer
    """
    # Handle report type conversion
    single_report = None
    selected_reports = config.reports

    # If only one report selected, check if it should be treated as single
    if len(selected_reports) == 1:
        report = selected_reports[0]
        # Standard views (with numbers) are treated as single report
        if len(report) > 2 and report[-1].isdigit():
            single_report = report
            selected_reports = []

    return HarvesterRequest(
        begin_date=config.start_date,
        end_date=config.end_date,
        selected_vendors=config.vendors,
        selected_reports=selected_reports,
        single_report_type=single_report,
        save_empty_reports=config.config.get('save_empty_report', False),
        create_database=True,
        output_json=True,
        output_tsv=True
    )