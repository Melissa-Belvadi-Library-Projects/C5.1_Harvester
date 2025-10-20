import sqlite3
import hashlib
from logger import log_error
#from current_config import data_table
# Removed - will be passed as parameter
from data_columns import data_columns

def normalize_column_names(data_dict):
    """Normalize inconsistent column names in a single row dictionary."""
    normalized = data_dict.copy()

    # Handle "Proprietary" vs "Proprietary_ID" -> normalize to "Proprietary"
    if "Proprietary_ID" in normalized and "Proprietary" not in normalized:
        normalized["Proprietary"] = normalized.pop("Proprietary_ID")

    # Handle "Parent_Proprietary" vs "Parent_Proprietary_ID" -> normalize to "Parent_Proprietary_ID"
    if "Parent_Proprietary" in normalized and "Parent_Proprietary_ID" not in normalized:
        normalized["Parent_Proprietary_ID"] = normalized.pop("Parent_Proprietary")

    # Handle "Database" ->  to "Database_Name"
    if "Database" in normalized and "Database_Name" not in normalized:
        normalized["Database_Name"] = normalized.pop("Database")

    return normalized


def generate_unique_hash(data_dict, data_columns):
    """Create a unique hash from the combination of key columns."""
    values = []
    for column in data_columns:
        if column in  ["Data_ID", "Row_Hash", "Metric_Usage"]:# exclude these from hash because they will prevent replacing data that needs to be replaced
            continue
        value = data_dict.get(column)
        # Special handling for None/NULL values
        if value is None:
            values.append("__NULL__" + column)
        else:
            values.append(f"{column}={value}")

    hash_input = "||".join(values)
    return hashlib.md5(hash_input.encode('utf-8')).hexdigest()

def insert_sqlite(data_dict, report_id, cursor, conn ,config):
    #Insert or update data into SQLite.
    #pass config so insert_sqlite can access data_table
    try:

        # Extract data_table from config instead of using cached import.
        data_table = config['data_table'] #New - Daniel


        table_name = data_table
        # Build the SELECT query to fetch the entire row for comparison
        #Using hash column to make sure no duplicate rows in table for "insert or replace"
        '''Statistics on MD5 Collision Risk:
        MD5 produces a 128-bit hash value (2^128 possible values, or about 3.4 × 10^38)
        For collision probability to reach 50%, you'd need approximately 2^64 records (18.4 quintillion)
        With 10 million rows, the collision probability is around 10^-23 (effectively zero)
        Even with 1 billion rows, probability remains astronomically small at about 10^-19
        '''

        data_dict["Row_Hash"] = generate_unique_hash(data_dict, data_columns)

       # Retrieve column names from the table to ensure proper alignment
        cursor.execute(f"PRAGMA table_info({table_name})")

        normalized_dict = normalize_column_names(data_dict)

        columns = ", ".join(normalized_dict.keys())
        placeholders = ", ".join(["?"] * len(normalized_dict))
        # Insert a new row or write over an existing one based on the unique index on that table
        insert_sql = f'''
            INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})
        '''
        cursor.execute(insert_sql, tuple(normalized_dict.values()))
        return table_name

    except sqlite3.OperationalError as e:
        # Handle operational errors (e.g., unable to connect, missing table, etc.)
        print(f"OperationalError: {e}")
        log_error(f"OperationalError: {e}")
        raise

    except sqlite3.DatabaseError as e:
        # Generic database errors
        print(f"DatabaseError: {e}")
        log_error(f"SQLite Error: DatabaseError: {e}")
        raise

    except sqlite3.Error as e:
        # Handle SQLite errors
        error_message = f"SQLite Error: (Report ID {report_id}): {e}\n"
        print(error_message)
        log_error(error_message)
        raise

    except Exception as e:
        # General catch-all for any other exceptions
        log_error(f"SQLite Error: An unexpected error occurred: {e}")
        raise

