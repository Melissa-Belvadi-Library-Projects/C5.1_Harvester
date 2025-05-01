# create_tables.py
# create the two sqlite tables using the list from data_columns_sql 
from logger import log_error
from sushiconfig import sqlite_filename, data_table
from data_columns import data_columns_sql


def create_data_table(cursor):
    #Create the data table in the SQLite database
    #log_debug(', '.join(data_columns_sql))  # This will show you the actual SQL
    column_definitions = ', '.join(data_columns_sql)  # Join data_columns_sql to define columns
    sql_statement = f'CREATE TABLE IF NOT EXISTS {data_table} ( Data_ID INTEGER PRIMARY KEY AUTOINCREMENT, {column_definitions}, UNIQUE (Provider_Name, Report_Type, Data_Year, Data_Month, Metric_Type, Title, Access_Method, Publisher, YOP, DOI, ISBN, Print_ISSN, Access_Type, Online_ISSN, URI, Article_Version, Proprietary, Database_Name, Platform, Item_Name, Data_Type));'
    #sql_statement = f'CREATE TABLE IF NOT EXISTS {data_table} ( Data_ID INTEGER PRIMARY KEY AUTOINCREMENT, {column_definitions}, FOREIGN KEY (Header_ID) REFERENCES header(id), UNIQUE (Provider_Name, Report_Type, Data_Year, Data_Month, Metric_Type, Title, Access_Method, Publisher, YOP, DOI, ISBN, Print_ISSN, Access_Type, Online_ISSN, URI, Article_Version, Proprietary, Database_Name, Platform, Item_Name, Data_Type));'
    #log_debug(f"Executing create data_table SQL: {sql_statement}\n")  # Output the full SQL for debugging
    cursor.execute(sql_statement)  # Finally execute the SQL
    Index_Report_Type = f'CREATE INDEX IF NOT EXISTS idx_report_type ON {data_table} (Report_Type)'
    Index_Provider_Name = f'CREATE INDEX IF NOT EXISTS idx_provider_name ON {data_table} (Provider_Name)'
    Index_Metric_Type = f'CREATE INDEX IF NOT EXISTS idx_Metric_Type ON {data_table} (Metric_Type)'
    Index_Title = f'CREATE INDEX IF NOT EXISTS idx_Title ON {data_table} (Title)'

    #log_debug("Executing data table indexes SQL")  # Output the full SQL for debugging
    cursor.execute(Index_Report_Type)
    cursor.execute(Index_Title)
    cursor.execute(Index_Provider_Name)
    cursor.execute(Index_Metric_Type)

def create_header_table(cursor):
    pass  # removing header table from project

