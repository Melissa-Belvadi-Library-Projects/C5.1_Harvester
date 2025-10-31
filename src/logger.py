# logger.py

# Global variables
_progress_callback = None
_error_log_file = 'infolog.txt'  # Default value


def set_error_log_file(filepath):
    """Set the error log file path."""
    global _error_log_file
    _error_log_file = filepath


def clear_log_error():
    with open(_error_log_file, 'w'):
       pass


def set_progress_callback(callback):
    """Set the callback function for progress updates."""
    global _progress_callback
    _progress_callback = callback


def log_error(message):
    #Log error messages that users need to know about
    with open(_error_log_file, 'a') as elog_file:
        elog_file.write(str(message) + '\n')

    # Also send to progress dialog if callback exists and it's an error/warning
    if _progress_callback:
        msg_upper = str(message).upper()
        if "ERROR:" in msg_upper or "WARNING:" in msg_upper:
            _progress_callback(message)