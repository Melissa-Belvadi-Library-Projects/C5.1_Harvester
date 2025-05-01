import sqlite3
from logger import log_error
from sushiconfig import data_table


def insert_sqlite(data_dict, report_id, cursor,conn):
    #Insert or update data into SQLite.
    try:

        table_name = data_table
        # Build the SELECT query to fetch the entire row for comparison

            # Retrieve column names from the table to ensure proper alignment
        cursor.execute(f"PRAGMA table_info({table_name})")
        # Insert a new row or write over an existing one based on the unique index on that table
        columns = ", ".join(data_dict.keys())
        #log_error(f'IS columns: {columns}\n')
        placeholders = ", ".join(["?"] * len(data_dict))
        insert_sql = f'''
            INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})
        '''
        cursor.execute(insert_sql, tuple(data_dict.values()))
        #log_error('fIS: just did cursor.execute: {tuple(data_dict.values())}\n')
        #log_error('fIS: just did conn.commit\n')
        return table_name

    except sqlite3.OperationalError as e:
        # Handle operational errors (e.g., unable to connect, missing table, etc.)
        print(f"OperationalError: {e}")
        log_error(f"OperationalError: {e}")
        raise

    except sqlite3.DatabaseError as e:
        # Generic database errors
        print(f"DatabaseError: {e}")
        log_error(f"DatabaseError: {e}")
        raise

    except sqlite3.Error as e:
        # Handle SQLite errors
        error_message = f"\nSQLite Error (Report ID {report_id}): {e}\n"
        print(error_message)
        log_error(error_message)
        raise

    except Exception as e:
        # General catch-all for any other exceptions
        log_error(f"An unexpected error occurred: {e}")
        raise

