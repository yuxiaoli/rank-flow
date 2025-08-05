import zipfile
import os
import csv
from pathlib import Path
from typing import List, Dict, Any, Generator

def unzip(filename: str, path: str) -> None:
    """Extract zip file to specified path"""
    print(f"Extracting {filename} to {path} ...")
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(path)

def iterate_directory(directory: str) -> Generator[str, None, None]:
    """Recursively iterate through directory and yield file paths"""
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    for file_path in directory_path.rglob('*'):
        if file_path.is_file():
            yield str(file_path)
