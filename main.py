import os
from src.etlp.etlp import process_pipeline_for_config


CONFIGS_DIR           = r"/workspace/qgi\trojan 2.0\config"
CORRELATION_THRESHOLD = 0.5


def main():
    """
    Main function to execute the ETLP (Extract, Transform, Load, Patternize) pipeline.

    This function iterates over all JSON config files located in the CONFIGS_DIR directory.
    For each config file, it triggers the ETLP pipeline to process the data as specified
    in the config.

    TODOs:
    - Optimize all stage and helper/utils functions.
    - Delete cache and CSVs after the end of a pipeline's job.
    - Implement a garbage collection script and set up its timer events.
    """
    # Loop over all files in the directory
    for file_name in os.listdir(CONFIGS_DIR):
        # Check if the file is a JSON config file
        if file_name.endswith(".json"):
            config_file_path = os.path.join(CONFIGS_DIR, file_name)
            process_pipeline_for_config(config_file_path, CORRELATION_THRESHOLD)

    ## TODO optimize all stage and helper/utils functions.
    ## TODO delete cache and CSVs after end of a pipeline's job: create a garbage compiler script, create its timer events
    ## TODO fix all docstrings, a lot of functions have been modified.

if __name__ == "__main__":
    main()
