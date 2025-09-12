# create_tables.py
# create the sqlite table using the list from data_columns
from logger import log_error
from current_config import sqlite_filename, data_table
from data_columns import data_columns


def create_data_table(cursor):
    #Create the data table in the SQLite database
    # Add Row_Hash to your column definitions
    local_data_columns = data_columns.copy()
    if "Row_Hash" not in local_data_columns:
        local_data_columns.append("Row_Hash")
    column_definitions = ', '.join(local_data_columns)  # Join local_data_columns to define columns
    sql_statement = f'''
    CREATE TABLE IF NOT EXISTS {data_table} (
        Data_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        {column_definitions},
        UNIQUE (Row_Hash)
    );
    '''
    # Execute the SQL to create the table

    cursor.execute(sql_statement)  # Finally execute the SQL
    Index_Report_Type = f'CREATE INDEX IF NOT EXISTS idx_report_type ON {data_table} (Report_Type)'
    Index_Provider_Name = f'CREATE INDEX IF NOT EXISTS idx_provider_name ON {data_table} (Provider_Name)'
    Index_Metric_Type = f'CREATE INDEX IF NOT EXISTS idx_Metric_Type ON {data_table} (Metric_Type)'
    Index_Title = f'CREATE INDEX IF NOT EXISTS idx_Title ON {data_table} (Title)'

    cursor.execute(Index_Report_Type)
    cursor.execute(Index_Title)
    cursor.execute(Index_Provider_Name)
    cursor.execute(Index_Metric_Type)

