# tsv_utils.py : Functions and variables used to generate tsv reports

### used to determine default metric list if user wants to always include it even when not the COUNTER COP to do so
PR_list_metric = ["Unique_Item_Investigations",  "Searches_Platform",  "Total_Item_Requests",  "Unique_Title_Investigations",  "Unique_Item_Requests",  "Unique_Title_Requests",  "Total_Item_Investigations"]
PR_P1_list_metric = ["Searches_Platform","Total_Item_Requests","Unique_Item_Requests","Unique_Title_Requests"]

DR_list_metric = ["Unique_Item_Investigations",  "Total_Item_Requests",  "Unique_Item_Requests",  "Searches_Regular",  "Total_Item_Investigations"]
DR_D1_list_metric = ["Searches_Automated","Searches_Federated","Searches_Regular","Total_Item_Investigations","Total_Item_Requests","Unique_Item_Investigations","Unique_Item_Requests"]
DR_D2_list_metric = ["Limit_Exceeded","No_License"]

TR_list_metric = ["Unique_Item_Investigations",  "Unique_Title_Investigations",  "Total_Item_Requests",  "Unique_Item_Requests",  "Unique_Title_Requests",  "Total_Item_Investigations",  "No_License"]
TR_J1_list_metric = ["Total_Item_Requests","Unique_Item_Requests"]
TR_J2_list_metric = ["Limit_Exceeded","No_License"]
TR_J3_list_metric = ["Total_Item_Investigations","Total_Item_Requests","Unique_Item_Investigations","Unique_Item_Requests"]
TR_J4_list_metric = ["Total_Item_Requests","Unique_Item_Requests"]
TR_B1_list_metric = ["Total_Item_Requests","Unique_Title_Requests"]
TR_B2_list_metric = ["Limit_Exceeded","No_License"]
TR_B3_list_metric = ["Total_Item_Investigations","Total_Item_Requests","Unique_Item_Investigations","Unique_Item_Requests","Unique_Title_Investigations","Unique_Title_Requests"]

IR_list_metric = ["Total_Item_Investigations","Total_Item_Requests","Unique_Item_Investigations","Unique_Item_Requests","Limit_Exceeded","No_License"]
IR_A1_list_metric = ["Total_Item_Requests","Unique_Item_Requests"]
IR_M1_list_metric = ["Total_Item_Requests","Unique_Item_Requests"]

official_reports = ['DR', 'DR_EX', 'DR_D1', 'DR_D2', 'PR', 'PR_EX', 'PR_P1', 'TR', 'TR_EX', 'TR_J1', 'TR_J2', 'TR_J3', 'TR_J4', 'TR_B1', 'TR_B2', 'TR_B3', 'IR', 'IR_EX', 'IR_A1', 'IR_M1']

default_metric_types = {
    "DR": DR_list_metric,
    "DR_EX": DR_list_metric,
    "DR_D1": DR_D1_list_metric,
    "DR_D2": DR_D2_list_metric,
    "PR": PR_list_metric,
    "PR_EX": PR_list_metric,
    "PR_P1": PR_P1_list_metric,
    "TR": TR_list_metric,
    "TR_EX": TR_list_metric,
    "TR_J1": TR_J1_list_metric,
    "TR_J2": TR_J2_list_metric,
    "TR_J3": TR_J3_list_metric,
    "TR_J4": TR_J4_list_metric,
    "TR_B1": TR_B1_list_metric,
    "TR_B2": TR_B2_list_metric,
    "TR_B3": TR_B3_list_metric,
    "IR": IR_list_metric,
    "IR_EX": IR_list_metric,
    "IR_A1": IR_A1_list_metric,
    "IR_M1": IR_M1_list_metric
}

# the ordered lists of possible column headers in .tsv files for each report type
# all of these come before the various year-month columns which themselves should be
# in chronological order. Referred to in code notes as "column orders"

PR_list = [
    "Platform",
    "Data_Type",
    "Metric_Type",
    "Reporting_Period_Total"
]

PR_EX_list = [
    "Platform",
    "Data_Type",
    "Access_Method",
    "Metric_Type",
    "Reporting_Period_Total"
]

PR_P1_list = [
    "Platform",
    "Data_Type",
    "Metric_Type",
    "Reporting_Period_Total"
]

DR_list = [
    "Database",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "Proprietary_ID",
    "Data_Type",
    "Metric_Type",
    "Reporting_Period_Total"
]

DR_EX_list = [
    "Database",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "Proprietary_ID",
    "Data_Type",
    "Access_Method",
    "Metric_Type",
    "Reporting_Period_Total"
]

DR_D1_list = [
    "Database",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "Proprietary_ID",
    "Metric_Type",
    "Reporting_Period_Total"
]

