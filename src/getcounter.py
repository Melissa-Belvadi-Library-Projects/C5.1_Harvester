#### Main program
import sqlite3
from datetime import datetime
from logger import log_error
from create_tables import create_data_table
from load_providers import load_providers  # Import the load_providers function
from fetch_json import fetch_json  # Import the fetch_json function to get report data
from process_item_details import process_item_details
from sushiconfig import sqlite_filename, providers_file, error_log_file


def json_to_sqlite(dict_providers):
    # Connect to the SQLite database
    conn = sqlite3.connect(sqlite_filename)
    cursor = conn.cursor()

    # Create tables if they do not exist
    create_data_table(cursor)
    #create_header_table(cursor)
    conn.commit()
    conn.close()
    # Process each provider's info
    for provider_name in dict_providers.keys():
        this_provider = dict_providers[provider_name]
        for report_id, report_url  in this_provider['Report_URLS'].items():  ###This was filtered for the user selections for report IDs
            #api_url = this_provider['Report_URLS'].get(report_id, 'Not available')  # use url for api
            log_error(f"\nINFO: Retrieving report: {provider_name}: {report_id.upper()}: \n{report_url}")
            print(f"Retrieving report: {provider_name}: {report_id.upper()}")
            process_item_details(this_provider,report_id,report_url)


if __name__ == "__main__":

    ### Temporary as we merge the gui code in here  - remove this declaration when we are passing it from the gui
    user_selections = {
        'start_date': "2025-01",
        'end_date': "2025-08",
        'reports': ['DR', 'IR', 'TR', 'PR'],
        'vendors': ['EBSCO']
    }
    open(error_log_file, 'w', encoding="utf-8").close()   ### empty out error log file
    current_time = datetime.now()
    log_error(f'INFO: Start of program run: Current date and time: {current_time}')

    # Load providers data from providers.tsv
    providers = load_providers(providers_file)  # With the GUI, this will only get the user_selections vendors list from among the providers_file
    # Fetch the provider api url info using fetch_json
    providers_dict = fetch_json(providers)
    # fetch_json returns
    if providers_dict and isinstance(providers_dict, dict):
        json_to_sqlite(providers_dict)
    else:
        log_error(f'ERROR: Getcounter Failed to get the providers info for the user selected vendors and reports from {providers_file}\n')
    print(f"Done all providers, all reports.\nCheck {error_log_file} for problems/reports that failed/exceptions")
