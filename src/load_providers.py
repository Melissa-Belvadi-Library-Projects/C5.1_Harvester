import csv
import sys
from logger import log_error

def load_providers(file_path, user_selections, error_callback , warning_callback ):
    """
    Loads provider data from a TSV file, validates it, and filters based on user selections.

    Args:
        file_path (str): The path to the TSV file.
        user_selections (dict): A dictionary containing user choices from the GUI.
        error_callback (callable): Function to call for fatal file-level errors.
        warning_callback (callable): Function to call for non-fatal, row-level warnings.

    Returns:
        list: A list of provider dictionaries on success.
        None: On any fatal validation failure.
    """
#added callback
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            # 1. General Validation: Sniff the delimiter to ensure it's a TSV.
            try:
                dialect = csv.Sniffer().sniff(file.read(2048), delimiters='\t,;')
                file.seek(0)  # Rewind the file after sniffing
                if dialect.delimiter != '\t':
                    error_message = f"File Format Error: Expected a Tab-Separated (TSV) file for providers, but it appears to be delimited by '{dialect.delimiter}'."
                    log_error(error_message)
                    error_callback(error_message)  # CHANGED: removed .emit()
                    return None
            except csv.Error:
                error_message = f"File Format Error: Could not determine file structure of {file_path}. Please ensure it is a valid TSV text file and not binary (like an Excel .xlsx file)."
                log_error(error_message)
                error_callback(error_message)
                return None

            reader = csv.reader(file, dialect)

            # 2. Header Validation
            try:
                headers = next(reader)
                num_headers = len(headers)
            except StopIteration:
                error_message = "File Format Error: The file is empty."
                error_callback(error_message)
                return None

            required_headers = ['Name', 'Base_URL', 'Customer_ID', 'Version']
            missing_headers = [h for h in required_headers if h not in headers]
            if missing_headers:
                error_message = f"Missing Required Columns: The providers file must contain the following columns: {', '.join(missing_headers)}."
                log_error(error_message)
                error_callback(error_message)
                return None

            # Create a map of header names to their column index for easy lookup
            header_indices = {header: index for index, header in enumerate(headers)}

            providers = []

            # 3. Process Data Rows
            for row_num, row in enumerate(reader, 2):  # Start from line 2
                if not ''.join(row).strip():  # Skip empty or all-whitespace rows
                    continue

                # Your original logic to handle rows with missing optional columns at the end
                if len(row) < num_headers:
                    row += [''] * (num_headers - len(row))
                # New validation: Check for rows that are too long
                elif len(row) > num_headers:
                    warning_message = f"Formatting Warning on line {row_num}: Expected {num_headers} columns, but found {len(row)}. Ignoring extra data."
                    warning_callback(warning_message) # removed emit
                    log_error(warning_message)
                    row = row[:num_headers]


                # --- Filter based on user selections from the GUI ---
                provider_name = row[header_indices['Name']]
                if provider_name not in user_selections.get('vendors', []):
                    continue

                # --- Row-level data validation ---
                version = row[header_indices.get('Version',-1)]
                if version != '5.1':

                    warning_message = f"Skipping '{provider_name}': The 'Version' column must be exactly '5.1', but it was '{version}'."
                    warning_callback(warning_message) # removed emit
                    log_error(warning_message)
                    continue

                if not row[header_indices['Base_URL']]:
                    warning_message = f"Skipping '{provider_name}': The 'Base_URL' column cannot be empty."
                    warning_callback(warning_message) #removed
                    log_error(warning_message)
                    continue

                if not row[header_indices['Customer_ID']]:
                    warning_message = f"Skipping '{provider_name}': The 'Customer_ID' column cannot be empty."
                    warning_callback(warning_message) #removed emit
                    log_error(warning_message)
                    continue

                provider_data = {header: value for header, value in zip(headers, row)}
                # Create the provider dictionary using .get for safety with optional columns
                provider = {
                    # Required fields (already checked that these headers exist)
                    'Name': provider_data.get('Name'),
                    'Base_URL': provider_data.get('Base_URL'),
                    'Customer_ID': provider_data.get('Customer_ID'),
                    'Version': provider_data.get('Version'),

                    'Requestor_ID': provider_data.get('Requestor_ID', ''), # If missing, returns ''
                    'API_Key': provider_data.get('API_Key', ''),          # If missing, returns ''
                    'Platform': provider_data.get('Platform', ''),       # If missing, returns ''
                    'Delay': provider_data.get('Delay', ''),          # If missing, returns ''
                    'Retry': provider_data.get('Retry', '')           # If missing, returns ''
                }
                providers.append(provider)

            if not providers:
                # This could be because the file only had a header, or no providers matched the user's selection
                error_message = f"No providers found in {file_path} for the vendors selected in the GUI."
                error_callback(error_message) #removed emit
                log_error(error_message)
                return None

        return providers

    except UnicodeDecodeError:
        error_message = f"File Encoding Error: {file_path} is not a valid UTF-8 text file. Please ensure it is not  a binary file (like an Excel .xlsx file)."
        error_callback(error_message)
        log_error(error_message)
        return None
    except FileNotFoundError:
        error_message = f"File Not Found: {file_path} could not be found at the specified path."
        error_callback(error_message)
        log_error(error_message)
        return None
    except Exception as e:
        # A catch-all for any other unexpected errors during file processing
        error_message = f"An unexpected error occurred while loading {file_path}: {e}"
        error_callback(error_message)
        log_error(error_message)
        return None