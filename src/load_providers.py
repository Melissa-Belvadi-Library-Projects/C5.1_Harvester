import csv
import sys
import os
from logger import log_error

def sanitize_tsv_file(file_path):
    """
    Reads a TSV file, corrects rows with too few or too many columns,
    and overwrites the original file with the corrected version.

    Args:
        file_path (str): The full path to the TSV file.

    Returns:
        bool: True if the file was successfully sanitized or was already correct.
              False if the file could not be found or was empty.
    """
    if not os.path.exists(file_path):
        log_error(f"Error: File not found at '{file_path}'.")
        return False

    # --- Read Phase ---
    try:
        with open(file_path, 'r', encoding="utf-8", newline='') as file:
            lines = file.readlines()
    except Exception as e:
        log_error(f"Error reading file: {e}")
        return False

    if not lines:
        log_error("File is empty. No sanitization needed.")
        return True # An empty file is technically "clean"

    # --- Analysis and Fixing Phase ---
    header_line = lines[0]
    expected_tab_count = header_line.count('\t')
    expected_column_count = expected_tab_count + 1

    corrected_lines = [header_line]
    changes_made = False

    for i, line in enumerate(lines[1:], start=2):
        clean_line = line.rstrip()
        current_tab_count = clean_line.count('\t')
        processed_line = ''
        if current_tab_count < expected_tab_count:
            tabs_to_add = expected_tab_count - current_tab_count
            processed_line = clean_line + ('\t' * tabs_to_add) + '\n'
        elif current_tab_count > expected_tab_count:
            columns = clean_line.split('\t')
            truncated_columns = columns[:expected_column_count]
            processed_line = '\t'.join(truncated_columns) + '\n'
        else:
            processed_line = clean_line + '\n'
        if processed_line != line:
            changes_made = True
        corrected_lines.append(processed_line)
    # --- Overwrite Phase (only if necessary) ---
    if changes_made:
        log_error(f"Inconsistencies found in {file_path}. Overwriting file with corrected data...")
        try:
            with open(file_path, "w", encoding="utf-8", newline='') as outfile:
                outfile.writelines(corrected_lines)
            #log_error("File successfully sanitized.")
        except Exception as e:
            log_error(f"Error writing sanitized file: {e}")
            return False
    else:
        pass
        #print("File structure is already consistent. No changes made.")
    return True


def load_providers(file_path, user_selections, error_callback , warning_callback, general_callback ):
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
    general_callback('Loading your provider information...')
    is_file_ready = sanitize_tsv_file(file_path)
    if is_file_ready:
        with open(file_path, 'r', encoding="utf-8", newline='') as file:
            reader = csv.reader(file, delimiter='\t')
            headers = next(reader)
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
