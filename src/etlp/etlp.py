from src.stages.extract.extract       import extract_handler
from src.stages.patternize.patternize import patternize_handler
from src.stages.transform.transform   import transform_handler
from src.stages.load.load             import load_handler
from src.classes.index                import Index


def process_pipeline_for_config(config_file_path: str, corr_thr: float) -> None:
    """
    Process the ETLP pipeline for a given config file.

    Parameters:
    - config_file_path (str): Path to the JSON config file.

    Returns:
    - None
    """
    # Init
    ind = Index(config_file_path)

    # Extract
    extracted_data = extract_handler(config_file_path)

    # Transform
    transformed_data = transform_handler(config_file_path, extracted_data)

    # Load
    processed_csv_path = load_handler(config_file_path, transformed_data)

    # Patternize
    patternize_handler(processed_csv_path, corr_thr, ind)
