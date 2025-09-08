### fetch_json - gets the /reports and creates the URLs for all supported master reports (TR,DR,PR,IR) into a data_dict json object
### that has two top-level objects: provider_info and Report_URLS
import json
import time
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import brotli
from logger import log_error
import traceback
from current_config import error_log_file, default_begin
from tsv_utils import default_metric_types, official_reports #default metric types is also a list of all possible valid report types, as the keys
#from requests.exceptions import SSLError
#from urllib3.exceptions import SSLCertVerificationError

''' Example of custom report for later development:
 {
    "Report_Name": "sciencedirect:Total Item Requests by Platform",
    "Report_ID": "sciencedirect:TR_SJ1",
    "Release": "5.1",
    "Report_Description": "Total Item Requests by Platform",
    "Path": "/reports/tr_sj1",
    "First_Month_Available": "2015-01-01",
    "Last_Month_Available": "2025-04-01"
  },
'''

def is_json(ij_dict):
    try:
        json.loads(ij_dict)  # Try to parse the variable as JSON
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def get_dates():
    global default_begin
    # Calculate default end date (previous month)
    today = datetime.now()
    default_end = (today - relativedelta(months=1)).strftime('%Y-%m')
    #default_begin set in sushiconfig
    if not default_begin:
        default_begin = "2025-01"

    print("What start and end dates do you want to collect data for?")
    print(f"(Press Enter for default: Begin={default_begin}, End={default_end})")

    while True:
        # Prompt for Begin Date
        begin_date = input("Enter the Begin Date (yyyy-mm): ").strip()

        # Use default if empty
        if begin_date == "":
            begin_date = default_begin
            print(f"Using default begin date: {begin_date}")

        # Validate Begin Date format
        if validate_date(begin_date):
            break
        else:
            print("Invalid format. Please enter the begin date in 'yyyy-mm' format.")
            exit(0)

    while True:
        # Prompt for End Date
        end_date = input("Enter the End Date (yyyy-mm): ").strip()

        # Use default if empty
        if end_date == "":
            end_date = default_end
            print(f"Using default end date: {end_date}")

        # Validate End Date format
        if validate_date(end_date):
            break
        else:
            print("Invalid format. Please enter the end date in 'yyyy-mm' format.")
            exit(0)

    return begin_date, end_date

def get_report_type():
    print(f'You can choose just one report type (eg TR_J1) or Enter for all of them. Type it in caps\n')
    report_type = input("What report type: ").strip().upper()
    if not report_type:
        print(f'Retrieving all supported report types for your providers.\n\n')
        return None
    elif report_type in official_reports:
        if report_type and report_type[-1].isdigit():
            print("Standard views will generate tsv but will not save any data to the sqlite database.")
            log_error(f"INFO: Standard view {report_type} will generate tsv but will not save any data to the sqlite database.")
        else:
            log_error(f"INFO: Report {report_type} will generate tsv and will save data to the sqlite database.")
        return(report_type)
    else:
        print(f'{report_type}: Sorry, this harvester cannot yet retrieve provider custom reports. Exiting.\n')
        #log_error(f'INFO: Report type: {report_type} is custom to this provider. A tsv will be created but nothing saved to the sqlite database\n')
        exit(0)

def is_custom_report(provider_info, report_type):
    if report_type:
        if report_type not in official_reports:
            special_base_url = base_url.strip('/')+provider_info('Path')
        else:
            return None
    else:
        return None
    report_name = provider_info.get('Report_Name','')
    report_description = provider_info.get('Report_Description','')
    return special_base_url, report_name, report_description


def validate_date(date_string):
    try:
        # Attempt to parse the date
        datetime.strptime(date_string, "%Y-%m")
        return True
    except ValueError:
        return False

def check_dates(provider_name, begin_date, end_date, first_month, last_month):
    # Convert string dates to datetime objects for comparison
    begin_date_dt = datetime.strptime(begin_date, "%Y-%m")
    first_month_dt = datetime.strptime(first_month, "%Y-%m")
    last_month_dt = datetime.strptime(last_month, "%Y-%m")
    end_date_dt = datetime.strptime(end_date, "%Y-%m")

    # Check if begin_date is before first_month
    if begin_date_dt < first_month_dt:
        print(f"WARNING: data from {provider_name} will not start until {first_month}")
        log_error(f"WARNING: data from {provider_name} will not start until {first_month}")
        begin_date=first_month
    # Check if end_date is after last_month
    if end_date_dt > last_month_dt:
        print(f"WARNING: data from {provider_name} only available through {last_month}")
        log_error(f"WARNING: data from {provider_name} only available through {last_month}")
        end_date=last_month
    return begin_date, end_date

