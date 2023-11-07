from datetime import timedelta
import json
import time
import psutil
import time


def import_config(config_file_path: str):
    """dummy docstring"""

    with open(config_file_path, "r") as file:
        return json.load(file)


def get_stage_processes(config: dict, stage: str) -> list[dict]:
    """dummy docstring"""

    ## TODO depending on what stage `stage` is, `globals()` should be a list of
    ## functions from that stage's script. That way, we can check if the function belongs
    ## there or not.
    ## Fetching stage process functions
    # for process in config["processing"][stage]:
    #    func_name  = process["action"]
    #    # Check if the function exists in the global scope
    #    if func_name not in globals():
    #        raise ValueError(f"Function '{func_name}' not found for stage '{stage}'. ")

    return config["processing"][stage]


def take_break_seconds(seconds: int) -> None:
    time.sleep(seconds)


def take_break(duration: timedelta, multiplier: float = 1):
    """
    Pauses the script for a duration specified by the input timedelta object, multiplied by the given multiplier.

    Parameters:
    - duration (timedelta): The base duration for which to pause the script.
    - multiplier (float): The factor by which to multiply the base duration.
    """
    # Convert the duration to total seconds and apply the multiplier
    pause_seconds = duration.total_seconds() * multiplier

    # Pause the script for the calculated duration
    time.sleep(pause_seconds)


def dynamic_throttle(threshold = 50, check_interval = 5, rest_multiplier = 2):
    """
    Dynamically throttles the script execution based on CPU usage.

    Parameters:
    - threshold (int): The CPU usage percentage at which to start throttling.
    - check_interval (int): How often to check the CPU usage (in seconds).
    - rest_multiplier (float): The factor by which to increase rest time if CPU usage is above the threshold.
    """
    while True:
        # Get the current CPU usage percentage
        cpu_usage = psutil.cpu_percent(interval = 1)

        # If the CPU usage is above the threshold, rest
        if cpu_usage > threshold:
            print(f"High CPU usage detected: {cpu_usage}%. Throttling...")
            rest_time = check_interval * rest_multiplier
            time.sleep(rest_time)
        else:
            # Perform work or check again after the interval
            time.sleep(check_interval)
