# data_columns.py

# List of column names for data insertion
data_columns = [
        "Row_Hash",  #not part of COUNTER data, needed for uniqueness of rows
        "Provider_Name",
        "Report_Type",
        "Platform",
        "Database_Name",
        "Title",
        "Metric_Type",
        "Data_Year",
        "Data_Month",
        "Metric_Usage",
        "Data_Type",
        "Access_Method",
        "Access_Type",
        "Item",
        "YOP",
        "Publisher",
        "DOI",
        "ISBN",
        "Print_ISSN",
        "Online_ISSN",
        "Proprietary",
        "URI",
        "Article_Version",
        "Authors",
        "Publication_Date",
        "Publisher_ID",
        "Customer_ID",
        "Institution_Name",
        "Country_Name",
        "Country_Code",
        "Subdivision_Name",
        "Subdivision_Code",
        "Attributed",
        "Book_Segment_Count",
        "Parent_Data_Type",
        "Parent_Publication_Date",
        "Parent_Title",
        "Parent_Article_Version",
        "Parent_Authors",
        "Parent_DOI",
        "Parent_ISBN",
        "Parent_Online_ISSN",
        "Parent_Print_ISSN",
        "Parent_Proprietary_ID",
        "Parent_URI",
        "Component_Authors",
        "Component_Data_Type",
        "Component_DOI",
        "Component_Online_ISSN",
        "Component_Print_ISSN",
        "Component_Proprietary",
        "Component_Publication",
        "Component_ISBN",
        "Component_Title",
        "Component_URI",
]

# List of columns for SQLite create table statements (with types)
data_columns_sql = [
    f"{col} TEXT PRIMARY KEY" if col == "Row_Hash"
    else f"{col} INTEGER" if col in ["Data_Month", "Data_Year", "Metric_Usage"]
    else f"{col} TEXT"
    for col in data_columns
]
