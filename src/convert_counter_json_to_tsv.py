import json
import csv
import os
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import inspect
import tsv_utils
from tsv_utils import default_metric_types, format_nested_id, format_exceptions
from current_config import tsv_dir, always_include_header_metric_types, save_empty_report
from logger import log_error
from reporting_period import reporting_period_build
from convert_ir_reports import get_ir_a1_data, get_ir_m1_data, get_ir_data, get_ir_ex_data
#import pdb; pdb.set_trace()

def extract_metric_types(report_items):
    #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
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


def date_columns(report_items):
    #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
    year_month_columns = set()  # Use a set to avoid duplicates
    # Iterate over each item in the report_items list
    for item in report_items:
        # Get the Attribute_Performance list
        attribute_performance = item.get('Attribute_Performance', [])
        # Iterate over each dict in Attribute_Performance
        for ap in attribute_performance:
            # Get the "Performance" dict
            performance = ap.get('Performance', {})
            # Iterate over metrics (key-value pairs) in the Performance dictionary
            for metric_type, date_values in performance.items():
                #print(f'date_values = {date_values}')
                # Add all the date keys (e.g., "2025-01") to the set
                year_month_columns.update(date_values.keys())
    # Return the sorted list of unique Year-Month columns
    return sorted(year_month_columns)

