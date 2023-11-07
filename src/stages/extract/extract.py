from src.stages.extract.extract_utils import read_xlsx, get_files_with_naming_pattern
from src.utils.utils                  import import_config, get_stage_processes

STAGE = "extract"

def extract_handler(config_file_path: str):
    """dummy docstring"""

    config    = import_config(config_file_path)
    processes = get_stage_processes(config, STAGE)

    print("Extraction in progress... ")
    for process in processes:
        # Call the function with the specified parameters
        func_name  = process["action"]
        parameters = process["parameters"]
        func       = globals()[func_name]
        result     = func(**parameters)

    print("Extraction has concluded. ")
    return result


def extract_one_sheet_data_from_xlsx_pattern(sheet_position: int, folder: str, file_pattern: str):
    """dummy docstring"""

    files      = get_files_with_naming_pattern(folder, file_pattern)
    dataframes = []
    for file in files:
        df = read_xlsx(file, sheet_position)
        dataframes.append(df)

    return dataframes
