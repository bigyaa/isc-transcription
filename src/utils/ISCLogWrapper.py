# *************************************************************************************************************************
#   ISCLogWrapper.py 
#       This module provides a class, ISCLogWrapper, which wraps the Python logging module to set up customized logging
#       with options for console and file output, different log levels, and optional colorization of output for 
#       differentiation of log levels.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#      log_wrapper = ISCLogWrapper(
#         console_log_output="stdout",
#         console_log_level="info",
#         console_log_color=True,
#         logfile_file="application.log",
#         logfile_path="logs/",
#         logfile_log_level="debug",
#         logfile_log_color=False
#      )
#      log_wrapper.set_up_logging()
#
#      Parameters:
#         console_log_output - Designate the console output stream ('stdout' or 'stderr').
#         console_log_level - Specify the logging level for console output.
#         console_log_color - Toggle colorization for console output.
#         logfile_file - Name of the file to write logs to.
#         logfile_path - Directory path for the log file.
#         logfile_log_level - Specify the logging level for file output.
#         logfile_log_color - Toggle colorization for file output.
#
#   Design Notes:
#   -.  Log levels and color codes are customizable.
#   -.  Log format includes timestamps, thread names, log levels, file names, line numbers, and messages.
#   -.  The log line format and date format can be easily adjusted by modifying the constants.
#   -.  The logging setup configures both console and file handlers with respective formatters.
#   -.  Fails gracefully by returning False if the setup encounters issues.
# ---------------------------------------------------------------------------------------------------------------------
#   TODO:
#   -.  Implement configuration file support for easier logging configuration management.
#   -.  Add support for rotating file handlers to manage log file sizes.
#   -.  Consider adding network logging capabilities for centralized log management.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  November 2023
#   authors:       Reuben Maharaj, Bigya Bajarcharya, Mofeoluwa Jide-Jegede
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************
#
# os - for file and directory operations
# sys - to access the stdout and stderr streams
# logging - to use the logging functionalities provided by Python
# glob - to list the files in a directory (if needed for log management)
#
import os
import sys
import logging
import glob


# Define constants used for the log line format and date format
LOG_LINE_TEMPLATE="%(color_on)s[%(asctime)s.%(msecs)03d] [%(threadName)s] [%(levelname)-8s] [%(filename)s:%(lineno)d] %(message)s%(color_off)s"
LOG_LINE_DATEFMT="%Y-%m-%d %H:%M:%S"


# ***********************************************
# LogFormatter class definition
# ***********************************************
#
# LogFormatter is a custom formatter for the logging module, which supports colorized output.
#
# Logging formatter supporting colorized output
class LogFormatter(logging.Formatter):

    COLOR_CODES = {
        logging.CRITICAL: "\033[1;35m", # bright/bold magenta
        logging.ERROR:    "\033[1;31m", # bright/bold red
        logging.WARNING:  "\033[1;33m", # bright/bold yellow
        logging.INFO:     "\033[0;37m", # white / light gray
        logging.DEBUG:    "\033[1;30m"  # bright/bold black / dark gray
    }

    RESET_CODE = "\033[0m"

    def __init__(self, color, *args, **kwargs):
        super(LogFormatter, self).__init__(*args, **kwargs)
        self.color = color

    def format(self, record, *args, **kwargs):
        if (self.color == True and record.levelno in self.COLOR_CODES):
            record.color_on  = self.COLOR_CODES[record.levelno]
            record.color_off = self.RESET_CODE
        else:
            record.color_on  = ""
            record.color_off = ""
        return super(LogFormatter, self).format(record, *args, **kwargs)

# ***********************************************
# ISCLogWrapper class definition
# ***********************************************
#
# ISCLogWrapper is the main class provided by this module to configure custom logging behavior.
#
# This class wraps the logging module and provides methods to set up logging
class ISCLogWrapper:

    # The constructor takes several arguments that configure logging
    def __init__(self, console_log_output, console_log_level, console_log_color, logfile_file, logfile_path, logfile_log_level, logfile_log_color):
        self.console_log_output = console_log_output # The output to write the console logs to (stdout or stderr)
        self.console_log_level = console_log_level # The minimum logging level to log to the console (e.g., INFO, WARNING, etc.)
        self.console_log_color = console_log_color # A boolean value indicating whether the console log should be colorized
        self.logfile_file = logfile_file # The filename to write the logs to
        self.logfile_path = logfile_path # The directory path to write the logs to
        self.logfile_log_level = logfile_log_level # The minimum logging level to log to the file
        self.logfile_log_color = logfile_log_color # A boolean value indicating whether the file log should be colorized

    # Set up logging using the configuration values passed to the constructor

    def set_up_logging(self):
        # Ensure the log file directory exists
        try:
            if not os.path.exists(self.logfile_path):
                os.makedirs(self.logfile_path)
        except Exception as e:
            print(f"Failed to create log directory '{self.logfile_path}': {e}")
            return False

        # Create logger
        # For simplicity, we use the root logger, i.e. call 'logging.getLogger()'
        # without name argument. This way we can simply use module methods for
        # for logging throughout the script. An alternative would be exporting
        # the logger, i.e. 'global logger; logger = logging.getLogger("<name>")'
     
        logger = logging.getLogger()
        
        # Set global log level to 'debug' (required for handler levels to work)
        logger.setLevel(logging.DEBUG)  

        # Create console handler with the appropriate log level
        console_output = sys.stdout if self.console_log_output.lower() == "stdout" else sys.stderr
        console_handler = logging.StreamHandler(console_output)
        try:
            console_handler.setLevel(self.console_log_level.upper())
        except ValueError as e:
            print(f"Failed to set console log level: {e}")
            return False

        # Create console formatter and add it to the console handler
        console_formatter = LogFormatter(fmt=LOG_LINE_TEMPLATE, datefmt=LOG_LINE_DATEFMT, color=self.console_log_color)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Create file handler with the appropriate log level
        log_file_path = os.path.join(self.logfile_path, self.logfile_file)
        try:
            logfile_handler = logging.FileHandler(log_file_path)
            logfile_handler.setLevel(self.logfile_log_level.upper())
        except (ValueError, Exception) as e:
            print(f"Failed to set up log file handler for '{log_file_path}': {e}")
            return False

        # Create file formatter and add it to the file handler
        logfile_formatter = LogFormatter(fmt=LOG_LINE_TEMPLATE, datefmt=LOG_LINE_DATEFMT, color=self.logfile_log_color)
        logfile_handler.setFormatter(logfile_formatter)
        logger.addHandler(logfile_handler)

        return True