def get_dd(date_string, position):
    #Generates the first or last date of a given month in the format YYYY-MM. Returns a string in format YYYY-MM-DD
    try:
        # Parse date_string into a datetime object
        parts = date_string.split("-")
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2]) if len(parts) == 3 else 1  # Default to 1 if day is not provided
        date_object = datetime(year, month, day)
        if not (1 <= month <= 12):
            raise ValueError("Invalid month. Month must be between 1 and 12.")
            return None

        # If the position is "begin", use the day directly as 1
        if position == "begin":
            day = 1  # First day of the month
            date_object = datetime(year, month, day)
        elif position == "end":
            # Calculate the last day of the month
            # Start with the first of the month, move to the next month, and subtract 1 day
            date_object = datetime(year, month, 1) + timedelta(days=31)
            date_object = date_object.replace(day=1) - timedelta(days=1)
        else:
            raise ValueError("Position must be 'begin' or 'end'.")

        return date_object.strftime("%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"ERROR processing input: {e}")

### This is used for getting all URLs via the SUSHI API - the list of supported reports, and the individual reports
# return None means a failure of this one URL
# return -1 means a failure of the entire provider API - don't bother trying any more URLs with that same base_url
def get_json_data(url, provider_info):
    report_json = {}
    provider_name = provider_info.get('Name','')
    sleep_delay = provider_info.get('Delay',0)
    retry_needed = provider_info.get('Delay',0)
    try:
        if sleep_delay and isinstance(sleep_delay, str):
            sleep_delay = float(sleep_delay)
        else:
            sleep_delay = 0.1
    except:
        sleep_delay = 5
    if retry_needed and not sleep_delay:
        sleep_delay = 5
    headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://https://www.countermetrics.org/'
    }
    try:
        # We are going to try up to 3 times to make the API call, because some vendors require sending the request twice and there can be other random connection failures
        max_attempts = 3  # Maximum number of tries
        attempts = 0      # Counter for the number of tries
        fatal_error = 0  #If we get a fatal error, there will not be any point in retrying
        http_desc = None

        while attempts < max_attempts:
            attempts += 1
            if sleep_delay:
                time.sleep(sleep_delay)
            if fatal_error:
                log_error(f'ERROR:  Got a fatal HTTP error - need to give up on this provider\n')
                break
            try:
                response = requests.get(url, headers=headers, timeout=(10,30)) #### The actual API call
                #response.raise_for_status()  # Raise exception for HTTP error codes (4xx, 5xx)
                if response.status_code == 200:
                    http_desc = None
                    break
                elif response.status_code == 202:
                    http_desc = (f"Request is queued - try again later:{url}\n {response.text}")
                    log_error(f'{http_desc}\n')
                    if sleep_delay < 5:
                        sleep_delay = 5
                    time.sleep(sleep_delay)
                    fatal_error = 0
                    continue
                elif response.status_code == 400:
                    http_desc = "Bad Request! Check your request parameters"
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    log_error(f'ERROR: fatal error: code={response.status_code}; report_json={report_json}\n')
                    return -1
                elif response.status_code == 401:
                    http_desc = "requestor_id or api_key wrong!"
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    log_error(f'ERROR: fatal error: code={response.status_code}; report_json={report_json}\n')
                    return -1
                elif response.status_code == 403:
                    http_desc = "Unauthorized requestor_id or customer_id. Check your request parameters."
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    log_error(f'ERROR: fatal error: code={response.status_code}; report_json={report_json}\n')
                    return -1
                elif response.status_code == 404:
                    http_desc = "Resource not found! Check if the base_url is correct."
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    log_error(f'ERROR: fatal error: code={response.status_code}; report_json={report_json}\n')
                    return -1
                elif response.status_code == 429:
                    http_desc = f"Too many requests too fast. {provider_name} needs a delay: {response.text}"
                    if sleep_delay and (isinstance(sleep_delay, int) or isinstance(sleep_delay, float)):
                        time.sleep(sleep_delay)
                    else:
                        sleep_delay = 3 #a reasonable delay if we need one but don't have a number to use
                        time.sleep(sleep_delay)
                    fatal_error = 0
                    continue
                elif response.status_code == 500:
                    http_desc = "Server error! The API might be down or experiencing issues."
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    log_error(f'ERROR: fatal error: code={response.status_code}; report_json={report_json}\n')
                    return -1
                elif response.status_code == 503:
                    http_desc = f"Service too busy or request is queued, try again soon and add a delay in your providers.tsv: {url}\n{response.text}"
                    log_error(f'ERROR: {http_desc}\n')
                    if not sleep_delay:
                        sleep_delay = 5 # a reasonable time to retry if we didn't have a provider-advised one, will total 10 seconds
                    time.sleep(sleep_delay+5)
                    fatal_error = 0
                    continue
                else:
                    http_desc = f"Unexpected status code: {response.status_code}\nResponse body: {response.text}"
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    log_error(f'ERROR: fatal error: code={response.status_code}; report_json={report_json}\n')
                    return -1

            ### these are the while-try
            except requests.exceptions.Timeout:
                log_error(f"ERROR: trying to get supported reports list for  {provider_name}\n{url}: The URL request timed out.")
                return None
            except requests.exceptions.HTTPError as err:
                log_error(f"ERROR: \nHTTP Error: {err}")
                log_error(f"ERROR: Response Code: {err.response.status_code}")
                print(f"HTTP Error trying to get {url} for  {provider_name}.\n See error log {error_log_file} for details.\n Cannot continue processing this vendor.")
                log_error(f"ERROR: HTTP Error trying to get  {provider_name}\n{url}: {err}.")
                try:
                    log_error(err.response.text)
                except Exception as d:
                    log_error(f'ERROR:  {err.response.content}; {d}\n')
                return -1
            except requests.exceptions.ConnectionError as e:
                log_error(f"ERROR: Network error occurred: {e}")
                return -1
            except requests.exceptions.TooManyRedirects as e:
                log_error(f"ERROR: Too many redirects: {e}")
                return -1
            except requests.exceptions.RequestException as e:
                # Catch any other requests-related exceptions
                log_error(f"ERROR: An error occurred: {e}")
                return -1
            except Exception as e:
                log_error(f'ERROR: An error occurred within the while try: {e}\n')
                return -1

        #out of the while loop without a return -1 interrupting it
        report_json = response.json()
        # Handle brotli encoding if present
        if response.headers.get('Content-Encoding') == 'br':
            decoded_content = brotli.decompress(response.content)
            report_json = json.loads(decoded_content)
        if  (not isinstance(report_json, dict)) and (not isinstance(report_json, list)):
            log_error(f"ERROR: Failed to get a valid response after 3 attempts, url={url}")
            return -1

        return report_json

    except Exception as e2:
        log_error(f'ERROR: An error occurred within the main try of get_json_data: {e2}\n')
        return -1


