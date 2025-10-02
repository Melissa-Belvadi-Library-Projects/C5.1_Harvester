### fetch_json - gets the /reports and creates the URLs for all supported master reports (TR,DR,PR,IR)
import json
import time
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import brotli
from logger import log_error
import traceback
from current_config import error_log_file, default_begin
from tsv_utils import default_metric_types, official_reports


def is_json(ij_dict):
    try:
        json.loads(ij_dict)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def validate_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m")
        return True
    except ValueError:
        return False


def check_dates(provider_name, begin_date, end_date, first_month, last_month):
    begin_date_dt = datetime.strptime(begin_date, "%Y-%m")
    first_month_dt = datetime.strptime(first_month, "%Y-%m")
    last_month_dt = datetime.strptime(last_month, "%Y-%m")
    end_date_dt = datetime.strptime(end_date, "%Y-%m")

    if begin_date_dt < first_month_dt:
        print(f"WARNING: data from {provider_name} will not start until {first_month}")
        log_error(f"WARNING: data from {provider_name} will not start until {first_month}")
        begin_date = first_month

    if end_date_dt > last_month_dt:
        print(f"WARNING: data from {provider_name} only available through {last_month}")
        log_error(f"WARNING: data from {provider_name} only available through {last_month}")
        end_date = last_month

    return begin_date, end_date


