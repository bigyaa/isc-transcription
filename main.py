# *************************************************************************************************************************
#   main.py 
#       This is the entry point for the transcription application using the WhisperxTranscriber. It handles command-line 
#       arguments, sets up logging, validates XML configuration, and initiates the transcription process.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#      python main.py --audio [path_to_audio_file] --configxml [path_to_config_file] [Other_Arguments]
#
#      Arguments:
#         --audio - Specify the path to the input audio file to be transcribed.
#         --configxml - Specify the path to the input XML configuration file.
#         --model_type - Specify the Whisper model type for transcription.
#         --audiodir - Specify the directory of audio files to transcribe.
#         --transcriptiondir - Specify the directory where transcriptions should be stored.
#         --hf_token - Hugging Face authentication token for using models with diarization.
#         --extensions - List of audio file extensions to be considered in the specified audio directory.
#
#      Outputs:
#         Initiates the transcription process and outputs transcription files in the specified directory.
#         Generates logs of the application's activities and errors.
#
#   Design Notes:
#   -.  The application is configured to be flexible with user inputs for audio sources and transcription settings.
#   -.  It utilizes an XML configuration file for setting up transcription parameters and validates it against a schema.
#   -.  Transcription is handled by creating an instance of WhisperxTranscriber and calling its transcribe method.
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
#
# os - for file path operations
# sys -
# glob - for retrieving files matching a certain pattern
# argparse - for command line argument parsing
# lxml.etree - for XML parsing and validation
# src.transcribe.models.Whisper - custom package for the transcription model
# datetime - for generating timestamped log files
# src.utils.ISCLogWrapper - custom wrapper for logging functionalities
# src.utils.TranscriptionConfig - custom configuration handler for transcription settings


import os
import sys
import glob
import argparse
from lxml import etree
from src.transcribe.models.WhisperxTranscriber import WhisperxTranscriber
from datetime import datetime
from src.utils.ISCLogWrapper import ISCLogWrapper, logging
from src.transcribe.TranscribeFactory import TranscribeFactory
from src.utils.TranscriptionConfig import TranscriptionConfig

default_audio='sample/Sample.mp3'

def setup_logging():
    isc_log_wrapper = ISCLogWrapper(
        console_log_output="stdout",
        console_log_level="info",
        console_log_color=True,
        logfile_file=datetime.now().strftime('ISC_%H_%M_%d_%m_%Y.log'),
        logfile_log_level="debug",
        logfile_log_color=False,
        logfile_path="logs"
    )
    if not isc_log_wrapper.set_up_logging():
        print("Failed to set up logging, aborting.")
        return 1
    return logging.getLogger(__name__)


logger = setup_logging()


def parse_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", help="Specify the input audio file")
    parser.add_argument(
        "--configxml", help="Specify the input xml config file")

    # new arguments
    parser.add_argument(
        "--model_type", help="Specify the model type for transcription")
    parser.add_argument(
        "--audiodir", help="Specify the directory of audio to transcribe")
    parser.add_argument("--transcriptiondir",
                        help="Specify the directory to store transcriptions")
    parser.add_argument(
        "--hf_token", help="Specify the user token needed for diarization")
    parser.add_argument(
        "--extensions", help="List of audio extensions in audiodir")

    return parser.parse_args()


def get_audio_source(config, cmd_audio, cmd_config, logger):
    if cmd_audio:
        logger.info('Starting transcription with cmd_audio audio directory')
        return cmd_audio

    if cmd_config and cmd_config.endswith('.xml'):
        try:
            extract_config = TranscriptionConfig(cmd_config)
            if 'audiodir' in extract_config:
                logger.info(
                    'Starting transcription with cmd_config audio directory')
                return extract_config.get('audiodir')
            else:
                logger.error(
                    "The configuration file does not contain 'audiodir'.")
        except Exception as e:
            logger.error("Error while reading the configuration file:", e)
    else:
        logger.error(
            "Wrong file name or extension for the configuration file.")

    default_audio = config.get('audiodir')
    if default_audio:
        logger.info('Starting transcription with default audio directory')
        return default_audio

    logger.error(
        "No valid audio directory specified. Transcription cannot proceed.")
    return default_audio


def validate_configxml(xml_file, xsd_file):
    # Load the XML file
    # xml_file = "config.xml"
    # xsd_file = "config_schema.xsd"  # Path to your XSD file

    # Parse the XML file
    xml_doc = etree.parse(xml_file)

    # Load the XML schema
    schema = etree.XMLSchema(file=xsd_file)

    logger.info('Validating to check if the xml meets schema requirements')

    # Validate the XML document against the schema
    try:
        schema.assertValid(xml_doc)
        logger.info("XML document is valid according to the schema.")
    except Exception as e:
        logger.error("XML document is not valid according to the schema.", e)


def main():
    path1 = os.getcwd()
    path = os.path.join(path1, "config/dev_config.xml")
    config = TranscriptionConfig(path)

    validate_configxml("config/dev_config.xml", "./config_validator.xsd")
    args = parse_command_line_args()
    audio = get_audio_source(config, args.audio, args.configxml, logger)

    hf_token = config.get('settings/hf_token')
    if audio:
        logger.info("Starting Transcription.")
        logger.info("CWD: " + os.getcwd())
        model = WhisperxTranscriber("small", hf_token, audio)
        model.transcribe()
    else:
        logger.error("Cannot access audio file")


if __name__ == '__main__':
    main()