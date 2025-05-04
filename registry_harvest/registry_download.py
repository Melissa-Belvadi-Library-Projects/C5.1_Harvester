#####  COUNTER Registry List

import requests
from pathlib import Path
import os.path
import logging
from datetime import datetime
import csv
import json
import sys

UA = 'Mozilla/5.0'
SERVICE1 = 'COP'
base_URL = 'https://registry.countermetrics.org/api/v1/platform/'
myheaders = {'User-Agent': UA}

today = datetime.now()
today_string = datetime.strftime(today, "%Y-%m-%d")

HEADER_MAPPING = {
    "vname": "Name",
    "url": "Base_URL",
    "customer_id_info": "Customer_ID",
    "requestor_id_info": "Requestor_ID",
    "api_key_info": "API_Key",
    "platform_specific_info": "Platform",
    "services_string": "Version",
    "request_volume_limits_info": "Delay",
    "retry_info": "Retry",
    "contact_info": "Support_Contact",
    "credentials_auto_expire_info": "Credentials_Expire",
    "customizations_info": "Customizations",
    "host_types": "Host_Types",
    "website": "Website",
    "notifications_url": "Notifications_URL",
    "data_host_name": "Usage_Data_Host",
    "data_host_contact": "Usage_Data_Host_Contact",
    "data_host_website": "Usage_Data_Host_Website",
    "data_host_url": "Usage_Data_Host_URL"
}

COLUMN_ORDER = ["Name", "Base_URL", "Customer_ID", "Requestor_ID","API_Key","Platform","Version","Delay","Retry","Support_Contact","Credentials_Expire","Customizations", "Host_Types","Website", "Notifications_URL", "Usage_Data_Host","Usage_Data_Host_Contact", "Usage_Data_Host_Website", "Usage_Data_Host_URL"]

