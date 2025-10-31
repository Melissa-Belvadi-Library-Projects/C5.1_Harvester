# create_tables.py
# create the sqlite table using the list from data_columns

from logger import log_error
import data_columns # includes data_columns_TR etc.


def create_data_table(cursor):
    report_types = ['IR','PR','TR','DR']
    column_definitions = {}
    all_data_columns = {
    'TR': data_columns.data_columns_TR,
    'PR': data_columns.data_columns_PR,
    'IR': data_columns.data_columns_IR,
    'DR': data_columns.data_columns_DR
    }

    for report_code in report_types:
        data_columns_sql = [
        f"{col} TEXT PRIMARY KEY" if col == "Row_Hash"
        else f"{col} INTEGER" if col in ["Data_Month", "Data_Year", "Metric_Usage"]
        else f"{col} TEXT"
        for col in all_data_columns[report_code]
        ]

        # Get the list of columns for the current report_code
        columns = all_data_columns[report_code]
        # Create the joined string and store it in the new dictionary
        column_definitions_with_sql_data_type = {}
        column_definitions_with_sql_data_type[report_code] = ', '.join(data_columns_sql)

        sql_statement = f'''
        CREATE TABLE IF NOT EXISTS {report_code} (
            {column_definitions_with_sql_data_type[report_code]},
            UNIQUE (Row_Hash)
        );
        '''
        # Execute the SQL to create the table

        cursor.execute(sql_statement)  # Finally execute the SQL
        Index_Report_Type = f'CREATE INDEX IF NOT EXISTS idx_report_type ON {report_code} (Report_Type)'
        Index_Provider_Name = f'CREATE INDEX IF NOT EXISTS idx_provider_name ON {report_code} (Provider_Name)'
        Index_Metric_Type = f'CREATE INDEX IF NOT EXISTS idx_Metric_Type ON {report_code} (Metric_Type)'
        if report_code == 'TR':
            Index_Title = f'CREATE INDEX IF NOT EXISTS idx_Title ON {report_code} (Title)'
        Index_Dates = f'CREATE INDEX IF NOT EXISTS idx_yearmonth ON {report_code} (Data_Year, Data_Month)'

        cursor.execute(Index_Report_Type)
        if report_code == 'TR':
            cursor.execute(Index_Title)
        cursor.execute(Index_Provider_Name)
        cursor.execute(Index_Metric_Type)
        cursor.execute(Index_Dates)
