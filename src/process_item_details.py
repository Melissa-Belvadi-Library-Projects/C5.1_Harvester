# process_item_details.py, gets the  portion of data_dict
# that was generated by fetch_json for the specific provider as isolated as "this_provider" in jts

import inspect
import os
import re
import json
import datetime
import sqlite3
import csv
from data_columns import data_columns  # Assuming this contains your SQLite table column names
from logger import log_error
from fetch_json import get_json_data  # generic routine to get json report with various error handling, headers, content encoding, etc.
from insert_sqlite import insert_sqlite
from sushiconfig import sqlite_filename, json_dir, error_log_file, save_empty_report
from convert_counter_json_to_tsv import convert_counter_json_to_tsv


def count_date_keys(data):
    flattened_data = str(data)
    pattern = re.compile(r'\d{4}-\d{2}')
    matches = pattern.findall(flattened_data)
    return len(matches)

def process_attribute_performance(item):
    # Extract 'Attribute_Performance' from the item
    attribute_performance = item.get('Attribute_Performance', [])
    # Variable to hold performance data
    performance_data = None
    # Variable to hold the result data
    rows_to_insert = []
    # Iterate through each entry in 'Attribute_Performance'
    for entry in attribute_performance:
        # Initialize a base dictionary for each entry
        attr_base_data = {key: entry[key] for key in entry if key != 'Performance'}
        #COUNTER is inconsistent in its instructions about Proprietary so we normalize to Proprietary
        if 'Proprietary_ID' in attr_base_data:
            attr_base_data['Proprietary'] = attr_base_data.pop('Proprietary_ID')
        performance_data = entry.get('Performance', {})
        # Process the performance metrics and create new rows
        for metric_type, metrics in performance_data.items():
            for month_year_key, usage in metrics.items():
                # Split "YYYY-MM" into year and month
                year, month = map(int, month_year_key.split('-'))
                # Create a new dictionary for this metric entry
                row_data = {
                    **attr_base_data,  # Merge the base data
                    'Data_Year': year,
                    'Data_Month': month,
                    'Metric_Type': metric_type,
                    'Metric_Usage': usage
                }
                # Append the row to the list
                rows_to_insert.append(row_data)
    return rows_to_insert  # Return the list of dictionaries

# this function just gets the metric types for the report header table; we'll get them again for the data table
def extract_metric_types(report_items):
    metric_types = set()  # Using a set to avoid duplicates
    # Check if report_items has at least one item
    for r_item in report_items:
        # Navigate to the Performance object
        attribute_performance = r_item.get('Attribute_Performance',[])
        for entry in attribute_performance:
            if 'Performance' in entry:
                # Add keys from the Performance object to the metric_types set
                for metric in entry['Performance'].keys():
                    metric_types.add(metric)
    # Convert set back to a list for the final output
    return list(metric_types)

def add_missing_columns(row, data_col):
    #Adds missing columns to each dictionary in the list.
    for col in data_col:
        row.setdefault(col, '')  # Set default value if column is missing
    return row  # Return the modified dict

def publisher_id_string(publisher_id_data):
    if not publisher_id_data:
       return ''
    #Publisher_ID is title level and can include Proprietary but not to be confused with Proprietary in the Item_ID
    #publisher_id_data = report_header.get("Publisher_ID", {})
    publisher_id_list = []
    # Iterate over all key-value pairs in the Publisher_ID in report_items NOT header
    for key, values in publisher_id_data.items():
        if isinstance(values, list):  # Ensure the value is a list as per the specification
            for value in values:
                # Append the key-value pair in "key:value" format
                publisher_id_list.append(f"{key}:{value}")
    # Join all key-value pairs with semicolons
    publisher_id = "; ".join(publisher_id_list)
    return publisher_id

