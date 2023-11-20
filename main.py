# *************************************************************************************************************************
#   main.py 
#       This is the entry point for the transcription application using the WhisperxTranscriber. It handles command-line 
#       arguments, sets up logging, validates XML configuration, and initiates the transcription process.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#      python main.py --audio [path_to_audio_file] --configxml [path_to_config_file] [Other_Arguments]
#      Arguments and defaults:
#         -a, --audio [path] : Specify the path to the input audio file to be transcribed.
#         -cx, --configxml [path] : Specify the path to the XML configuration file. Default 'config/default_config.xml'
#         -mt, --model_type [type] : Specify the Whisper model type for transcription. Default 'base'
#         -ad, --audiodir [dir] : Specify the directory of audio files to transcribe. Default 'audio_files'
#         -td, --transcriptiondir [dir] : Specify the directory to store transcriptions. Default 'transcriptions'
#         -ht, --hf_token [token] : Hugging Face authentication token for using models with diarization.
#         -e, --extensions [ext] : List of audio file extensions in audiodir. Default ['.mp3', '.wav', '.aac']
#      Outputs:
#         Initiates the transcription process and outputs transcription files in the specified directory.
#         Generates logs of the application's activities and errors.
# ---------------------------------------------------------------------------------------------------------------------
#   TODO:
#   -.  Improve error handling for command-line argument parsing and XML validation.
#   -.  Extend the application to handle different input/output formats and sources.
#   -.  Refactor the code for better modularity and testability.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  November 2023
#   authors:       Reuben Maharaj, Bigya Bajarcharya, Mofeoluwa Jide-Jegede
# *************************************************************************************************************************
# ***********************************************
# imports
# ***********************************************

# os - for file path operations
#   getcwd - get the current working directory
#   path.exists - check if a path exists
#   path.join - join one or more path components intelligently

# argparse - for command line argument parsing
#   ArgumentParser - create a parser object to hold argument information
#   add_argument - define how a single command-line argument should be parsed

# lxml.etree - for XML parsing and validation
#   parse - parse an XML document into an element tree
#   XMLSchema - validate an XML document against XML Schema

# datetime - for generating timestamped log files
#   datetime.now - get the current date and time
#   strftime - format a date or time according to the specified format

# Custom packages for the transcription model and utilities
# src.transcribe.models.WhisperxTranscriber - custom package for the transcription model
#   WhisperxTranscriber - class to handle transcription process using Whisper models

# src.utils.ISCLogWrapper - custom wrapper for logging functionalities
#   ISCLogWrapper - class to configure and initiate logging
#   logging.getLogger - method to return a logger instance with the specified name

# src.utils.TranscriptionConfig - custom configuration handler for transcription settings
#   TranscriptionConfig - class to manage transcription configuration from an XML file

import os
import argparse
from lxml import etree
from datetime import datetime
from src.transcribe.models.WhisperxTranscriber import WhisperxTranscriber
from src.utils.ISCLogWrapper import ISCLogWrapper, logging
from src.utils.TranscriptionConfig import TranscriptionConfig
import ssl
import certifi

ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())


# Default values
DEFAULT_XML_CONFIG = 'config/default_config.xml'
DEFAULT_SCHEMA_FILE = 'config/config_schema.xsd'
DEFAULT_TRANSCRIPTION_DIR = 'transcriptions'
DEFAULT_LOG_FILE = 'logs/ISC_DefaultLog.log'
DEFAULT_FILE_EXTENSIONS = ['.mp3', '.wav', '.aac']
DEFAULT_AUDIO = 'sample/Sample.mp3'  # Default audio file if no other source is specified
ALLOWED_MODEL_TYPES = ['tiny', 'base', 'small', 'medium', 'large']
DEFAULT_MODEL_TYPE = 'base'
DEFAULT_LOGGING_CONFIG = {
    'console_log_output': "stdout",
    'console_log_level': "info",
    'console_log_color': True,
    'logfile_file': datetime.now().strftime('ISC_%H_%M_%d_%m_%Y.log'),
    'logfile_log_level': "debug",
    'logfile_log_color': False,
    'logfile_path': "logs"
}

def setup_logging():
    isc_log_wrapper = ISCLogWrapper(**DEFAULT_LOGGING_CONFIG)
    if not isc_log_wrapper.set_up_logging():
        print("Failed to set up logging, aborting.")
        sys.exit(1)
    return logging.getLogger(__name__)

logger = setup_logging()

def parse_command_line_args():
    parser = argparse.ArgumentParser(description="Process command-line arguments for audio transcription.")
    parser.add_argument("-a", "--audio", help="Specify the input audio file")
    parser.add_argument("-cx", "--configxml", help="Specify the input xml config file", default=DEFAULT_XML_CONFIG)
    parser.add_argument("-mt", "--model_type", help="Specify the model type for transcription", default='base')
    parser.add_argument("-ad", "--audiodir", help="Specify the directory of audio to transcribe", default=DEFAULT_TRANSCRIPTION_DIR)
    parser.add_argument("-td", "--transcriptiondir", help="Specify the directory to store transcriptions", default=DEFAULT_TRANSCRIPTION_DIR)
    parser.add_argument("-ht", "--hf_token", help="Specify the user token needed for diarization")
    parser.add_argument("-e", "--extensions", nargs='+', help="List of audio extensions in audiodir", default=DEFAULT_FILE_EXTENSIONS)
    return parser.parse_args()

def validate_configxml(xml_file, xsd_file, logger):
    try:
        xml_doc = etree.parse(xml_file)
        schema = etree.XMLSchema(file=xsd_file)
        schema.assertValid(xml_doc)
        logger.info("XML document is valid according to the schema.")
    except etree.XMLSchemaParseError as xspe:
        logger.error("XML Schema is not valid: {}".format(xspe))
    except etree.DocumentInvalid as di:
        logger.error("XML document is not valid: {}".format(di))
    except Exception as e:
        logger.error("An error occurred during XML validation: {}".format(e))

def main():
    args = parse_command_line_args()
    logger = setup_logging()
    validate_configxml(args.configxml, DEFAULT_SCHEMA_FILE, logger)
    
    config = TranscriptionConfig(args.configxml)
    audio_source = args.audio if args.audio is not None else config.get('audiodir')
    if not audio_source:
        logger.error("No valid audio directory specified. Transcription cannot proceed.")
        return

    model_type = args.model_type if args.model_type in ALLOWED_MODEL_TYPES else DEFAULT_MODEL_TYPE
    hf_token = config.get('settings/hf_token')
    model = WhisperxTranscriber(model_type, hf_token, audio_source)
    
    if os.path.exists(audio_source):
        logger.info("Starting Transcription.")
        model.transcribe()
    else:
        logger.error("Cannot access audio file: {}".format(audio_source))

if __name__ == '__main__':
    main()