# PVD expects the dict for a single vendor from the list of vendor dicts
## which was the expected response from the main API call to https://registry.countermetrics.org/api/v1/platform/?format=api
def process_vendor_data(vendor_data, output_file):
    # VOV creates a dict for all of the column/values for this vendor for the tsv line
    v_list_one = vlist_one_vendor(vendor_data)
    if not v_list_one:
        return
    with open(output_file, mode='a', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        for key, value in v_list_one.items():
            # Create a row based on the desired column order
            row = []
            for col in COLUMN_ORDER:
                # Get the original key corresponding to this column header
                original_key = get_original_key_from_label(col, HEADER_MAPPING)
                row.append(v_list_one.get(original_key, ""))  # Default to "" if key is missing
            # Write the row for this vendor
        writer.writerow(row)

def get_original_key_from_label(label, header_mapping):
    for key, mapped_label in header_mapping.items():
        if mapped_label == label:
            return key
    return label  # If no mapping, return the label itself



def flatten_list(data_list):
    results = []
    for entry in data_list:
        # Extract data from each dictionary entry
        formatted_entry = ", ".join(
        f"{key}={value}" for key, value in entry.items() if value  # Skip if the value is empty/None
        )
        results.append(formatted_entry)
    return "; ".join(results)

def flatten_dict(contact):
    flattened = []
    # Iterate over the dictionary to build formatted key-value pairs
    for key, value in contact.items():
        if value:  # Check if the value is not empty
            flattened.append(f"{key.capitalize()}={value}")
    # Join the key-value pairs with a comma
    return ", ".join(flattened)

def get_usage_data_host_detail(v_list,dh_url):
    v_list["data_host_url"] = dh_url
    dh = requests.get(dh_url, headers=myheaders) #get the registry record for that usage data host
    dh_dict=dh.json()
    if dh_dict.get("contact"):
        v_list["data_host_contact"] = flatten_dict(dh_dict.get("contact"))
    if dh_dict.get("name"):
        v_list["data_host_name"] = dh_dict.get("name", "")
    if dh_dict.get("abbrev"):
        v_list["data_host_abbrev"] = dh_dict.get("abbrev", "")
    if dh_dict.get("website"):
        v_list["data_host_website"] = dh_dict.get("website", "")
    return v_list

def get_sushi_detail(v_list, detail_url):
    r=requests.get(detail_url, headers=myheaders)
    get_sushi_dict=r.json()
    for key, value  in get_sushi_dict.items():
        if key == "last_audit" and isinstance(value,dict):
            v_list[key] = flatten_dict(value)
        elif not isinstance(value, bool):
            v_list[key] = str(value).replace("\r\n", " ")
        else:
            v_list[key] = value
        if key == "data_host": # url to registry entry for the usage data host eg atypon, scholarlyiq etc.
            dh_url = value
            get_usage_data_host_detail(v_list, dh_url)
    if v_list["services_string"] == None:
        v_list["services_string"]="No 5.1 SUSHI services"
        return None
    if v_list.get("requestor_id_required"):
        v_list["requestor_id_info"] = f'Required: {v_list["requestor_id_info"].replace("\r\n", " ")}'
    else:
        v_list["requestor_id_info"] = "Not required"
    if v_list.get("api_key_required"):
       v_list["api_key_info"] = f'Required: {v_list["api_key_info"].replace("\r\n", " ")}'
    else:
        v_list["api_key_info"] = "Not required"
    if v_list.get("platform_attr_required"):
        v_list["platform_attr_info"] = f'Required: {v_list["platform_specific_info"].replace("\r\n", " ")}'
    else:
        v_list["platform_attr_info"] = "Not required"
    if v_list.get("credentials_auto_expire"):
        v_list["credentials_auto_expire_info"] = f'Credentials Auto Expire: {v_list["credentials_auto_expire_info"].replace("\r\n", " ")}'
    else:
        v_list["credentials_auto_expire_info"] = "Credentials do not auto expire"
    if v_list.get("request_volume_limits_applied"):
        v_list["request_volume_limits_info"] = f'Volume limits apply: {v_list["request_volume_limits_info"].replace("\r\n", " ")}'
    else:
        v_list["request_volume_limits_info"] = "No volume limits"
    if v_list.get("customizations_in_place"):
        v_list["customizations_info"] = f'Customizations: {v_list["customizations_info"].replace("\r\n", " ")}'
    else:
        v_list["customizations_info"] = "No customizations"
    v_list["retry_info"] = "Queuing reports unknown"
    keys_to_delete = [key for key, value in v_list.items() if not value or (isinstance(value, str) and not value.strip())]
    for key in keys_to_delete:
        del v_list[key]
    return(v_list)


def vlist_one_vendor(vendor_dict):
    v_list = {}
    v_list["vname"] = vendor_dict.get('name','')
    #v_list["vid"] = vendor_dict.get('id', '')
    #v_list["abbrev"] = vendor_dict.get('abbrev', '')
    #v_list["content_provider_name"] = vendor_dict.get('content_provider_name','')
    v_list["host_types"] = flatten_list(vendor_dict.get('host_types','')).replace("name=","")
    v_list["website"] = vendor_dict.get('website', '')
    #v_list["audited"] = vendor_dict.get('audited', False)
    v_list["contact_info"] = ""
    contact = vendor_dict.get("contact",'')
    if contact and isinstance(contact, dict):
        v_list["contact_info"] = flatten_dict(contact)
    v_list["services_string"] = None
    sushiserv = vendor_dict.get("sushi_services",None)
    if not sushiserv or len(sushiserv) == 0:
        return None
    if sushiserv and isinstance(sushiserv, list):
        for block in sushiserv:
            if block["counter_release"] == "5.1":
                detail_url = block["url"]
                v_list["services_string"] = "5.1"
                get_sushi_detail(v_list, detail_url) #v_list updated in function
                break
    if not v_list.get("services_string"):
        return None
    return v_list


if __name__ == "__main__":
    try:
        recordsfolder = Path('.')
        os.chdir(recordsfolder)
    except:
        recordsfolder = Path('.')

    outfile = f'registry-entries-{today_string}.tsv'
    loggerfile = f'registry-entries-log-{today_string}.txt'
    infologger = logging.getLogger()
    infologger.setLevel(logging.ERROR)  # DEBUG, WARNING, ERROR -  should be upper-case here but lower case when used
    infohandler = logging.FileHandler(loggerfile, 'w', 'utf-8')  # or whatever
    infoformatter = logging.Formatter('%(message)s')  # or whatever
    infohandler.setFormatter(infoformatter)  # Pass handler as a parameter, not assign
    infologger.addHandler(infohandler)

    ### write the tsv column header line, hardcoded as COLUMN_ORDER
    with open(outfile, 'w', encoding='utf-8', errors="ignore") as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        writer.writerow(COLUMN_ORDER)

    print(f'Retrieving all registry data, please wait, this can take a few minutes...')
    vendor_list=requests.get(base_URL, headers=myheaders)
    #Vendor list should be a list of dicts, one dict per platform (usually a company)
    if vendor_list.status_code == 200:
        try:
            vendor_list = vendor_list.json()
            if isinstance(vendor_list, list) and all(isinstance(item, dict) for item in vendor_list):
                for vendor_data in vendor_list:
                    print(f'Processing vendor: {vendor_data.get("name")}\n')
                    process_vendor_data(vendor_data, outfile)
            else:
                print("Error: JSON response is not a list of dictionaries.")
                sys.exit()
        except ValueError:
            print("Error: Response is not valid JSON.")
            print(vendor_list.content)
    else:
        print(f"HTTP Error: {vendor_list.status_code} - {vendor_list.reason}")
        print(vendor_list.content)  # Debug content in case of failure
        sys.exit()
    print(f"DONE. COUNTER Registry entries as tab delimited file: {outfile}\n")
