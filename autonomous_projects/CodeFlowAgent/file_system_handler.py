import os
import tempfile
from typing import *

def read_file(file_path: str) -> str:
    """
    Reads the content of a file and returns it as a string.
    
    :param file_path: The path to the file to be read.
    :return: The content of the file as a string.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read file {file_path}: {e}")

def write_file(file_path: str, content: str) -> None:
    """
    Writes the given content to the specified file. If the file does not exist, it will be created.
    
    :param file_path: The path to the file where the content will be written.
    :param content: The content to be written to the file.
    """
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except Exception as e:
        raise RuntimeError(f"Failed to write to file {file_path}: {e}")

def append_to_file(file_path: str, content: str) -> None:
    """
    Appends the given content to the specified file. If the file does not exist, it will be created.
    
    :param file_path: The path to the file where the content will be appended.
    :param content: The content to be appended to the file.
    """
    try:
        with open(file_path, 'a') as file:
            file.write(content)
    except Exception as e:
        raise RuntimeError(f"Failed to append to file {file_path}: {e}")

def create_temp_file(content: Optional[str] = None) -> str:
    """
    Creates a temporary file and optionally writes the given content to it.
    
    :param content: The content to be written to the temporary file. Defaults to None.
    :return: The path to the created temporary file.
    """
    try:
        fd, temp_file_path = tempfile.mkstemp()
        os.close(fd)
        if content is not None:
            write_file(temp_file_path, content)
        return temp_file_path
    except Exception as e:
        raise RuntimeError(f"Failed to create temporary file: {e}")

def delete_file(file_path: str) -> None:
    """
    Deletes the specified file.
    
    :param file_path: The path to the file to be deleted.
    """
    try:
        os.remove(file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to delete file {file_path}: {e}")