# data_columns.py

# List of column names for data insertion
data_columns = [
        "Row_Hash",  #not part of COUNTER data, needed for uniqueness of rows
        "Provider_Name",
        "Report_Type",
        "Item",
        "Database_Name",
        "Access_Method",
        "Access_Type",
        "Article_Version",
        "Authors" ,
        "Title",
        "Publisher",
        "Publisher_ID",
        "Platform",
        "Publication_Date",
        "DOI",
        "ISBN",
        "Print_ISSN",
        "Online_ISSN",
        "Proprietary",
        "URI",
        "YOP",
        "Data_Type",
        "Customer_ID",
        "Institution_Name",
        "Country_Name",
        "Country_Code",
        "Subdivision_Name",
        "Subdivision_Code",
        "Attributed",
        "Metric_Type",
        "Data_Year",
        "Data_Month",
        "Metric_Usage",
        "Book_Segment_Count",
        "Parent_Article_Version",
        "Parent_Authors",
        "Parent_Data_Type",
        "Parent_DOI",
        "Parent_ISBN",
        "Parent_Online_ISSN",
        "Parent_Print_ISSN",
        "Parent_Proprietary_ID",
        "Parent_Publication_Date",
        "Parent_Title",
        "Parent_URI"
        #"Component_Authors",
        #"Component_Data_Type",
        #"Component_DOI",
        #"Component_Online_ISSN",
        #"Component_Print_ISSN",
        #"Component_Proprietary",
        #"Component_Publication",
        #"Component_ISBN",
        #"Component_Title",
        #"Component_URI"

]

# List of columns for SQLite create table statements (with types)
data_columns_sql = [
    #f"{col} TEXT" if col not in ["Data_ID", "Header_ID", "Data_Month","Data_Year", "Metric_Usage"] else f"{col} INTEGER" for col in data_columns
    f"{col} TEXT" if col not in ["Data_ID", "Data_Month","Data_Year", "Metric_Usage"] else f"{col} INTEGER" for col in data_columns
]