# if vendor needs delay between url requests, provide the appropriate delay time
def timedelay(provider_name,thisdelay):
    if thisdelay is None:  # Check if it's None first
        delaylength =2
    elif thisdelay == '':  # Check if it's an empty string
        delaylength = 2
    elif isinstance(thisdelay, int):  # Check if it's an integer
        delaylength =thisdelay
    else:  # Handle anything else - eg a string of any len > 0
        delaylength = 2
        log_error(f"ERROR: 'Delay' for {provider_name} is unexpected, using 2 seconds; value: {thisdelay} -> {type(thisdelay)}")
    return delaylength


def fetch_json(providers):
    begin_date, end_date = get_dates()
    print(f"\nBegin Date: {begin_date}, End Date: {end_date}\n")

    data_dict = {}  # Initialize as an empty dictionary for providers
    report_type_one = None
    report_type_one = get_report_type() # if user wants only one specific kind of COUNTER report


    for provider in providers:
        provider_info ={}
        checked_date = 0
        get_report_url_credentials = ''
        get_report_url_final = ''
        get_report_url_daterange = ''
        credentials =''
        b=''
        e=''
        # Access mandatory fields
        provider_name = provider.get('Name')
        base_url = provider.get('Base_URL')
        customer_id = provider.get('Customer_ID')
        # Collect missing fields and present information
        missing_fields = []
        if not provider_name:
            missing_fields.append("Name")
            continue
        if not base_url:
            missing_fields.append("Base_URL")
            continue
        if not customer_id:
            missing_fields.append("Customer_ID")
            continue
        # If there are any missing mandatory fields
        if missing_fields:
            present_info = []
            if provider_name:
                present_info.append(f"Name: {provider_name}")
            if base_url:
                present_info.append(f"Base_URL: {base_url}")
            if customer_id:
                present_info.append(f"Customer_ID: {customer_id}")

            # Print error information
            print(f"Error: Missing mandatory fields, skipping this provider: {', '.join(missing_fields)}. Present: {', '.join(present_info)}\n")
            continue  # Skip to next provider if mandatory fields are missing

        # Optional fields accessed safely
        requestor_id = provider.get('Requestor_ID', '')
        api_key = provider.get('API_Key', '')
        platform = provider.get('Platform', '')
        version = provider.get('Version', '5.1')  # Default to '5.1' if not provided
        delay = provider.get('Delay', '')            # Optional field
        retry = provider.get('Retry', '')            # Optional field
        first_month_available = provider.get('First_Month_Available', '')
        last_month_available = provider.get('Last_Month_Available', '')
        path = provider.get('Path', '') # for custom reports
        report_name = provider.get('Report_Name', '') # for custom reports
        report_description = provider.get('Report_Description', '') # for custom reports

        # Initialize the provider entry
        provider_info = {
            'Name' : provider_name,
            'Base_URL': base_url,
            'Customer_ID': customer_id,
            'Requestor_ID': requestor_id,
            'API_Key': api_key,
            'Platform': platform,
            'Version': version,
            'Delay': delay,
            'Retry': retry,
            'Path' : path,
            'First_Month_Available' : first_month_available,
            'Last_Month_Available' : last_month_available,
            'Report_Name' : report_name,
            'Report_Description' : report_description,
            'Report_URLS': {}  # Initialize the report URLs dictionary
        }
        #account credentials from the providers.tsv are always used together as a string
        credentials = f"customer_id={customer_id}" if customer_id else credentials
        credentials = f"{credentials}&requestor_id={requestor_id}" if requestor_id else credentials
        credentials = f"{credentials}&api_key={api_key}" if api_key else credentials

        try: ### first we're going to get the list of supported reports
	    # fix base_urls from the providers.tsv to make sure there is exactly one suffix: /reports/
            if not base_url.endswith("/reports/"):
                if base_url.endswith("/reports"):
                    base_url = f"{base_url}/"
                else:
                    base_url = f"{base_url.rstrip('/')}/reports/"
            # Construct the report_json_url to get the list of reports
            report_json_url = f"{base_url[:-1]}?{credentials}&platform={platform}"
            if platform:
                report_json_url = f"{base_url[:-1]}?{credentials}&platform={platform}"
            else:
                report_json_url = f"{base_url[:-1]}?{credentials}"

             ### *** Here is the actual call to get the report of supported reports #####
            log_error(f'INFO: {provider_name}: supported reports API URL=\n{report_json_url}')
            report_json = get_json_data(report_json_url,provider_info)
            if not report_json:
                log_error(f'ERROR: get_json_data failed for this url, {report_json_url}, skipping provider\n')
                continue
            elif report_json == -1:
                log_error(f'ERROR: get_json_data failed fatally not specific to this url,{report_json_url}, which means skip this entire provider\n')
                continue #try the next provider

            # Now we can process the list of  reports
            # Loop through the list of reports supported as returned by get_json_data to create all URLs for supported reports
            #  Need to figure out where custom reports will fit into this           if is_custom_report(provider_info, report_type)
            if isinstance(report_json, list):  # this must be the supported_reports api response
                for report in report_json:
                    if "Report_ID" not in report:
                        log_error(f"ERROR: No_report_id: a report from {provider_name} does not contain Report_ID\n")
                        continue
                    report_id = report.get('Report_ID')
                    if report_type_one:
                        if report_id != report_type_one:
                            continue # skip to the next report in the list for this provider
                    if platform:## this is the providers.tsv platform, NOT the Platform Report meaning of platform
                        get_report_url_credentials = f'{base_url}{report_id.lower()}?{credentials}&platform={platform}'
                    else:
                        get_report_url_credentials = f'{base_url}{report_id.lower()}?{credentials}'
                    #Determine the overlap between what date range the user asked for, and what is available for this report
                    first_month = report.get('First_Month_Available', '')
                    if not validate_date(first_month):
                        b=begin_date
                    last_month = report.get('Last_Month_Available', '')
                    if not validate_date(last_month):
                        e=end_date
                    # adjusts and notifies user if user wants too early begin or too late end
                    if validate_date(first_month) and validate_date(last_month) and not checked_date:
                        b, e = check_dates(provider_name, begin_date, end_date, first_month, last_month)
                        checked_date = 1
                    if (b > begin_date and not checked_date) and (e  < end_date and not checked_date):
                        print(f"WARNING: data from {provider_name} will not start until {b} and  only available through {e}\n")
                        log_error(f"WARNING: data from {provider_name} will not start until {b} and  only available through {e}\n")
                    elif b > begin_date and not checked_date:
                        print(f"WARNING: data from {provider_name} will not start until {b}")
                        log_error(f"WARNING: data from {provider_name} will not start until {b}\n")
                    elif e  < end_date and not checked_date:
                        print(f"WARNING: data from {provider_name} only available through {e}")
                        log_error(f"WARNING: data from {provider_name} only available through {e}\n")
                    if not validate_date(first_month):
                        b = begin_date
                    if not validate_date(last_month):
                        e = end_date
                    b = get_dd(b,"begin")
                    e = get_dd(e, "end")
                    provider_info['Dates'] = f"{b}-{e}"
                    # Append begin and end dates
                    ### For the master reports we will get them twice - the primary one will have the default attributes to show,
                    #### and the "extra" one will have more attributes to show for maximizing the data collection for the database
                    #### this program will invent its own "standard view" for this: TR_EX, DR_EX, etc.

                    get_report_url_daterange = f"{get_report_url_credentials}&begin_date={b}&end_date={e}"
                    # Maximize all possible additional data breakdowns using attributes_to_show
                    extra_report_id = report_id + "_EX"
                    if report_id == 'IR':
                        IR_EX_attributes_to_show = "Authors|Publication_Date|Article_Version|YOP|Access_Type|Access_Method"
                        get_report_url_final_extra =f"{get_report_url_daterange}&attributes_to_show={IR_EX_attributes_to_show}&include_parent_details=True"
                        get_report_url_final =f"{get_report_url_daterange}"
                    elif report_id == 'TR':
                        get_report_url_final =f"{get_report_url_daterange}"
                        get_report_url_final_extra =f"{get_report_url_daterange}&attributes_to_show=YOP|Access_Method|Access_Type"
                    elif report_id in {'DR', 'PR'}:
                        get_report_url_final =f"{get_report_url_daterange}"
                        get_report_url_final_extra =f"{get_report_url_daterange}&attributes_to_show=Access_Method"
                    elif report_id not in official_reports:#most likely a custom report
                        log_error(f'INFO: {provider_name} offers a custom report called {report_id} but this harvester does not support those yet.\n')
                        continue # go on to the next report for this provider
                    else:
                        get_report_url_final = get_report_url_daterange   ### we don't change attributes or filters on standard views

                    # Add the report URL to the provider's entry
                    provider_info['Report_URLS'][report_id] = get_report_url_final
                    #Also request the "_EX" versions for the sqlite database
                    if report_id in ("IR","TR","DR","PR"):
                        provider_info['Report_URLS'][extra_report_id] = get_report_url_final_extra

                # Store the provider information in the main dictionary
                data_dict[provider_name] = provider_info  # Add provider_info dict  directly to the data_dict
            else:
                log_error(f'ERROR: The response to the url {report_json_url} is not the expected supported reports list\n')
                if isinstance(report_json, dict):
                    if report_json.get("Code", None):
                        log_error(f'ERROR: A COUNTER Exception code was provided: {report_json.get("Code")}:\nMessage: {report_json.get("Message","(None provided)")}\n')
                continue
        # these are all raised from get_json_data
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for provider '{provider_name}': {http_err}\nSee error log for details")
            trace_details=traceback.format_exc()
            log_error(f"ERROR: HTTP error occurred for provider '{provider_name}': {http_err}\n{trace_details}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error occurred while requesting data from provider '{provider_name}': {req_err}\nSee error log for details")
            trace_details=traceback.format_exc()
            log_error(f"ERROR: Error occurred while requesting data from provider '{provider_name}': {req_err}\n{trace_details}")
        except Exception as e:
            trace_details=traceback.format_exc()
            log_error(f"ERROR: Unexpected error occurred for {provider_name}: {type(e).__name__}: {str(e)}\n{trace_details}")
    if len(data_dict)> 0:
        return data_dict
    else:
        return None
