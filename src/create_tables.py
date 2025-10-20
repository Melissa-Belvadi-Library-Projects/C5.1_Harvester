# create_tables.py
# create the sqlite table using the list from data_columns

from logger import log_error
#from current_config import sqlite_filename, data_table-D
# Removed - will be passed as parameters-D
from data_columns import data_columns, data_columns_sql


def create_data_table(cursor,data_table):
    # Added data_table parameter- Daniel
    #Create the data table in the SQLite database
    # data_columns_sql sets the column types for all columns, including Row_Hash as primary key
    local_data_columns = data_columns_sql.copy()
    column_definitions = ', '.join(local_data_columns)  # Join local_data_columns to define columns
    sql_statement = f'''
    CREATE TABLE IF NOT EXISTS {data_table} (
        {column_definitions}
    );
    '''
    # Execute the SQL to create the table

    cursor.execute(sql_statement)  # Finally execute the SQL
    Index_Report_Type = f'CREATE INDEX IF NOT EXISTS idx_report_type ON {data_table} (Report_Type)'
    Index_Provider_Name = f'CREATE INDEX IF NOT EXISTS idx_provider_name ON {data_table} (Provider_Name)'
    Index_Metric_Type = f'CREATE INDEX IF NOT EXISTS idx_Metric_Type ON {data_table} (Metric_Type)'
    Index_Title = f'CREATE INDEX IF NOT EXISTS idx_Title ON {data_table} (Title)'
    Index_Dates = f'CREATE INDEX IF NOT EXISTS idx_yearmonth ON {data_table} (Data_Year, Data_Month)'

    cursor.execute(Index_Report_Type)
    cursor.execute(Index_Title)
    cursor.execute(Index_Provider_Name)
    cursor.execute(Index_Metric_Type)
    cursor.execute(Index_Dates)

