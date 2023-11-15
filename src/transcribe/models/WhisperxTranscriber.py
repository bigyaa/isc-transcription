# *************************************************************************************************************************
#   WhisperxTranscriber.py 
#       This module contains the WhisperxTranscriber class, which utilizes the Whisper speech recognition library to 
#       transcribe audio files. It supports batch processing, multiple compute types, and integrates diarization for 
#       identifying different speakers within the audio.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#      from WhisperxTranscriber import WhisperxTranscriber
#      transcriber = WhisperxTranscriber(model_size='base', hf_token='your_hf_token', audio_files='sample.mp3')
#      transcriber.transcribe()
#
#      Parameters:
#         model_size - The size of the Whisper model to use (e.g., 'tiny', 'base', 'small', 'medium', 'large')
#         hf_token - Hugging Face authentication token for using models hosted on Hugging Face
#         audio_files - The path to the audio file to transcribe
#         batch_size - The number of audio segments to process simultaneously (default=16)
#         compute_type - The type of computation (precision) to use, such as 'int8' or 'float16' (default='int8')
#
#      Outputs (on successful transcription):
#         A text file for the input audio file, containing the transcribed text with timestamps and speaker identification.
#
#   Design Notes:
#   -.  The WhisperxTranscriber is built to utilize CPU resources by default but can be adapted to use GPU.
#   -.  It incorporates a diarization pipeline to differentiate between speakers in the audio.
#   -.  Aligned segments with speaker labels are produced to enhance the readability of the transcript.
# ---------------------------------------------------------------------------------------------------------------------
#   TODO:
#   -.  Add support for GPU-based diarization and transcription for performance improvements.
#   -.  Error handling for unsupported audio formats and failed transcription attempts.
#   -.  Option to output aligned segments with character-level alignments.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  November 2023
#   authors:       Reuben Maharaj, Bigya Bajarcharya, Mofeoluwa Jide-Jegede
# *************************************************************************************************************************

import os
from typing import List
import whisperx
from whisperx import load_audio, DiarizationPipeline, load_align_model, align, assign_word_speakers
import logging
import subprocess

# Setup logger for informational output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class WhisperxTranscriber:
    """
    Transcribes audio using the Whisper speech recognition library with added diarization.
    """
    def __init__(self, model_size: str, hf_token: str, audio_files: str, batch_size: int = 16, compute_type: str = "int8"):
        """
        Initializes the transcriber with the given model size, Hugging Face token, audio file path, and optional batch size and compute type.
        """
        self.model_size = model_size
        self.hf_token = hf_token
        self.audio_files = audio_files
        self.batch_size = batch_size
        self.compute_type = compute_type
        self.model = whisperx.load_model(model_size, device="cpu", compute_type=self.compute_type)

    def transcribe(self):
        for audio in self.audio_files:
            waveform = load_audio(audio)
            result = self.model.transcribe(waveform, batch_size=self.batch_size)
            base_name = os.path.splitext(os.path.basename(audio))[0]
            output_file_path = f"{base_name}.txt"
            
            with open(output_file_path, "w+") as output_file:
                for segment in result["segments"]:
                    output_file.write(f"{segment['start']} {segment['end']} {segment['text']}\n")
    
    
    def transcribe(self):
        """
        Performs transcription of the specified audio file, including diarization to identify and label different speakers.
        Outputs a .txt file with time-stamped transcriptions.
        """
        logger.info(f"Loading {self.model_size} model")
        diarize_model = DiarizationPipeline(use_auth_token=self.hf_token, device="cpu")

        #todo: integrate traversal branch
        audio=self.audio_files
        logger.info(f"Transcribing audio file: {audio}")
        waveform = load_audio(audio)
        result = self.model.transcribe(waveform, batch_size=self.batch_size)
        base_name = os.path.splitext(os.path.basename(audio))[0]
        output_file_path = f"{base_name}.txt"
        logger.info(f"Writing transcription to file: {output_file_path}")

        diarize_segments = diarize_model(audio)
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device='cpu')

        aligned_segments = whisperx.align(result['segments'], model_a, metadata, audio, "cpu", return_char_alignments=False)
        segments_with_speakers = whisperx.assign_word_speakers(diarize_segments, aligned_segments)

        with open(output_file_path, "w+") as output_file:
            for segment in segments_with_speakers["segments"]:
                output_file.write(f"{segment['start']} {segment['end']} {segment['text']}\n")

        logger.info(f"Finished writing transcription to file: {output_file_path}")


        # # Define the base command
        # command = "whisperx" #todo: integrate directory traversal

        # # Define optional flags and their values
        # optional_flags = {
        #     "--compute_type": self.compute_type,
        #     # "--hf_token": self.hf_token,
        #     # "--model": self.model_size,
        #     # "--batch_size": self.batch_size,
        #     # "--output_dir": "output_dir",
        #     # "--language": "en"
        #     # "--diarize": "false"
        # }

        # # Construct the command and its arguments
        # args = [command]
        # for flag, value in optional_flags.items():
        #     if value is not None:
        #         args.extend([flag, value])
        # if self.audio_files:
        #     args.append(self.audio_files)
        # # Run the command using subprocess
        # # try:
        #     completed_process = subprocess.run(args, check=True, stderr=subprocess.PIPE, text=True, shell=True)
        #     print(".......", completed_process.stderr) 
        # # except subprocess.CalledProcessError as e:
        # #     print(f"Error running the command: {e}")