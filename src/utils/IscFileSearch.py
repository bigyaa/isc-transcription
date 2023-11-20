# *************************************************************************************************************************
#   IscFileSearch.py 
#       This module contains the IscFileSearch class that provides functionality to search, retrieve, and manipulate
#       files within a specified directory. It is designed to perform common file operations such as traversing directories, 
#       renaming files, deleting files, and getting file properties.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       The IscFileSearch class can be imported and instantiated with a directory path. It provides methods to:
#       - Traverse directories and find files with specific extensions.
#       - Retrieve files with certain extensions within the given directory.
#       - Delete files and handle deletions with proper error checking.
#       - Rename files with an option to overwrite existing files.
#       - Get file properties such as size and modification time.
#
#       from src.utils.IscFileSearch import IscFileSearch
#       file_search = IscFileSearch('path/to/directory')
#       files = file_search.get_files(['mp3', 'wav'])
#       file_search.delete_file('path/to/file.mp3')
#       file_search.rename_file('old_name.mp3', 'new_name.mp3', overwrite=True)
#       properties = file_search.get_file_properties('path/to/file.mp3')
#
#   Design Notes:
#   -.  The class utilizes the os module to interact with the filesystem.
#   -.  Includes comprehensive error handling to ensure robust file operations.
#   -.  Provides logging for each operation to track the behavior and potential issues.
#   -.  Designed to be a utility within a larger system, such as a transcription application.
# ---------------------------------------------------------------------------------------------------------------------
#   TODO:
#   -.  Extend functionality to support more file operations as needed.
#   -.  Implement additional file property retrieval, such as file permissions.
#   -.  Optimize file traversal with more efficient search patterns or parallel processing.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  November 2023
#   authors:       Reuben Maharaj, Bigya Bajarcharya, Mofeoluwa Jide-Jegede
# *************************************************************************************************************************
# ***********************************************
# imports
# ***********************************************

# os - operating system interface
#   path.join - join one or more path components intelligently
#   path.exists - check if a path exists
#   path.isdir - check if a path is a directory
#   path.isfile - check if a path is a regular file
#   path.basename - get the base name of a path
#   listdir - list the names of the entries in the directory given by path
#   walk - generate the file names in a directory tree by walking the tree either top-down or bottom-up
#   remove - remove a file (delete)
#   rename - rename the file or directory
#   stat - get the status of a file or a file descriptor

# logging - logging library
#   getLogger - function to get a logging instance
#   basicConfig - function to configure the logging
#   error - log an error message
#   info - log an informational message
#   warning - log a warning message

import os
import logging

logger = logging.getLogger()

class IscFileSearch:
    def __init__(self, path):
        """
        Initializes the IscFileSearch class with a path attribute and a logger attribute from the logging module.
        """
        self.path = path
        
    
    def traverse_directory(self, path=None):
        """
        Recursively traverses a directory and returns a list of file paths for all
        files that end with .mp3 or .wav.
        """
        if path is None:
            path = self.path
        
        def handle_error(error, dirpath):
            logger.error("Failed to traverse directory %s: %s", dirpath, error)
    
        if not os.path.exists(path):
            logger.error("Directory does not exist: %s", path)
            return []

        file_paths = []
    
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
            
                if file_path.lower().endswith(('.mp3', '.wav')):
                    file_paths.append(file_path)
        
            # handle errors after processing files in the current directory
            try:
                for dirname in dirnames:
                    os.listdir(os.path.join(dirpath, dirname))
            except OSError as error:
                handle_error(error, dirpath)
            
        return file_paths
    
    def get_files(self, file_exts=['mp3', 'wav']):
        """
        Returns a list of file paths in the directory whose extensions are in the specified file_exts parameter.
        """
        if not os.path.exists(self.path):
            logger.error("Directory does not exist: %s", self.path)
            return []
    
        return [os.path.join(self.path, file) for file in os.listdir(self.path) 
                if os.path.isfile(os.path.join(self.path, file)) 
                and file.lower().rsplit('.')[-1] in file_exts]

    def delete_file(self, file_path):
        """
        Deletes a file at the specified path.
        """
        if not os.path.exists(file_path):
            logger.error("File does not exist: %s", file_path)
            return
        
        os.remove(file_path)
        logger.info("File deleted: %s", file_path)
    
    
    def rename_file(self, old_name, new_name, overwrite=False):
        """
        Renames a file in the directory from old_name to new_name and returns a status code.
        If overwrite is set to True and a file with new_name already exists, it will be overwritten.
        """
        old_path = os.path.join(self.path, old_name)
        new_path = os.path.join(self.path, new_name)

        if not os.path.exists(old_path):
            logger.error("File does not exist: %s", old_path)
            return 1

        if os.path.exists(new_path) and not overwrite:
            logger.warning("File already exists with new name: %s", new_name)
            user_input = input("Do you want to overwrite the existing file? (y/n)").lower()
            if user_input != "y":
                logger.warning("File was not renamed: %s", old_name)
                return 2

        try:
            os.rename(old_path, new_path)
            logger.info("File renamed from %s to %s", old_name, new_name)
            return 0

        except OSError as e:
            logger.error("Failed to rename file %s to %s: %s", old_name, new_name, str(e))
            return 3

          
    def get_file_properties(self, file_path):
        """
        Returns a dictionary of properties for the file at the specified path, including
        file name, file size, creation time, modified time, and access time.
        """
        if not os.path.exists(file_path):
            logger.error("File does not exist: %s", file_path)
            return None
        
        file_stats = os.stat(file_path)
        
        return {
            "file_name": os.path.basename(file_path),
            "file_size": file_stats.st_size,
            "creation_time": file_stats.st_ctime,
            "modified_time": file_stats.st_mtime,
            "access_time": file_stats.st_atime,
        }