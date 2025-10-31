#
import tsv_utils
from tsv_utils import IR_A1_list, IR_M1_list, IR_EX_list, IR_list
from logger import log_error
from pprint import pformat
import json
import re
import inspect

#    log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")

def process_authors(author_list): # Authors is a list of dicts where each dict is a person with key "Name" and possibly two additional keys: ISNI and ORCID
    # example of input: author_list=[{'Name': 'Richard E. Zinbarg'}, {'Name': 'Alexander L. Williams'}, {'Name': 'Susan Mineka'}]
    if not author_list:
        return None
    if not isinstance(author_list, list):
        return None
    output_list_string = ''
    for person in author_list:
        if isinstance(person, dict):
            name = person.get('Name','')
            isni = person.get('ISNI', '')
            orcid = person.get('ORCID', '')
            output_list_string += name+","+isni+","+orcid+"; "
        else:
            output_list_string = str(person)
            return output_list_string
    output_list_string = clean_string(output_list_string)
    return output_list_string

def clean_string(text):   # Replace any double commas with a single comma and Remove semicolon at the end if present
    while ",," in text: # need loop in case there are 3 or more
        text = text.replace(",,", ",")
    text=text.replace(",; ", "; ")
    if text.endswith("; "):
        text = text[:-2]
    if text.endswith(";"):
        text = text[:-1]
    if text.endswith(","):
        text = text[:-1]
    return text

def clean_text(text):
    """Decode unicode escape sequences and remove HTML tags from a string."""
    if not text:
        return text

    # The 'unicode_escape' codec is designed specifically for this.
    # It finds sequences like \u00e9 and converts them to the actual character.
    # We wrap this in a try/except because it can fail on malformed sequences.
    try:
        if '\\u' in text:
            # First, encode to latin-1 to preserve existing bytes, then decode with unicode_escape.
            text = text.encode('latin-1', 'backslashreplace').decode('unicode_escape')
    except Exception:
        # If decoding fails, it's safer to leave the original text as is
        # rather than having the function crash.
        pass

    # --- HTML tag removal
    text = re.sub(r'<[^>]+>', '', text)

    return text


def process_publisher_id(publisher_dict):
    if not isinstance(publisher_dict,dict):
        return str(publisher_dict)
    else:
        if not isinstance(publisher_dict.get("Proprietary",None),list):
            return ""
        pub_string = str(publisher_dict.get("Proprietary",None)[0])
        return pub_string

def process_parent_item_id(data_to_insert, item_id_dict):
    if not item_id_dict:
        for loop in ["DOI", "ISBN", "Online_ISSN", "Print_ISSN", "Proprietary", "URI"]:
            data_to_insert[f"Parent_{loop}"] = ''
        return None
    for key, value in item_id_dict.items():
        data_to_insert[f"Parent_{key}"] = value
    return None # the work is being done in data_to_insert not a returned value

def process_items_item_id(data_to_insert, item_id_dict):
    if not item_id_dict:
        for loop in ["DOI", "ISBN", "Online_ISSN", "Print_ISSN", "Proprietary", "URI"]:
            if loop == "Proprietary":
                data_to_insert["Proprietary_ID"] = ''
            else:
                data_to_insert[loop] = ''
        return None
    for key, value in item_id_dict.items():
        if key == "Proprietary":
            data_to_insert["Proprietary_ID"] = value
        else:
            data_to_insert[key] = value
    return None # the work is being done in data_to_insert not a returned value

def process_m1_items_item_id(data_to_insert, item_id_dict):
    if not item_id_dict:
        for loop in ["DOI", "Proprietary", "URI"]:
            if loop == "Proprietary":
                data_to_insert["Proprietary_ID"] = ''
            else:
                data_to_insert[loop] = ''
        return None
    if not isinstance(item_id_dict, dict):
        log_error(f'ERROR: Item_id_dict is not a dict but is a {type(item_id_dict)}\n')
        return None
    for key, value in item_id_dict.items():
        if key == "Proprietary":
            data_to_insert["Proprietary_ID"] = value
        else:
            data_to_insert[key] = value
    return None # the work is being done in data_to_insert not a returned value

