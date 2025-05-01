# logger.py

from sushiconfig import error_log_file

def clear_log_error():
    with open(error_log_file, 'w'):
       pass

def log_error(message):
    #Log error messages that users need to know about
    with open(error_log_file, 'a') as elog_file:
        elog_file.write(str(message) + '\n')