# Note distinction between report_id which includes my EX pretend standard views and report_type
### which comes directly from the actual report header and for the EX ones, will be the 2-letter master report
def save_json(report_json, report_id, provider_info, json_folder=json_dir, save_empty=False, report_items=None):
    vendor = provider_info.get('Name', '').replace(' ','_')
    subfolder = os.path.join(json_folder, vendor)
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    report_header = report_json.get("Report_Header", {})
    if not report_header:
        log_error(f'ERROR: the report header is missing, unable to save a report for {vendor}')
        return -1
    report_type = report_header.get("Report_ID","")
    exceptions = report_header.get("Exceptions","")
    api_platform = provider_info.get("Platform","")
    if exceptions:
        log_error(f'ERROR: Exceptions reported for {vendor}: {report_type}')
    date_range = provider_info.get("Dates","")
    created_date = f"{datetime.datetime.now():%Y_%m_%d}"
    if not all ((report_type,date_range,created_date,vendor)):
        return -1
    if api_platform:
        json_filename = f'{vendor}_{report_id}_{api_platform}_{date_range}_{created_date}.json'
    else:
        json_filename = f'{vendor}_{report_id}_{date_range}_{created_date}.json'
    if save_empty and not report_items:
        json_filename = json_filename.removesuffix(".json") + "_empty.json"
    if exceptions:
        if len(exceptions) == 1 and exceptions[0].get("Code") == 3030:  # Don't bother user to print if just some vendors don't have data available for those dates
            log_error(f'Warning:       Exception is for date range only:\n        {exceptions}')
        else:
            print(f'ERROR: Exception for {json_filename}; see error log for details')
            log_error(f'ERROR: Exception given for {json_filename}; {exceptions}\nThe report may still have been saved and added to the database, but may not have the data you wanted')
    full_file_path = os.path.join(subfolder, json_filename)
    with open(full_file_path, "w", encoding="utf-8") as json_file:
        json.dump(report_json, json_file, indent=4)
    return full_file_path

"""
    Parse a TSV file with specific format:
    - Skip first 15 rows
    - 16th row contains column headers
    - Special handling for MMM-YYYY date columns
    Returns a list of dictionaries, where each dictionary represents a row for SQLite insertion.
"""
def parse_tsv_file(file_path, provider_name, report_type):
    # Month name to number mapping
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    result_rows = []

    with open(file_path, 'r', encoding='utf-8', newline='') as tsv_file:
        # Skip the first 14 rows which is the COUNTER report header in the tsv
        for _ in range(14):
            next(tsv_file)

        # Read the TSV data
        reader = csv.reader(tsv_file, delimiter='\t')
        headers = next(reader)  # 16th row has column headers
        # Process each data row
        for row in reader:
            # Skip empty rows
            if len(row) == 0 or all(not cell.strip() for cell in row):
                continue

            # Create base dictionary with non-date columns
            base_dict = {}
            date_columns = []
            base_dict["Provider_Name"] = provider_name
            base_dict["Report_Type"] = report_type[:2]
            # First pass: identify regular columns and date columns "headers" = column names
            for idx, header in enumerate(headers):
                if idx < len(row):
                    if header == "Reporting_Period_Total":
                        continue
                    # Check if this is a date column (MMM-YYYY format)
                    if '-' in header and len(header.split('-')) == 2:
                        month_str, year_str = header.split('-')
                        if month_str in month_map:
                            date_columns.append((idx, header, month_str, year_str))
                        else:
                            # Not a proper date column, treat as regular
                            base_dict[header] = row[idx]
                    else:
                        # Regular column
                        base_dict[header] = row[idx]
            # Second pass: create separate row for each date column with a value
            for col_idx, date_header, month_str, year_str in date_columns:
                if col_idx < len(row) and row[col_idx].strip():
                    # Create a new dictionary for this date entry
                    data_dict = base_dict.copy()
                    # Add date information
                    data_dict['Data_Month'] = month_map[month_str]
                    data_dict['Data_Year'] = int(year_str)
                    data_dict['Metric_Usage'] = row[col_idx]
                    # Remove the original date column from the dict
                    if date_header in data_dict:
                        del data_dict[date_header]
                    result_rows.append(data_dict)
    return result_rows