def process_ir_attribute_performance(item,header_date_list): # parameter should be a list
    attribute_performance = item.copy()
    performance_data = None
    rows_to_insert = []
    if not attribute_performance or not isinstance(attribute_performance, list):
        return None
    if not header_date_list or not isinstance(header_date_list,list):
        log_error(f'ERROR: header_date_list does not have the needed list: {header_date_list}\n')
        return None
    for entry in attribute_performance:
        attr_base_data = {key: entry[key] for key in entry if key != 'Performance'} #values like Access_Type
        if 'Proprietary_ID' in attr_base_data:
            attr_base_data['Proprietary'] = attr_base_data.pop('Proprietary_ID')
        performance_data = entry.get('Performance', {}) # Performance is a dict of dicts, with key=metric type and value is a dict with key year-month and value usage count
        # like this example: {'Performance': {'Total_Item_Requests': {'2025-02': 1, '2024-12': 2}, 'Unique_Item_Requests': {'2025-02': 1}}
        for metric_type, metrics in performance_data.items():
            rep_total = 0
            row_data = {
                **attr_base_data,  # Merge the base data
                'Metric_Type': metric_type,
                }
            for year_month, metric_value in metrics.items():# calculate the reporting period total for each metric type within an item
                rep_total+= metric_value
                row_data['Reporting_Period_Total'] =  rep_total
            for year_month, metric_value in metrics.items():
                row_data[year_month] = metric_value
            rows_to_insert.append(row_data)
    for row in rows_to_insert:  # have to fill all of the empty values in the usage cols with a literal 0
        for yrmonth_col in header_date_list:
            if yrmonth_col not in row or not isinstance(row[yrmonth_col],int):
                row[yrmonth_col] = "0"
    return rows_to_insert  # Return the list of dictionaries

def ir_a1_extract_metrics_and_dates(report_items):#IR_A1/IR_M1 metrics and date columns are different from other reports
    metric_type_list = set()
    usage_dates_list = set()
    for report_item in report_items:
        for item in report_item.get("Items", []):
            for performance_data in item.get("Attribute_Performance", []):
                performance = performance_data.get("Performance", {})
                for metric_type, dates in performance.items():
                    metric_type_list.add(metric_type)
                    usage_dates_list.update(dates.keys())
    return sorted(metric_type_list), sorted(usage_dates_list)

