import sqlite3
import traceback
from datetime import datetime
from pathlib import Path
from logger import log_error, set_progress_callback
from create_tables import create_data_table
from load_providers import load_providers
from fetch_json import fetch_json
from process_item_details import process_item_details

# Import VendorRepository to find the providers file the same way GUI does
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
from core.repositories import VendorRepository, ConfigRepository

from logger import set_error_log_file


def run_harvester(begin_date, end_date, selected_vendors, selected_reports, config_dict,
                  progress_callback=None, is_cancelled_callback=None):
    """
    Run the COUNTER harvester with given parameters.

    Args:
        begin_date: Start date in YYYY-MM format
        end_date: End date in YYYY-MM format
        selected_vendors: List of vendor names to process (empty list = all vendors)
        selected_reports: List of report types like ['DR', 'TR', 'PR', 'IR']
        config_dict: Settings (where to save files, database name, etc.)
        progress_callback: function to call with progress messages
        is_cancelled_callback:  function that returns True if user cancelled

    Returns:
        Dictionary with results
    """

    # Get default configuration values and merge with provided config
    #What this does , ConfigRepository()._get_defaults() = Get default settings from default_config.py
    #{**defaults, **config_dict} = Merge defaults with user's custom settings
    #Why? In the rare case ,user might not have set ALL settings, so we use defaults for missing ones.

    defaults = ConfigRepository()._get_defaults()
    config = {**defaults, **config_dict}  # Merge: defaults + user settings

    # Extract config values (all keys guaranteed to exist)-Daniel
    sqlite_filename = config['sqlite_filename']
    providers_file = config['providers_file']
    error_log_file = config['error_log_file']
    json_dir = config['json_dir']
    tsv_dir = config['tsv_dir']
    data_table = config['data_table']
    save_empty_report = config['save_empty_report']
    always_include_header_metric_types = config['always_include_header_metric_types']

    # Configure logger with current error log file,tells logger where to write errors using current config-Daniel
    set_error_log_file(error_log_file)

    # Set the callback for logger to use
    set_progress_callback(progress_callback)


    def log(msg):
        """Send message to callback or print."""
        if progress_callback:
            progress_callback(msg)
        else:
            print(msg)

    def is_cancelled():
        """Checks if operation was cancelled."""
        if is_cancelled_callback:
            return is_cancelled_callback()
        return False

    # Initialize results
    results = {
        'errors': []
    }

    try:
        # Clear error log
        open(error_log_file, 'w', encoding="utf-8").close()
        current_time = datetime.now()
        log_error(f'INFO: Start of harvester run: {current_time}')

        # Find the full path to the providers file using same logic as GUI-Daniel
        vendor_repo = VendorRepository(providers_file=providers_file)
        providers_file_path = vendor_repo._find_file()

        # Validate that file exists
        if not providers_file_path or not providers_file_path.exists():
            error_msg = f"Providers file '{providers_file}' not found"
            log(f"ERROR: {error_msg}")
            results['errors'].append(error_msg)
            return results


        # Build user_selections for load_providers
        user_selections = {
            'start_date': begin_date,
            'end_date': end_date,
            'reports': selected_reports,
            'vendors': selected_vendors
        }

        #  callback functions for provider loading errors/warnings..used them instead of signals
        def error_callback(msg):
            log(f"ERROR: {msg}")
            results['errors'].append(msg)

        def warning_callback(msg):
            log(f"WARNING: {msg}")

        def general_callback(msg):
            log(f"{msg}")

        providers = load_providers(
            str(providers_file_path),
            user_selections,
            error_callback,
            warning_callback,
            general_callback
        )

        if not providers:
            error_msg = "No valid providers found"
            log(f"ERROR: {error_msg}")
            results['errors'].append(error_msg)
            return results

        if is_cancelled():
            return results

        # Fetch provider API information
        providers_dict = fetch_json(providers, begin_date, end_date, selected_reports)

        if not providers_dict:
            error_msg = "Failed to fetch provider information from API"
            log(f"ERROR: {error_msg}")
            results['errors'].append(error_msg)
            return results

        if is_cancelled():
            return results

        # Initialize database
        conn = sqlite3.connect(sqlite_filename)
        cursor = conn.cursor()
        create_data_table(cursor, data_table)  # Pass data_table from config-Daniel
        conn.commit()
        conn.close()

        if is_cancelled():
            return results

        # Process each provider's reports
        for provider_name, provider_info in providers_dict.items():
            if is_cancelled(): #Check #1, before starting a provider
                break

            report_urls = provider_info.get('Report_URLS', {})
            #log_error(f'DEBUG gc: report list for {provider_name}: {report_urls}\n')
            log(f"Retrieving reports: {provider_name}") # do this line for pause..instead of retrieve ..use completed

            for report_id, report_url in report_urls.items():

                log_error(f"INFO: Retrieving report: {provider_name}: {report_id.upper()}: {report_url}")
                current_timestamp = datetime.now()
                formatted_time = current_timestamp.strftime("%M:%S")
                #log_error(f"DEBUG gc: Retrieving report at:{formatted_time} : {provider_name}: {report_id.upper()}: {report_url}")

                try:
                    process_item_details(provider_info, report_id, report_url,config)
                    #Pass config dict-Daniel

                    if is_cancelled():
                        log(f"Completed {provider_name}: {report_id.upper()}")
                        break


                except Exception as e:
                    error_msg = f"Error processing {provider_name}:{report_id}: {str(e)}"
                    log_error(f"ERROR: {error_msg}\n{traceback.format_exc()}")
                    results['errors'].append(error_msg)

        log(f"Finished")
        log(f"Check {error_log_file} for problems/reports that failed/exceptions")

    except Exception as e:
        error_msg = f"Harvester failed: {str(e)}"
        log(f"ERROR: {error_msg}")
        log_error(f"ERROR: {error_msg}\n{traceback.format_exc()}")
        results['errors'].append(error_msg)

    return results
