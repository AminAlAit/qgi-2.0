import glob
import pandas as pd


def read_xlsx(file_path, sheet_name):
    """dummy docstring"""

    return pd.read_excel(file_path, sheet_name = sheet_name)


def get_files_with_naming_pattern(source_folder: str, file_pattern: str):
    """dummy docstring"""

    return glob.glob(f"{source_folder}\{file_pattern}")