# For IR_A1, Include_Parent_Details must be True and is not included in the report attributes in the header; header_date_range is the yyyy-mm parsed from the report header begin/end
def get_ir_a1_data(report_items,header_date_list):
    data_rows_to_insert = []

    metric_type_list, usage_dates_list = ir_a1_extract_metrics_and_dates(report_items)
    try:
        for ri_index, parent_item in enumerate(report_items):  # Report_items is a list of dicts, where each dict has the parent items and a list of "items", each of which is a dict
            parent_data_to_insert = {}
            row = []
            row = [None] * len(IR_A1_list)  # Prepopulate/clear out the row with placeholders
            try:
                Parent_Title = parent_item.get("Title", []) if parent_item.get("Title",None) else ''
                Parent_Title = clean_text(Parent_Title)
                parent_data_to_insert["Parent_Title"] = Parent_Title
                parent_data_to_insert["Parent_Article_Version"] = parent_item.get("Article_Version","")  if parent_item.get("Article_Version",None) else ''
                Parent_Authors = process_authors(parent_item.get("Authors", None)) if parent_item.get("Authors") else ''
                if Parent_Authors:
                    parent_data_to_insert["Parent_Authors"] = Parent_Authors
                else:
                    parent_data_to_insert["Parent_Authors"] = ''
                process_parent_item_id(parent_data_to_insert, parent_item.get('Item_ID', None))
                items = parent_item.get("Items", [])
                if not isinstance(items, list):
                    log_error(f'ERROR: there are no items in this report\n')
                    return None
            except Exception as f:
                log_error(f'ERROR: Exception in parent handling block: {str(f)}\n')
            for it_index, item in enumerate(parent_item["Items"]):  #each "item" is the article-level item and a dict
                #item_fields_list = ["Item", "Publisher", "Publisher_ID", "Authors", "Platform", "Publication_Date",  "Article_Version", "DOI", "Proprietary","Print_ISSN", "Online_ISSN", "ISBN", "URI"]
                item_data_to_insert = {}
                for item_key, item_value in item.items():
                    rows_to_insert = {} # column data at the performance level, reset here then save it all at the end of the item.items for loop
                    try:
                        if item_key == "Item":
                            item_data_to_insert["Item"] = clean_text(item_value)
                        elif item_key == "Authors": # Authors should be a list
                            if item_value and isinstance(item_value,list):
                                item_data_to_insert["Authors"] = process_authors(item_value)
                            else:
                                item_data_to_insert["Authors"] = ''
                        elif item_key == "Publisher_ID": # this is a dict
                            if item_value and isinstance(item_value,dict):
                                item_data_to_insert["Publisher_ID"] = process_publisher_id(item_value)
                            else:
                                item_data_to_insert["Publisher_ID"] = ''
                        elif item_key == "Item_ID":
                            if item_value and isinstance(item_value,dict):
                                process_items_item_id(item_data_to_insert, item_value)
                        elif item_key == "Attribute_Performance":  # the actual usage data that determines the rows is within here; A-P is a list
                            if not item_value:
                                log_error(f'ERROR: There is no Attribute Performance for this item - this should never happen\n')
                            else:
                                rows_to_insert = process_ir_attribute_performance(item_value,header_date_list)
                        elif item_value: # Some other key/value, expecting simple strings: Article_Version, Platform, Publisher
                            item_data_to_insert[item_key] = clean_text(item_value)
                        elif item_key == "Article_Version" and item_value == '':
                            continue #Article Version should never be empty, but if we're here, it is empty
                        else:
                            log_error(f'ERROR-detail: Unexpected key={item_key}, value={item_value}\n')
                    except Exception as h: # the try for the individual articles
                        log_error(f'ERROR: Exception in item level items: {str(h)}; item_key = {item_key}; item_value={item_value}\n')
                for row in rows_to_insert: # save all of the data in rows to data_rows_to_insert
                    # Create a new dictionary by merging data_to_insert and the current row
                    combined_dict = {**parent_data_to_insert, **item_data_to_insert, **row}
                    data_rows_to_insert.append(combined_dict)

    except Exception as e: # the parent level item
        log_error(f"ERROR: Exception occurred in get_ir_a1: outside of the main FOR loop - {str(e)}")
        raise  # Re-raise the error for further debugging
    return data_rows_to_insert

def get_ir_m1_data(report_items,header_date_list):# For IR_M1, there are no parents; report_items is a list of dicts, header_date_range is the yyyy-mm parsed from the report header begin/end
    #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
    data_to_insert = {}
    data_rows_to_insert = []
    # Generate rows
    rows_to_insert = []
    metric_type_list, usage_dates_list = ir_a1_extract_metrics_and_dates(report_items)
    for rep_loop in report_items:
        for it_index, item in enumerate(rep_loop["Items"]):  #rep_loop is a dict, and rep_loop[Items] is a list
            # item is  a dict, its keys include Item, Item_ID, Attr_Per, etc.
            row = []
            row = [None] * len(IR_M1_list)  # Prepopulate/clear out the row with placeholders
            try:
                for item_key, item_value in item.items(): # parse out the values in dict item
                    #log_error(f'The keys in item are: {item.keys()}\n')
                    if item_key =="Item":
                        data_to_insert["Item"] = clean_text(item_value)
                        continue
                    if item_key == "Attribute_Performance":  # the actual usage data that determines the rows is within here; A-P is a list
                        if not item_value:
                            log_error(f'ERROR: There is no Attribute Performance for this item - this should never happen\n')
                        else:
                            rows_to_insert = process_ir_attribute_performance(item_value,header_date_list)
                        continue
                    if item_key == "Publisher_ID": # this is a dict
                        if item_value and isinstance(item_value,dict):
                            data_to_insert["Publisher_ID"] = process_publisher_id(item_value)
                        else:
                            data_to_insert["Publisher_ID"] = ''
                        continue
                    if item_key == "Item_ID":
                        if item_value and isinstance(item_value,dict):
                            process_m1_items_item_id(data_to_insert, item_value) # This populates several key-values in data_to_insert
                        continue
                    if item_key in ("Publisher", "Platform"): # simple strings
                        if item_value:
                            data_to_insert[item_key] = clean_text(item_value)
                        else:
                            data_to_insert[item_key] = ''
                        continue
                    if item_key == "Article_Version" and item_value == '':
                        continue #Article Version should never be empty, but if we're here, it is empty
                    if item_value: # Some other key/value
                        #data_to_insert[item_key] = str(item_value)
                        log_error(f'ERROR-detail: unexpected extra key. check COP if key should be added: items {item_key} = {item_value}\n')
                        continue
            except Exception as h: # the try for the individual articles
                log_error(f'ERROR: Exception h: {str(h)}; item_key = {item_key}; item_value={item_value}\n')
            # Iterate through each row dictionary in rows_to_insert
            for row in rows_to_insert:
                # Create a new dictionary by merging data_to_insert and the current row
                combined_dict = {**data_to_insert, **row}
                data_rows_to_insert.append(combined_dict)
    return data_rows_to_insert