DR_D2_list = [
    "Database",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "Proprietary_ID",
    "Metric_Type",
    "Reporting_Period_Total"
]

TR_list = [
    "Title",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "ISBN",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Data_Type",
    "Metric_Type",
    "Reporting_Period_Total"
]

TR_EX_list = [
    "Title",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "ISBN",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Data_Type",
    "YOP",
    "Access_Type",
    "Access_Method",
    "Metric_Type",
    "Reporting_Period_Total"
]

TR_J1_list = [
    "Title",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Metric_Type",
    "Reporting_Period_Total"
]

TR_J2_list = [
    "Title",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Metric_Type",
    "Reporting_Period_Total"
]

TR_J3_list = [
    "Title",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Access_Type",
    "Metric_Type",
    "Reporting_Period_Total"
]

TR_J4_list = [
    "Title",
    "Publisher",
    "Publisher_ID",
    "Platform",
   "DOI",
    "Proprietary_ID",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "YOP",
    "Metric_Type",
    "Reporting_Period_Total"
]

TR_B1_list = [
    "Title",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "ISBN",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Data_Type",
    "YOP",
    "Metric_Type",
   "Reporting_Period_Total"
]

TR_B2_list = [
    "Title",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "ISBN",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Data_Type",
    "YOP",
    "Metric_Type",
    "Reporting_Period_Total"
]

TR_B3_list = [
    "Title",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "ISBN",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Data_Type",
    "YOP",
    "Access_Type",
    "Metric_Type",
    "Reporting_Period_Total"
]

IR_list = [
    "Item",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "ISBN",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Data_Type",
    "Metric_Type",
    "Reporting_Period_Total"
]


IR_EX_list = [
    "Item",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "Authors",
    "Publication_Date",
    "Article_Version",
    "DOI",
    "Proprietary_ID",
    "ISBN",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Parent_Title",
    "Parent_Authors",
    "Parent_Publication_Date",
    "Parent_Article_Version",
    "Parent_Data_Type",
    "Parent_DOI",
    "Parent_Proprietary_ID",
    "Parent_ISBN",
    "Parent_Print_ISSN",
    "Parent_Online_ISSN",
    "Parent_URI",
    "Data_Type",
    "YOP",
    "Access_Type",
    "Access_Method",
    "Metric_Type",
    "Reporting_Period_Total"
]
IR_A1_list = [
    "Item",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "Authors",
    "Publication_Date",
    "Article_Version",
    "DOI",
    "Proprietary_ID",
    "Print_ISSN",
    "Online_ISSN",
    "URI",
    "Parent_Title",
    "Parent_Authors",
    "Parent_Article_Version",
    "Parent_DOI",
    "Parent_Proprietary_ID",
    "Parent_Print_ISSN",
    "Parent_Online_ISSN",
    "Parent_URI",
    "Access_Type",
    "Metric_Type",
    "Reporting_Period_Total"
]

IR_M1_list = [
    "Item",
    "Publisher",
    "Publisher_ID",
    "Platform",
    "DOI",
    "Proprietary_ID",
    "URI",
    "Data_Type",
    "Metric_Type",
    "Reporting_Period_Total"
]



def format_nested_id(nested_field):

    if isinstance(nested_field, dict):
        # Build a list of formatted key-value strings
        formatted_pairs = []
        for key, value in nested_field.items():
            if isinstance(value, list):  # If value is a list, join it with commas
                value_str = ",".join(map(str, value))  # Ensure all list items are strings
                formatted_pairs.append(f"{key}:{value_str}")
            else:  # If value is not a list, directly convert it to a string
                formatted_pairs.append(f"{key}:{str(value)}")
        # Join all key-value pairs into a single semicolon-separated string
        return str("; ".join(formatted_pairs))
    
    # Fallback: Ensure non-dict inputs are converted to string
    return str(nested_field) if nested_field is not None else ""



def format_exceptions(report_header):
    # Extract the Exceptions array from the Report_Header dictionary
    exceptions_list = report_header.get("Exceptions", [])
    # Ensure the Exceptions data is a list
    if not isinstance(exceptions_list, list) or not exceptions_list:
        return ""

    formatted_exceptions = []
    for exception in exceptions_list:
        # Extract required fields from each exception
        code = exception.get("Code", "Undefined Code")
        message = exception.get("Message", "No Message")
        data = exception.get("Data", None)
        help_url = exception.get("Help_URL", None)
        if help_url is not None:
            formatted_exceptions.append(f"{code}: {message} ({data}, {help_url})")
        else:
            formatted_exceptions.append(f"{code}: {message} ({data})")
    # Join all formatted exceptions with a semicolon for the final output
    final_string = "; ".join(formatted_exceptions)

    return final_string