def get_dd(date_string, position):
    try:
        parts = date_string.split("-")
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2]) if len(parts) == 3 else 1
        date_object = datetime(year, month, day)

        if not (1 <= month <= 12):
            raise ValueError("Invalid month. Month must be between 1 and 12.")
            return None

        if position == "begin":
            day = 1
            date_object = datetime(year, month, day)
        elif position == "end":
            date_object = datetime(year, month, 1) + timedelta(days=31)
            date_object = date_object.replace(day=1) - timedelta(days=1)
        else:
            raise ValueError("Position must be 'begin' or 'end'.")

        return date_object.strftime("%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"ERROR processing input: {e}")


def get_json_data(url, provider_info):
    report_json = {}
    provider_name = provider_info.get('Name', '')
    sleep_delay = provider_info.get('Delay', 0)
    retry_needed = provider_info.get('Retry', 0)

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
        max_attempts = 3
        attempts = 0
        fatal_error = 0
        http_desc = None

        while attempts < max_attempts:
            attempts += 1
            if sleep_delay:
                time.sleep(sleep_delay)
            if fatal_error:
                log_error(f'ERROR: Got a fatal HTTP error - need to give up on this provider\n')
                break

            try:
                response = requests.get(url, headers=headers, timeout=(10, 30))

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
                    log_error(f'ERROR: fatal error: code={response.status_code}\n')
                    return -1
                elif response.status_code == 401:
                    http_desc = "requestor_id or api_key wrong!"
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    return -1
                elif response.status_code == 403:
                    http_desc = "Unauthorized requestor_id or customer_id. Check your request parameters."
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    return -1
                elif response.status_code == 404:
                    http_desc = "Resource not found! Check if the base_url is correct."
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    return -1
                elif response.status_code == 429:
                    http_desc = f"Too many requests too fast. {provider_name} needs a delay: {response.text}"
                    if sleep_delay and (isinstance(sleep_delay, int) or isinstance(sleep_delay, float)):
                        time.sleep(sleep_delay)
                    else:
                        sleep_delay = 3
                        time.sleep(sleep_delay)
                    fatal_error = 0
                    continue
                elif response.status_code == 500:
                    http_desc = "Server error! The API might be down or experiencing issues."
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    return -1
                elif response.status_code == 503:
                    http_desc = f"Service too busy or request is queued, try again soon: {url}\n{response.text}"
                    log_error(f'ERROR: {http_desc}\n')
                    if not sleep_delay:
                        sleep_delay = 5
                    time.sleep(sleep_delay + 5)
                    fatal_error = 0
                    continue
                else:
                    http_desc = f"Unexpected status code: {response.status_code}\nResponse body: {response.text}"
                    log_error(f'ERROR: {http_desc}\n')
                    fatal_error = 1
                    return -1

            except requests.exceptions.Timeout:
                log_error(f"ERROR: The URL request timed out for {provider_name}\n{url}")
                return None
            except requests.exceptions.HTTPError as err:
                log_error(f"ERROR: HTTP Error: {err}")
                print(f"HTTP Error trying to get {url} for {provider_name}. See error log for details.")
                return -1
            except requests.exceptions.ConnectionError as e:
                log_error(f"ERROR: Network error occurred: {e}")
                return -1
            except requests.exceptions.TooManyRedirects as e:
                log_error(f"ERROR: Too many redirects: {e}")
                return -1
            except requests.exceptions.RequestException as e:
                log_error(f"ERROR: An error occurred: {e}")
                return -1
            except Exception as e:
                log_error(f'ERROR: An error occurred within the while try: {e}\n')
                return -1

        report_json = response.json()

        if response.headers.get('Content-Encoding') == 'br':
            decoded_content = brotli.decompress(response.content)
            report_json = json.loads(decoded_content)

        if (not isinstance(report_json, dict)) and (not isinstance(report_json, list)):
            log_error(f"ERROR: Failed to get a valid response after 3 attempts, url={url}")
            return -1

        return report_json

    except Exception as e2:
        log_error(f'ERROR: An error occurred within get_json_data: {e2}\n')
        return -1


def timedelay(provider_name, thisdelay):
    if thisdelay is None:
        delaylength = 2
    elif thisdelay == '':
        delaylength = 2
    elif isinstance(thisdelay, int):
        delaylength = thisdelay
    else:
        delaylength = 2
        log_error(f"ERROR: 'Delay' for {provider_name} is unexpected, using 2 seconds; value: {thisdelay}")
    return delaylength


def fetch_json(providers, begin_date, end_date, report_type_list):
    """
    Fetch provider API information with given parameters.

    Args:
        providers: List of provider dictionaries
        begin_date: Start date in YYYY-MM format
        end_date: End date in YYYY-MM format
        report_type_list: List of report types like ['DR', 'TR', 'PR', 'IR']

    Returns:
        Dictionary of provider data or None on failure
    """
    print(f"\nBegin Date: {begin_date}, End Date: {end_date}\n")

    data_dict = {}

    if not report_type_list:
        print("You did not select any report types.\n")
        return None

    for provider in providers:
        provider_info = {}
        checked_date = 0
        get_report_url_credentials = ''
        get_report_url_final = ''
        get_report_url_daterange = ''
        credentials = ''
        b = ''
        e = ''

        provider_name = provider.get('Name')
        base_url = provider.get('Base_URL')
        customer_id = provider.get('Customer_ID')

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

        if missing_fields:
            present_info = []
            if provider_name:
                present_info.append(f"Name: {provider_name}")
            if base_url:
                present_info.append(f"Base_URL: {base_url}")
            if customer_id:
                present_info.append(f"Customer_ID: {customer_id}")

            print(
                f"Error: Missing mandatory fields, skipping: {', '.join(missing_fields)}. Present: {', '.join(present_info)}\n")
            continue

        requestor_id = provider.get('Requestor_ID', '')
        api_key = provider.get('API_Key', '')
        platform = provider.get('Platform', '')
        version = provider.get('Version', '5.1')
        delay = provider.get('Delay', '')
        retry = provider.get('Retry', '')
        first_month_available = provider.get('First_Month_Available', '')
        last_month_available = provider.get('Last_Month_Available', '')
        path = provider.get('Path', '')
        report_name = provider.get('Report_Name', '')
        report_description = provider.get('Report_Description', '')

        provider_info = {
            'Name': provider_name,
            'Base_URL': base_url,
            'Customer_ID': customer_id,
            'Requestor_ID': requestor_id,
            'API_Key': api_key,
            'Platform': platform,
            'Version': version,
            'Delay': delay,
            'Retry': retry,
            'Path': path,
            'First_Month_Available': first_month_available,
            'Last_Month_Available': last_month_available,
            'Report_Name': report_name,
            'Report_Description': report_description,
            'Report_URLS': {}
        }

        credentials = f"customer_id={customer_id}" if customer_id else credentials
        credentials = f"{credentials}&requestor_id={requestor_id}" if requestor_id else credentials
        credentials = f"{credentials}&api_key={api_key}" if api_key else credentials

        try:
            if not base_url.endswith("/reports/"):
                if base_url.endswith("/reports"):
                    base_url = f"{base_url}/"
                else:
                    base_url = f"{base_url.rstrip('/')}/reports/"

            report_json_url = f"{base_url[:-1]}?{credentials}&platform={platform}" if platform else f"{base_url[:-1]}?{credentials}"

            log_error(f'INFO: {provider_name}: supported reports API URL=\n{report_json_url}')
            report_json = get_json_data(report_json_url, provider_info)

            if not report_json:
                log_error(f'ERROR: get_json_data failed for {report_json_url}, skipping provider\n')
                continue
            elif report_json == -1:
                log_error(f'ERROR: Fatal error for {report_json_url}, skipping provider\n')
                continue

            if isinstance(report_json, list):
                for report in report_json:
                    if "Report_ID" not in report:
                        log_error(f"ERROR: A report from {provider_name} does not contain Report_ID\n")
                        continue

                    report_id = report.get('Report_ID')
                    if report_id not in report_type_list:
                        continue

                    if platform:
                        get_report_url_credentials = f'{base_url}{report_id.lower()}?{credentials}&platform={platform}'
                    else:
                        get_report_url_credentials = f'{base_url}{report_id.lower()}?{credentials}'

                    first_month = report.get('First_Month_Available', '')
                    if not validate_date(first_month):
                        b = begin_date

                    last_month = report.get('Last_Month_Available', '')
                    if not validate_date(last_month):
                        e = end_date

                    if validate_date(first_month) and validate_date(last_month) and not checked_date:
                        b, e = check_dates(provider_name, begin_date, end_date, first_month, last_month)
                        checked_date = 1

                    if (b > begin_date and not checked_date) and (e < end_date and not checked_date):
                        print(
                            f"WARNING: data from {provider_name} will not start until {b} and only available through {e}\n")
                        log_error(
                            f"WARNING: data from {provider_name} will not start until {b} and only available through {e}\n")
                    elif b > begin_date and not checked_date:
                        print(f"WARNING: data from {provider_name} will not start until {b}")
                        log_error(f"WARNING: data from {provider_name} will not start until {b}\n")
                    elif e < end_date and not checked_date:
                        print(f"WARNING: data from {provider_name} only available through {e}")
                        log_error(f"WARNING: data from {provider_name} only available through {e}\n")

                    if not validate_date(first_month):
                        b = begin_date
                    if not validate_date(last_month):
                        e = end_date

                    b = get_dd(b, "begin")
                    e = get_dd(e, "end")
                    provider_info['Dates'] = f"{b}-{e}"

                    get_report_url_daterange = f"{get_report_url_credentials}&begin_date={b}&end_date={e}"

                    extra_report_id = report_id + "_EX"
                    if report_id == 'IR':
                        IR_EX_attributes_to_show = "Authors|Publication_Date|Article_Version|YOP|Access_Type|Access_Method"
                        get_report_url_final_extra = f"{get_report_url_daterange}&attributes_to_show={IR_EX_attributes_to_show}&include_parent_details=True"
                        get_report_url_final = f"{get_report_url_daterange}"
                    elif report_id == 'TR':
                        get_report_url_final = f"{get_report_url_daterange}"
                        get_report_url_final_extra = f"{get_report_url_daterange}&attributes_to_show=YOP|Access_Method|Access_Type"
                    elif report_id in {'DR', 'PR'}:
                        get_report_url_final = f"{get_report_url_daterange}"
                        get_report_url_final_extra = f"{get_report_url_daterange}&attributes_to_show=Access_Method"
                    elif report_id not in official_reports:
                        log_error(
                            f'INFO: {provider_name} offers a custom report called {report_id} but this harvester does not support those yet.\n')
                        continue
                    else:
                        get_report_url_final = get_report_url_daterange

                    provider_info['Report_URLS'][report_id] = get_report_url_final

                    if report_id in ("IR", "TR", "DR", "PR"):
                        provider_info['Report_URLS'][extra_report_id] = get_report_url_final_extra

                data_dict[provider_name] = provider_info
            else:
                log_error(f'ERROR: The response to {report_json_url} is not the expected supported reports list\n')
                if isinstance(report_json, dict):
                    if report_json.get("Code", None):
                        log_error(
                            f'ERROR: COUNTER Exception code: {report_json.get("Code")}:\nMessage: {report_json.get("Message", "(None provided)")}\n')
                continue

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error for provider '{provider_name}': {http_err}\nSee error log for details")
            trace_details = traceback.format_exc()
            log_error(f"ERROR: HTTP error for provider '{provider_name}': {http_err}\n{trace_details}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error requesting data from provider '{provider_name}': {req_err}\nSee error log for details")
            trace_details = traceback.format_exc()
            log_error(f"ERROR: Error requesting data from provider '{provider_name}': {req_err}\n{trace_details}")
        except Exception as e:
            trace_details = traceback.format_exc()
            log_error(f"ERROR: Unexpected error for {provider_name}: {type(e).__name__}: {str(e)}\n{trace_details}")

    if len(data_dict) > 0:
        return data_dict
    else:
        return None