def get_ir_data(report_items,header_date_list):# For IR, there are no parents; report_items is a list of dicts, header_date_range is the yyyy-mm parsed from the report header begin/end
    #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}") #DEBUG
    data_to_insert = {}
    data_rows_to_insert = []
    # Generate rows
    rows_to_insert = []
    metric_type_list, usage_dates_list = ir_a1_extract_metrics_and_dates(report_items)
    for rep_loop in report_items:
        for it_index, item in enumerate(rep_loop["Items"]):  #rep_loop is a dict, and rep_loop[Items] is a list
            # item is  a dict, its keys include Item, Item_ID, Attr_Per, etc.
            row = []
            row = [None] * len(IR_list)  # Prepopulate/clear out the row with placeholders
            try:
                for item_key, item_value in item.items(): # parse out the values in dict item
                    #log_error(f'The keys in item are: {item.keys()}\n')
                    if item_key =="Item":
                        data_to_insert["Item"] = clean_text(item_value)
                        continue
                    if item_key == "Attribute_Performance":  # the actual usage data that determines the rows is within here; A-P is a list
                        if not item_value:
                            log_error(f'ERROR: There is no Attribute Performance for this item - this should never happen\n')
                        else:
                            rows_to_insert = process_ir_attribute_performance(item_value,header_date_list)
                        continue
                    if item_key == "Publisher_ID": # this is a dict
                        if item_value and isinstance(item_value,dict):
                            data_to_insert["Publisher_ID"] = process_publisher_id(item_value)
                        else:
                            data_to_insert["Publisher_ID"] = ''
                        continue
                    if item_key == "Item_ID":
                        if item_value and isinstance(item_value,dict):
                            process_m1_items_item_id(data_to_insert, item_value) # This populates several key-values in data_to_insert
                        continue
                    if item_key in ("Publisher", "Platform"): # simple strings
                        if item_value:
                            data_to_insert[item_key] = clean_text(item_value)
                        else:
                            data_to_insert[item_key] = ''
                        continue
                    if item_key == "Article_Version" and item_value == '':
                        continue #Article Version should never be empty, but if we're here, it is empty
                    if item_value: # Some other key/value
                        #data_to_insert[item_key] = str(item_value)
                        log_error(f'ERROR-detail: unexpected extra key. check COP if key should be added: items {item_key} = {item_value}\n')
                        continue
            except Exception as h: # the try for the individual articles
                log_error(f'ERROR: Exception h: {str(h)}; item_key = {item_key}; item_value={item_value}\n')
            # Iterate through each row dictionary in rows_to_insert
            for row in rows_to_insert:
                # Create a new dictionary by merging data_to_insert and the current row
                combined_dict = {**data_to_insert, **row}
                data_rows_to_insert.append(combined_dict)
    return data_rows_to_insert

