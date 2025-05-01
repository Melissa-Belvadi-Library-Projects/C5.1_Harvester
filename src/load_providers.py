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

        for row in reader:
            # Ensure the row has at least the mandatory columns
            if len(row) < len(headers): # sometimes the providers data is missing the empty tabs for the Delay and Retry columns
                row += [''] * (len(headers) - len(row))
            if 'Name' in header_indices:
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
            providers.append(provider)

    return providers

