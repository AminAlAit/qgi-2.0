import pandas as pd
from src.utils.utils import get_stage_processes, import_config


STAGE = "load"


def load_handler(config_file_path: str, result: pd.DataFrame):
    """dummy docstring"""

    config    = import_config(config_file_path)
    processes = get_stage_processes(config, STAGE)

    print("Loading in progress...")
    for process in processes:
        func_name  = process["action"]
        parameters = process["parameters"]
        func       = globals()[func_name]
        result     = func(result, **parameters)

    print("Loading has concluded.")
    return result


def save_csv(df: pd.DataFrame, destination_folder: str, file_name_pattern: str, index_name: str):
    """dummy docstring"""

    file_name = file_name_pattern.format(index_name = index_name)
    path      = f"{destination_folder}{file_name}"
    df.to_csv(path, index = False)
    return path