def get_ir_ex_data(report_items,header_date_list): #IR_EX needs the parent items so is more like IR_A1, but other things needed too
    '''
https://cop5.countermetrics.org/en/5.1.0.1/04-reports/04-item-reports.html  Table 4.4.2 everything that IR has M or C that IR_A1 does not have
Parent_Publication_Date - string
Parent_Data_Type - string
Parent_ISBN in Parent Item_ID
YOP string in Attribute Performance in the Items
Access_Method - string in Attribute Performance in the Items
ISBN - string in Item_ID in the Items
    '''
    data_rows_to_insert = []
    metric_type_list, usage_dates_list = ir_a1_extract_metrics_and_dates(report_items)
    try:
        for ri_index, parent_item in enumerate(report_items):  # Report_items is a list of dicts, where each dict has the parent items and a list of "items", each of which is a dict
            parent_data_to_insert = {}
            row = []
            row = [None] * len(IR_EX_list)  # Prepopulate/clear out the row with placeholders
            try:
                Parent_Title = parent_item.get("Title", []) if parent_item.get("Title",None) else ''
                Parent_Title = clean_text(Parent_Title)
                parent_data_to_insert["Parent_Title"] = Parent_Title
                parent_data_to_insert["Parent_Article_Version"] = parent_item.get("Article_Version","")  if parent_item.get("Article_Version",None) else ''
                Parent_Authors = process_authors(parent_item.get("Authors", None)) if parent_item.get("Authors") else ''
                if Parent_Authors:
                    parent_data_to_insert["Parent_Authors"] = Parent_Authors
                else:
                    parent_data_to_insert["Parent_Authors"] = ''
                process_parent_item_id(parent_data_to_insert, parent_item.get('Item_ID', None))
                items = parent_item.get("Items", [])
                if not isinstance(items, list):
                    log_error(f'ERROR: there are no items in this report\n')
                    return None
            except Exception as f:
                log_error(f'ERROR: Exception in parent handling block: {str(f)}\n')
            for it_index, item in enumerate(parent_item["Items"]):  #each "item" is the article-level item and a dict
                #item_fields_list = ["Item", "Publisher", "Publisher_ID", "Authors", "Platform", "Publication_Date",  "Article_Version", "DOI", "Proprietary","Print_ISSN", "Online_ISSN", "ISBN", "URI"]
                item_data_to_insert = {}
                for item_key, item_value in item.items():
                    rows_to_insert = {} # column data at the performance level, reset here then save it all at the end of the item.items for loop
                    try:
                        if item_key == "Item":
                            item_data_to_insert["Item"] = clean_text(item_value)
                        elif item_key == "Authors": # Authors should be a list
                            if item_value and isinstance(item_value,list):
                                item_data_to_insert["Authors"] = process_authors(item_value)
                            else:
                                item_data_to_insert["Authors"] = ''
                        elif item_key == "Publisher_ID": # this is a dict
                            if item_value and isinstance(item_value,dict):
                                item_data_to_insert["Publisher_ID"] = process_publisher_id(item_value)
                            else:
                                item_data_to_insert["Publisher_ID"] = ''
                        elif item_key == "Item_ID":
                            if item_value and isinstance(item_value,dict):
                                process_items_item_id(item_data_to_insert, item_value)
                        elif item_key == "Attribute_Performance":  # the actual usage data that determines the rows is within here; A-P is a list
                            if not item_value:
                                log_error(f'ERROR: There is no Attribute Performance for this item - this should never happen\n')
                            else:
                                rows_to_insert = process_ir_attribute_performance(item_value,header_date_list)
                        elif item_key == "Article_Version" and item_value == '':
                            continue #Article Version should never be empty, but if we're here, it is empty
                        elif item_value: # Some other key/value, expecting simple strings: Article_Version, Platform, Publisher
                            item_data_to_insert[item_key] = clean_text(item_value)
                        else:
                            log_error(f'ERROR-detail: Unexpected key={item_key}, value={item_value}\n')
                    except Exception as h: # the try for the individual articles
                        log_error(f'ERROR: Exception in item level items: {str(h)}; item_key = {item_key}; item_value={item_value}\n')
                for row in rows_to_insert: # save all of the data in rows to data_rows_to_insert
                    # Create a new dictionary by merging data_to_insert and the current row
                    combined_dict = {**parent_data_to_insert, **item_data_to_insert, **row}
                    data_rows_to_insert.append(combined_dict)

    except Exception as e: # the parent level item
        log_error(f"ERROR: Exception occurred in get_ir_ex: outside of the main FOR loop - {str(e)}")
        raise  # Re-raise the error for further debugging
    return data_rows_to_insert