def generate_date_range(date_string): # from the header info, as opposed to the performance info
    #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
    try:
        # Parse the string to extract Begin_Date and End_Date
        date_parts = dict(part.split("=") for part in date_string.split("; "))
        begin_date = date_parts.get("Begin_Date")
        end_date = date_parts.get("End_Date")

        # Verify both dates exist
        if not begin_date or not end_date:
            raise ValueError("Invalid date_string format. Missing Begin_Date or End_Date.")

        # Convert these into datetime objects
        start = datetime.strptime(begin_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Generate a range of YYYY-MM values
        date_range_list = []
        current = start
        while current <= end:
            date_range_list.append(current.strftime("%Y-%m"))  # Format as YYYY-MM
            current += relativedelta(months=1)  # Increment by 1 month

        return date_range_list
    except Exception as e:
        log_error(f"ERROR: {str(e)}")
        return None

# Convert dict report_filters to proper string
# the argument should be  passed as
# report_header.get("Report_Filters", {})
def get_report_filter_string(dict):
    #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
    if dict:
        #header_data_type = str(dict.get("Data_Type", ""))
        header_data_type = "|".join(dict.get("Data_Type", [])) if isinstance(dict.get("Data_Type", []), list) else ""
        #print(f' Access_type: {dict.get('Access_Type',[])}\n')
        header_access_type = "|".join(dict.get("Access_Type", [])) if isinstance(dict.get("Access_Type", []), list) else ""
        header_access_method = "; ".join(dict.get("Access_Method", [])) if isinstance(dict.get("Access_Method", []), list) else ""
        #print(f' header_access_type: {header_access_type}')
        #print(f' header_access_method: {header_access_method}; type= {type(header_access_method)}')
        report_filter_string = ""
        if header_data_type:
            report_filter_string += "Data_Type="+header_data_type+"; "
        if header_access_type:
            report_filter_string +="Access_Type="+header_access_type+"; "
        if header_access_method:
            report_filter_string +="Access_Method="+str(header_access_method)
        report_filter_string = report_filter_string.rstrip("; ")
    else:
            report_filter_string = ''
    return report_filter_string

# Function to clean strings of `\r`
def clean_string(value):
    if isinstance(value, str):
        return value.replace("\r", "")
    return value


def get_default_metric_types(report_type):
    metric_list = default_metric_types.get(report_type,[])
    return metric_list

def ir_a1_extract_metrics_and_dates(report_items):#IR_A1/IR_M1 metrics and date columns are different from other reports
    #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
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

def convert_counter_json_to_tsv(report_type, json_file_path,provider_info):
    #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
    try:
        # Load JSON data for reading
        with open(json_file_path, "r", encoding="utf-8") as f:
            counter_data = json.load(f)
        # Extract Report_Header and Report_Items
        report_header = counter_data.get("Report_Header", {})
        if not report_header:
            print(f'ERROR:  No report header, skipping entire report\n')
            log_error(f'ERROR:  No report header, skipping entire report\n')
            return 0
        report_items = counter_data.get("Report_Items", None)
        if not report_items and not save_empty_report:
            print(f"No report items in {json_file_path}.\nReason: {report_header.get('Exceptions',[])[0].get('Message', '')}\n")
            log_error(f'ERROR: No report items in {json_file_path}. Exceptions: {report_header.get('Exceptions',[])}')
            return 0
        # Ensure tsv_dir is a string
        if not isinstance(tsv_dir, str):
            raise ValueError(f"ERROR: tsv_dir must be a string, but got {type(tsv_dir)}: {tsv_dir}")
        vendor = provider_info.get('Name', '').replace(' ','_')
        tsvsubfolder = os.path.join(tsv_dir, vendor)
        if not os.path.exists(tsv_dir):
            os.makedirs(tsv_dir)
        if not os.path.exists(tsvsubfolder):
            os.makedirs(tsvsubfolder) # tsv folder for this vendor exists
        # Ensure json_file_path is a string and compute tsv_filename
        if not isinstance(json_file_path, str):
            log_error(f'ERROR: Unable to name the tsv, problem with json filename: {json_file_path} type: {type(json_file_path)}')
            raise ValueError(f"ERROR: json_file_path must be a string, but got {type(json_file_path)}: {json_file_path}")
        
        tsv_basename = os.path.basename(json_file_path)
        tsv_filename = os.path.splitext(tsv_basename)[0] + ".tsv"
        tsv_full_path = os.path.join(tsvsubfolder, tsv_filename) # tsv_full_path includes folder/subfolder/filename

        # Retrieve the Report_ID which is the same as Report_Type except for the _EX special reports which are passed as report_type
        report_id = report_header.get("Report_ID", "")
        # The default list of metric_types by report type
        ## If the user wants them all displayed they set always_include_header_metric_types in sushiconfig to True
        ### The COUNTER standard is to suppress the list in the header if the list exactly matches the default
        ### But some users may find it helpful to see them in the report header

        # Determine the correct column order list based on the Report_ID
        column_mapping = {
            "DR": tsv_utils.DR_list,
            "DR_EX": tsv_utils.DR_EX_list,
            "DR_D1": tsv_utils.DR_D1_list,
            "DR_D2": tsv_utils.DR_D2_list,
            "PR": tsv_utils.PR_list,
            "PR_EX": tsv_utils.PR_EX_list,
            "PR_P1": tsv_utils.PR_P1_list,
            "TR": tsv_utils.TR_list,
            "TR_EX": tsv_utils.TR_EX_list,
            "TR_J1": tsv_utils.TR_J1_list,
            "TR_J2": tsv_utils.TR_J2_list,
            "TR_J3": tsv_utils.TR_J3_list,
            "TR_J4": tsv_utils.TR_J4_list,
            "TR_B1": tsv_utils.TR_B1_list,
            "TR_B2": tsv_utils.TR_B2_list,
            "TR_B3": tsv_utils.TR_B3_list,
            "IR": tsv_utils.IR_list,
            "IR_EX": tsv_utils.IR_EX_list,
            "IR_A1": tsv_utils.IR_A1_list,
            "IR_M1": tsv_utils.IR_M1_list
        }
        #column_mapping["TR_no_YOP"] = [col for col in tsv_column_orders.TR_list if col != "YOP"] ## Also produce the standard TR
        if report_items:
            column_order_list = column_mapping.get(report_type, None)
            if column_order_list is None:
                log_error(f'ERROR: There is no valid Report Type {report_type}, in {json_file_path}, skipping this report\n')
                print(f'There is no valid Report Type {report_type}, in {json_file_path}, skipping this report\n')
                raise ValueError(f"ERROR: Unexpected report_id: '{report_type}'")
                return None


                #special def for IR_A1 metrics and date columns
        if report_id in ("IR_A1", "IR_M1", "IR", "IR_EX"):
            items_metrics, items_date_cols = ir_a1_extract_metrics_and_dates(report_items)
        else:
            items_metrics = ""
            items_date_cols = ""

        #Set the report_header's Metric Types display list, not to be confused with the Metric_Type column in the table data
        # some providers don't put the metric_types in the report_header
        ## so we need to get them from the entire report_items list if the user wants them always and if report_items has content
        metric_types_list = report_header.get('Report_Filters').get("Metric_Type",[])
        if not metric_types_list and report_type.endswith('EX') and always_include_header_metric_types:#user wants the metric_types for master reports, not the COUNTER standard result
            if report_items:
                if report_id not in ("IR_A1", "IR_M1", "IR", "IR_EX"):
                    metric_types_list = extract_metric_types(report_items)# report_header metric_types is empty, get from combing report_items
                else:
                    metric_types_list = items_metrics

            else:
                metric_types_list = ''
        #log_error(f'Metric_Types_list: {metric_types_list}\n')

        # Standard views don't have metrics listed in report header
        ## and master reports don't repeat the list if it's the same as the default
        ### but the user can override both and always see the list in the header, using
        ### the value of always_include_header_metric_types in sushiconfig
        default_metric_types_list = get_default_metric_types(report_type)
        if not report_items:  # There are by definition no metric_types if there are no report items
            metric_type_string = ''
        else:
            if always_include_header_metric_types: #does the user want always display (True) or go with COUNTER standard rules (False)
                if not metric_types_list or (set(metric_types_list) == set(default_metric_types_list)) :#display the default list
                    metric_type_string = "; ".join(map(str,default_metric_types_list))
                else:# report list is different from default - display what the report has
                    metric_type_string = "; ".join(metric_types_list)
            else:# user wants the COUNTER standard behavior
                if not metric_types_list: # providers usually don't have
                    metric_type_string  = ""
                else:
                    if not report_type.endswith('EX') and (len(report_type) == 5): #Standard views don't show the metric_types
                        metric_type_string  = ""
                    else:# user wants standard and this is a master report, not a view, so only display if they are different from default
                        if set(metric_types_list) == set(default_metric_types_list):# they are the same so nothing is displayed
                            metric_type_string  = ""
                        else:#report has non-default metric_types selected, so display them in a master report
                            metric_type_string = "; ".join(metric_types_list)

        # Report Header rows (lines 1–13)
        inst_id_orig = report_header.get("Institution_ID")
        if not inst_id_orig:
           inst_id=""
        else:
            inst_id = format_nested_id(inst_id_orig)  # Flatten Institution_ID
            inst_id =  inst_id.replace("Proprietary:", "")
        rep_att_orig = report_header.get("Report_Attributes")
        if rep_att_orig:
            rep_att = format_nested_id(rep_att_orig)  # Flatten Report_Attributes
            rep_att = rep_att.replace("Attributes_To_Show:","Attributes_To_Show=")
            rep_att = rep_att.replace(",","|")
        else:
           rep_att=""
        rep_fil = get_report_filter_string(report_header.get("Report_Filters"))  # Flatten Report_Attributes
        if not rep_fil:
           rep_fil=""
        rep_per = reporting_period_build(report_header.get("Report_Filters"))  # Flatten Report_Attributes
        if not rep_per:
           rep_per=""
        excep = format_exceptions(report_header)# Flatten Report_Attributes
        if not excep:
           excep=""
        header_rows = [
            ["Report_Name", report_header.get("Report_Name", "")],
            ["Report_ID", report_id],### Even though we are making our own "EX" report, the data should still reflect the master report type for the database
            ["Release", report_header.get("Release", "")],
            ["Institution_Name", report_header.get("Institution_Name", "")],
            ["Institution_ID", inst_id],
            ["Metric_Types", metric_type_string],
            ["Report_Filters", rep_fil],
            ["Report_Attributes", rep_att],
            ["Exceptions", excep],
            ["Reporting_Period", rep_per],
            ["Created", report_header.get("Created", "")],
            ["Created_By", report_header.get("Created_By", "")],
            ["Registry_Record", report_header.get("Registry_Record", "")]
        ]

        # Write output to TSV
        with open(tsv_full_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter="\t")

            # Write header rows (lines 1–13)
            writer.writerows(header_rows)
            # Add the blank line before the table header (Line 14)
            writer.writerow([])  # Outputs a proper blank line

        if not report_items: # nothing else to do if we're saving an "empty" report
            return tsv_full_path
        #Get the data column header row ready with the year_month columns
        # If missing from header, extract year-month keys from the Performance section and add them as columns to column_order_list
        year_month_columns = generate_date_range(rep_per)
        header_date_range = year_month_columns.copy()
        #Get year_month_columns then add them to the total table column list
        if not year_month_columns:
            if report_id not in ("IR_A1", "IR_M1", "IR", "IR_EX"):
                year_month_columns = date_columns(report_items)
            else:
                year_month_columns = items_date_cols
                column_order_list = items_date_cols
        if not year_month_columns: # unable to get year_month columns from the report header OR the report_items, this should never happen
            log_error(f'ERROR: No usage year-months in report items, skipping this report: {json.dumps(report_header, separators=(",", ":"))}')
            return None
        else:
            if year_month_columns and year_month_columns[0] in column_order_list:
                pass
            else:
                column_order_list_dates = column_order_list.copy()
                column_order_list_dates += year_month_columns # adds to the end of the list of report item columns
                column_order_list = column_order_list_dates.copy()
        # Final table headers: Use the predefined list plus dynamic year-month columns which is now in column_order_list
        # This is not to be confused with the report header in lines 1-13 of the tsv, written above to the fil
        # This has its own writerows at the bottom right before the data rows
        table_headers = list(column_order_list)
        # Regex pattern to match yyyy-mm format
        pattern = re.compile(r"^\d{4}-\d{2}$")
        for i, item in enumerate(table_headers):
            if pattern.match(item):  # Check if the item matches the yyyy-mm pattern
                # Convert and replace the item with the formatted date so 2025-01 becomes Jan-2025 etc.
                date_obj = datetime.strptime(item, "%Y-%m")
                table_headers[i] = date_obj.strftime("%b-%Y")


        # Write output to TSV "a" because we've already started with the report headers lines 1-14
        with open(tsv_full_path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter="\t")
            # Write table header (line 15)
            writer.writerow(table_headers)

        #Now we get the actual rows for the table
        if report_type in ("IR_A1", "IR_M1", "IR", "IR_EX"):
            if report_type == "IR_A1":
                rows = get_ir_a1_data(report_items,header_date_range)#these are complete including the date columns and metrics
            elif report_type == "IR_M1":
                rows = get_ir_m1_data(report_items,header_date_range)
            elif  report_type == "IR_EX": # Must be the master IR report extended
                rows = get_ir_ex_data(report_items,header_date_range)
            else: # Must be the master IR report
                rows = get_ir_m1_data(report_items,header_date_range)
            for row in rows:
                # Add missing keys with empty string values
                for column in column_order_list:
                    if column not in row:
                        row[column] = ''
            for row in rows:
                ordered_values = [row[column] for column in column_order_list]
                with open(tsv_full_path, "a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f, delimiter="\t")
                    writer.writerow(ordered_values)
            print(f"TSV file successfully created at: {tsv_full_path}")
            log_error(f"INFO: TSV file successfully created at: {tsv_full_path}")
            #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
            return tsv_full_path # Done with the IR_A1/M1 report
        else:# Must be one of the non-IR reports or views
            # Generate rows
            for i_index, item in enumerate(report_items):  # "Item" is an array (list) of report_items
                #Reset the row list for every item/attribute_performance
                row = []
                row = [None] * len(column_order_list)  # Prepopulate/clear out the row with placeholders
                #First the top level keys in the item that need to go into the rows if they are in column_order_list
                item_fields_list = ["Title", "Platform", "Database", "Publisher", "Book_Segment_Count", "Publisher_ID"]
                fields_to_add = list(set(item_fields_list) & set(column_order_list))
                for field in fields_to_add:  #All of these are possible fields for this particular report type
                    if field == "Publisher_ID" and item.get('Publisher_ID',{}):
                        temp_value = item.get('Publisher_ID',{})
                        if temp_value:
                            value = str(format_nested_id(temp_value)).replace("\r", "")
                            value =  value.replace("Proprietary:", "")
                        else:
                            value = ''
                    else:
                        value = item.get(field,"")
                    col_index = column_order_list.index(field)
                    row[col_index] = value

                #Handle the Item_ID columns - Item_ID is a dict with one or more key-value pairs
                ### Only some of these will be present depending on the particular kind of item it is
                #### Note that the column_order_list will always have Proprietary_ID, not Proprietary even if the provider uses the shorter form
                if not isinstance(item, dict):
                    raise ValueError("Error: 'item' is not a dictionary!")
                    raise TypeError("Error: 'item' must be a dictionary.")
                item_id_dict = item.get('Item_ID', {})
                item_id_fields_list = ["DOI", "ISBN", "Print_ISSN", "Online_ISSN", "URI", "Proprietary", "Proprietary_ID"]
                ## Only look for fields that are possible in and item_id AND possible in this particular report_type
                fields_to_add = list(set(item_id_fields_list) & set(column_order_list))
                if "Proprietary" not in fields_to_add and "Proprietary" in item_id_dict:
                    item_id_dict["Proprietary_ID"] = item_id_dict.pop("Proprietary")
                for field in fields_to_add:
                    if field in fields_to_add:
                        if not isinstance(item_id_dict, dict):
                            continue
                        value = item_id_dict.get(field, "")  # have to use the json original field key to get the value
                        col_index = column_order_list.index(field)
                        row[col_index]= value

                # Handle Attribute_Performance - some column values come from the top of A-P
                # A-P is a list of dicts  but will have only one within any "item" in report_items
                ### Note these should NOT be confused with report_header fields by these same names
                attribute = item.get("Attribute_Performance", [])
                attr_fields_list = ["Data_Type", "YOP", "Access_Method", "Access_Type"] # this is generic all possible fields from an A-P
                ## Get the columns that both the list of possible attr fields AND the columns possible for this kind of report have
                fields_to_add = list(set(attr_fields_list) & set(column_order_list))
                # We have to empty out of row the values from a previous A-P block
                for field in fields_to_add:
                    col_index = column_order_list.index(field)
                    row[col_index] = ""
                ### A-P is a list, an attribute is a dict, and a "performance" within an attribute is a dict
                for attr in attribute:  ### usully just one (dict) per item but in theory could be more than one
                    if 'Performance' not in attr: # in theory this should never happen but if it does, we skip this entire attr
                        log_error(f'ERROR: There is no performance in this attribute block - this should never happen but we have to skip this attribute')
                        continue
                    if not isinstance(attr, dict):
                        log_error(f'ERROR: ATTR is {type(attr)}. That should never happen - skipping this atttribute block\n')
                        continue
                    for field in fields_to_add: ## For each possible field that this particular report could have column for
                        if field not in attr: ### now is this possible field also in our actual data
                            continue
                        ### If we've gotten here then we have an A-P key that is needed for this particular report
                        ##### so we need to add that to our row
                        ##### This field is definitely in this attr
                        value = attr.get(field, '')
                        col_index = column_order_list.index(field)
                        row[col_index]= value

                    performance = attr.get("Performance", {})

                    # We generate the Metric_Type and Year_Month column values from Performance
                    ### and then we can pull all of those Item, Item_ID, A-P data into the actual row
                    for metric_type, date_values in performance.items():
                        ### First we have to empty out the row values for the year-month data
                        #### but we want to keep the values for the A-P and item_id as they repeat through all of these Performance lines
                        #### Metric_Type and Reporting_Period_Total will necessarily get overwritten below
                        #### and the rest of the row values should be repeated for each performance line
                        start_index = column_order_list.index("Reporting_Period_Total") # Start clearing column values from RPT through all of the year-months
                        for i in range(start_index, len(row)):
                            row[i] = ""
                        # There will always be a Metric_Type column in every report
                        col_index = column_order_list.index("Metric_Type")
                        row[col_index] = metric_type
                        # There will always be a Reporting_Period_Total column in every report
                        # and its value is calculated here
                        reporting_period_total = 0  # Initialize the total
                        for item in column_order_list:
                            if len(item) == 7 and item[4] == "-" and item[:4].isdigit() and item[5:].isdigit():
                                col_index = column_order_list.index(item)
                                row[col_index] = "0"
                        for value in date_values.values():
                            if value:  # Only add the value if it's not empty or None
                                reporting_period_total += int(value)  # Convert the value to an integer and add it to the total
                        col_index = column_order_list.index("Reporting_Period_Total")
                        row[col_index] = reporting_period_total
                        # Prepopulate all cells for the year-month columns with 0 because they can't be blank
                        for year_month, value in date_values.items():
                            col_index = column_order_list.index(year_month)  # Find the column index
                            if isinstance(value,int):
                                row[col_index]= str(value)
                        # This is where we need to write out this row  before looping for the next metric type
                        # Write output to TSV
                        with open(tsv_full_path, "a", newline="", encoding="utf-8-sig") as f:
                            writer = csv.writer(f, delimiter="\t")
                            # Write table row (line 16 onward)
                            writer.writerow(row)

        print(f"TSV file successfully created at: {tsv_full_path}")
        #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
        return tsv_full_path

    except Exception as e:
        #log_error(f"DEBUG: I am inside: {inspect.currentframe().f_code.co_name}")
        print(f"An error occurred during the conversion: {e}\nThe tsv file  may not have been created properly.")
        log_error(f"ERROR: An error occurred during the conversion: {e}\nThe tsv file  may not have been created properly.")