def process_item_details(provider_info,report_type,get_report_url):
    provider_name = provider_info.get('Name')
    if not all((provider_info,report_type,get_report_url)):
        log_error(f"ERROR:  missing one or more of the function parameters\n")
        return -1
    try:
        ################# This uses get_json_data in fetch_json.py to actually get the specific report
        report_data = get_json_data(get_report_url,provider_info)
        if (not report_data) or (isinstance(report_data, int)) or (not isinstance(report_data, dict)): # an int response is an error
            log_error(f"ERROR: Processing {provider_name}:{report_type.upper()}: unable to get report {report_type.upper()}\n")
            return -1
    except Exception as e:
        log_error(f"ERROR: Processing {provider_name}:{report_type.upper()}: Error occurred for {get_report_url}: \n{e} type: {type(e).__name__}\n")
        return None
    try:
        report_header = report_data.get("Report_Header", {})
        if not report_header:
            log_error(f"ERROR: Processing {provider_name}:{report_type.upper()}: Error: Got json data but no Report_Header for {report_type.upper()}\n")
            return -1

    except Exception as e:
        log_error(f"ERROR: Processing {provider_name}:{report_type.upper()}: Error: Got json data but no Report_Header for {report_type.upper()}\n: {e} type: {type(e).__name__}\n")
        return -1

    report_header["Provider_Name"] = provider_info.get('Name') # this doesn't really come from the json report header but we need it in sqlite
    if not report_header["Provider_Name"]:
        log_error(f"ERROR: Processing {provider_name}:{report_type.upper()}: Error: Got Report Header but no Name for {report_type.upper()}\n")
        return -1

    try:
        report_items = report_data.get("Report_Items", [])
        if not report_items:
            log_error(f"Warning: Processing {provider_name}:{report_type.upper()}: Error Got json data but no Report_Items for:{report_type.upper()}")
            if save_empty_report:
                log_error(f'      Since you chose in sushiconfig.py to save empty reports,\n     you will find the tsv for {provider_name}:{report_type.upper()} with header and exceptions but no table.')
            if not save_empty_report:  # user configures whether they want to save a report with just the header so they have a record of trying and not having data for that report/period
                return -1
        #metric_types = extract_metric_types(report_items)
    except Exception as e:
        log_error(f"Warning: Processing {provider_name}:{report_type.upper()}: Error Got json data but no Report_Items for:\n{report_type.upper()}\n:   {e} type: {type(e).__name__}")
        if save_empty_report:
            log_error(f'          Since you chose in sushiconfig.py to save empty reports,you will find the tsv for {provider_name}:{report_type.upper()} with header and exceptions but no table.')
        return -1
    ########### Step 1 - Save the json to a file
    #save the entire json to a file in folder specified in sushiconfig
    json_saved_filename = save_json(report_data, report_type, provider_info, json_dir, save_empty_report, report_items)
    if not json_saved_filename or not isinstance(json_saved_filename, str):
        print(f'Unable to save json for {provider_name}:{report_type.upper()}, key data is missing, skipping this report')
        log_error(f'ERROR: Unable to save json for {provider_info} {report_type.upper()};\nreport_data={report_data}\n')
        return -1

    tsv_saved_file = convert_counter_json_to_tsv(report_type.upper(),json_saved_filename, provider_info)

    if not tsv_saved_file:
        print(f'Unable to save tsv for: {provider_name}: {report_type.upper()}; see {error_log_file} for details\n')
        log_error(f'ERROR: Unable to save tsv for: {provider_name}: {report_type.upper()}\njson file: {json_saved_filename}\n')
        return -1


    ########## Step 3 - save the data from the EX reports to the sqlite database
    ####   From here on we are only working with the special master reports for the database
    if not report_type.endswith("EX"):
       return None

    #log_error(f'Report_type: {report_type.upper()}\n')
        #Not ready to save IR data to sqlite
#    if report_type.upper() in ("IR", "IR_A1", "IR_M1", "IR_EX"):
#        return 0

    ### Ready to create the data_table entries in the sqlite database.
    #### We only use master reports for the database, not the standard views
    #### report_items in tabular reports would be a single row with columns for the months' data
    ##### but in our database will become multiple rows
    ###  for each year-month pairing, and for each of those, for each metric_type, YOP, data_type, etc.
    ###  so the data table really blows up for TR and IR for all combinations of values
    ####  rows{} gets all of the data specific to each row to be written to the sqlite usage_data table

    ### From here to the end is all about the data going into the database
    ### Here is where we need to use the EX reports instead of the original master report- for the database

    #Use the tsv file to make the sqlite database rows
    try:
        if tsv_saved_file.endswith('empty.tsv'):
            log_error(f'INFO: {provider_name}:{report_type} is empty, nothing to save to sqlite database.')
            return None
        #### MUST ALSO PASS the Provider_Name and Report_Type!!!!!
        rows = parse_tsv_file(tsv_saved_file, provider_name, report_type)
    except Exception as h:
        log_error(f'ERROR: Unable to open or parse the tsv file so unable to write the data to the sqlite database.\nTSV filename tried: {tsv_saved_file}\n{h}\n')
        return None
    # Connect to SQLite using the imported `sqlite_filename` we open it once then close it once at the end of this function
    conn = sqlite3.connect(sqlite_filename)
    cursor = conn.cursor()
    if not rows:
        log_error(f'INFO: no data retrieved from tsv file, so nothing to save to sqlite database.')
        return None
    log_error(f'INFO: saving the contents of {tsv_saved_file} to the sqlite database\n')

    for row in rows:
        try:
            ####### The actual insert per each row of usage data
            insert_sqlite(row,report_type,cursor,conn)
        except sqlite3.OperationalError as e:
            # Handle operational errors (e.g., unable to connect, missing table, etc.)
            log_error(f"ERROR: OperationalError: {e}")

        except sqlite3.DatabaseError as e:
            # Generic database errors
            log_error(f"ERROR: DatabaseError: {e}")

        except sqlite3.Error as e:
            # Handle SQLite errors
            error_message = f"\nSQLite Error: {e}\n"
            log_error(error_message)

    if conn:
    #save all of the data sent to sqlite for this report
        conn.commit()
        conn.close()

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
