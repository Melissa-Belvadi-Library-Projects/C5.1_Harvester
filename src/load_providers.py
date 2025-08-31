import csv
import sys
from logger import log_error

def load_providers(file_path):

    providers = []

    with open(file_path, 'r',encoding="utf-8") as file:
        # Use the csv module to read the TSV file
        reader = csv.reader(file, delimiter='\t')
        
        # Read the header row
        headers = next(reader)
        #print(f"Headers: {headers}")  # Debugging line

        # Define required headers
        required_headers = ['Name', 'Base_URL', 'Customer_ID']
        
        # Check for missing required headers
        missing_required_headers = [header for header in required_headers if header not in headers]
        if missing_required_headers:
            print(f"Error: Missing required columns in providers.tsv: {', '.join(missing_required_headers)}")
            sys.exit(1)  # Exit the program with a non-zero status code

        header_indices = {header: index for index, header in enumerate(headers)}

        ### Temporary as we merge the gui code in here  - remove this declaration when we are passing it from the gui
        user_selections = {
            'start_date': "2025-01",
            'end_date': "2025-08",
            'reports': ['DR', 'IR', 'TR', 'PR'],
            'vendors': ['EBSCO']
        }

        for row in reader:
            if not ''.join(row).strip():# skip empty (or all whitespace) rows (might especially be at the end of the file)
                continue
            # Ensure the row has at least the mandatory columns
            if len(row) < len(headers): # sometimes the providers data is missing the empty tabs for the Delay and Retry columns
                row += [''] * (len(headers) - len(row))
            if 'Name' in header_indices:
                if row[header_indices['Name']] not in user_selections['vendors']:  #not a vendor that the user selected in the GUI
                    continue
                provider_name = row[header_indices['Name']]
            else:
                log_error(f'No provider name - skipping {row}')
                continue
            version =  ( str(row[header_indices.get('Version')]) if 'Version' in header_indices else '' 
            )
            if version != '5.1':
                print (f'Vendor {provider_name} is not version 5.1; the Version column in your providers list must say exactly "5.1"; skipping')
                continue
            if 'Base_URL' in header_indices:
                provider_name = row[header_indices['Base_URL']]
            else:
                log_error(f'No Base_URL for {provider_name} - skipping {row}')
                continue
            # Create a provider dictionary, filling optional fields with empty strings if missing
            provider = {
                'Name': row[header_indices['Name']],
                'Base_URL': row[header_indices['Base_URL']],
                'Customer_ID': row[header_indices['Customer_ID']],
                'Requestor_ID': row[header_indices.get('Requestor_ID')] if 'Requestor_ID' in header_indices else '',
                'API_Key': row[header_indices.get('API_Key')] if 'API_Key' in header_indices else '',
                'Platform': row[header_indices.get('Platform')] if 'Platform' in header_indices else '',
                'Version': row[header_indices.get('Version')] if 'Version' in header_indices else '',
                'Delay': row[header_indices.get('Delay')] if 'Delay' in header_indices else '',
                'Retry': row[header_indices.get('Retry')] if 'Retry' in header_indices else ''
            }
            ### Temporary as we merge the gui code in here
            ### Remove the next line when we are actually populating the user_selections['vendors'] list from the gui
            user_selections['vendors'].append(provider['Name'])
            if provider['Name'] in user_selections['vendors']: ### Skip the ones the user doesn't want to use this run - from the GUI
                providers.append(provider)

    return providers

