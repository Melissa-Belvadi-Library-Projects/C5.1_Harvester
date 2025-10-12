import sqlite3
import traceback
from datetime import datetime
from pathlib import Path
from logger import log_error, set_progress_callback
from create_tables import create_data_table
from load_providers import load_providers
from fetch_json import fetch_json
from process_item_details import process_item_details


def run_harvester(begin_date, end_date, selected_vendors, selected_reports,
                  progress_callback=None, is_cancelled_callback=None):
    """
    Run the COUNTER harvester with given parameters.

    Args:
        begin_date: Start date in YYYY-MM format
        end_date: End date in YYYY-MM format
        selected_vendors: List of vendor names to process (empty list = all vendors)
        selected_reports: List of report types like ['DR', 'TR', 'PR', 'IR']
        progress_callback: function to call with progress messages
        is_cancelled_callback:  function that returns True if user cancelled

    Returns:
        Dictionary with results
    """


    #  refresh values each time..provider file was loading older one
    import importlib
    import current_config
    importlib.reload(current_config)  # Force Python to re-read the file

    from current_config import (
        sqlite_filename,
        providers_file,
        error_log_file,
        json_dir,
        tsv_dir,
        data_table,
        save_empty_report,
        always_include_header_metric_types
    )


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

        providers = load_providers(
            providers_file,
            user_selections,
            error_callback,
            warning_callback
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
        create_data_table(cursor)
        conn.commit()
        conn.close()

        if is_cancelled():
            return results

        # Process each provider's reports
        for provider_name, provider_info in providers_dict.items():
            if is_cancelled():
                break

            report_urls = provider_info.get('Report_URLS', {})
            log(f"Retrieving reports: {provider_name}") # do this line for pause..instead of retrieve ..use completed

            for report_id, report_url in report_urls.items():
                if is_cancelled():
                    break

                log_error(f"INFO: Retrieving report: {provider_name}: {report_id.upper()}: {report_url}")

                try:
                    process_item_details(provider_info, report_id, report_url)

                except Exception as e:
                    error_msg = f"Error processing {provider_name}:{report_id}: {str(e)}"
                    log_error(f"ERROR: {error_msg}\n{traceback.format_exc()}")
                    results['errors'].append(error_msg)
                #around here ..insert infobox
                # if stop signals , write to progress report ,..completed provider ... take out warning ..only write for the last provider and report  collected
        #log(f"Retrieving report: {provider_name}: {report_id.upper()}")
        log(f"Finished")
        log(f"Check {error_log_file} for problems/reports that failed/exceptions")

    except Exception as e:
        error_msg = f"Harvester failed: {str(e)}"
        log(f"ERROR: {error_msg}")
        log_error(f"ERROR: {error_msg}\n{traceback.format_exc()}")
        results['errors'].append(error_msg)

    return results
