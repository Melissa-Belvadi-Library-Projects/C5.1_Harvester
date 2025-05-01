from pathlib import Path
from convert_counter_json_to_tsv import convert_counter_json_to_tsv
from logger import log_debug, log_error, clear_log_debug, clear_log_error
import sys

def main():
    clear_log_debug()

    # Check if a filename is provided as a command-line argument
    if len(sys.argv) > 1:
        # Use the first argument as the JSON file path
        json_file_path = sys.argv[1]
        print(f"Using JSON file from command line: {json_file_path}")
    else:
        # Prompt the user to enter the file path if not provided in the command line
        json_file_path = input("Enter the path to the COUNTER 5.1 JSON file: ").strip()

    # Check if the file exists
    file_path = Path(json_file_path)
    if not file_path.is_file():
        print(f"Error: The file {file_path} does not exist. Please check the path and try again.")
        return

    # Run the conversion process
    try:
        json_file_path = str(file_path)
        convert_counter_json_to_tsv(json_file_path)
    except Exception as e:
        print(f"An error occurred during the conversion: {e}")
        log_debug(f"An error occurred during the conversion: {e}")

if __name__ == "__main__":
    main()

