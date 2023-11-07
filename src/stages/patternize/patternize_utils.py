from datetime import datetime
import random
import sqlite3
import string
import warnings
import numpy as np
import pandas          as pd
from src.classes.index import Index
from stumpy import stump


# Constants
PATTERNS_DB_PATH = r"/workspace/qgi\trojan 2.0\data\database\patterns_database.db"


def get_org_version_main(index: Index) -> list:
    return [index.org, index.version, index.main_polished_name]


def get_pattern_lengths_list(df: pd.DataFrame) -> list:
    min_year = df["Year"].min()
    max_year = df["Year"].max()
    return list(range(3, max_year - min_year + 1))


def get_pattern_fromIndex_matrix_profile(country_ts, pattern_length):
    # Compute the matrix profile for the current country using stumpy
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category = RuntimeWarning)
        matrix_profile = stump(country_ts, m = pattern_length)
        # stringing it for a later sqlite query injection
        matrix_profile_str = ','.join(map(str, matrix_profile))

    # Find the starting index of the most similar
    # pattern in the current country's time series
    from_index = np.argmin(matrix_profile[:, 0])
    # Extract the pattern from the current country's time series
    pattern = country_ts[from_index:from_index + pattern_length]

    return [pattern, from_index, matrix_profile_str]


def generate_unique_id(country_a: str, country_b: str, pattern_length: int, index_name: str) -> str:
    """Generate a unique ID based on the provided parameters."""
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{country_a}_{country_b}_{pattern_length}_{index_name}_{random_chars}"


def import_and_fix_csv_column_names(csv_path: pd.DataFrame, index: Index) -> pd.DataFrame:
    """
    Rename columns of a DataFrame based on a list of new column names, 
    while skipping the columns "Year" and "Country".

    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - new_column_names (list): List of new column names.

    Returns:
    - pd.DataFrame: DataFrame with renamed columns.
    """
    new_column_names = index.get_patternizable_indexes()

    # Extract current column names
    df = pd.read_csv(csv_path)
    current_columns = df.columns.tolist()

    # Remove "Year" and "Country" from the current columns list
    columns_to_rename = [col for col in current_columns if col not in ["Year", "Country"]]

    # Ensure the number of columns to rename matches the length of new_column_names
    if len(columns_to_rename) != len(new_column_names):
        raise ValueError("The number of new column names does not match the number of columns to be renamed.")

    # Create a dictionary mapping current column names to new column names
    rename_dict = {old: new for old, new in zip(columns_to_rename, new_column_names)}

    # Rename the columns
    df.rename(columns = rename_dict, inplace = True)

    return df


def sqlite_execute_query(query_params: tuple):
    conn = sqlite3.connect(PATTERNS_DB_PATH)
    cursor = conn.cursor()
    query, params = query_params
    cursor.execute(query, params)
    # Check if it's a modification query and commit if it is
    if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
        conn.commit()
        result = cursor.rowcount  # This will return the number of rows affected
    else:
        result = cursor.fetchall()  # For SELECT statements, fetch the results
    conn.close()
    return result


def is_index_patternized(org: str, version: int, main_name: str, index_name: str) -> bool:
    """
    Check if a given index has been patternized.

    Parameters:
    - conn (sqlite3.Connection): SQLite database connection.
    - org (str): Name of the organization.
    - version (integer): Year this index was made.
    - main_name (str): Main name of the index.
    - index_name (str): Name of the sub-index to check.

    Returns:
    - bool: True if the index has been patternized, otherwise False.
    """
    query  = ("SELECT 1 FROM patternized_indexes WHERE org = ? AND version = ? AND main_name = ? AND index_name = ?",
              (org, version, main_name, index_name))
    result = sqlite_execute_query(query)
    return len(result) > 0


def is_country_patternized(
    org: str,
    version: int,
    main: str,
    index_name: str,
    country_a: str,
    country_b: str,
    pattern_length: int,
    start_year_a: int,
    start_year_b: int
) -> bool:
    """
    Check if a given pattern has been patternized for a specific country and index.

    Parameters:
    ... [rest of the parameters] ...

    Returns:
    - bool: True if the pattern has been patternized, otherwise False.
    """
    query  = ("SELECT 1 FROM patterns WHERE org = ? AND version = ? AND main_name = ? AND index_name = ? AND country_a = ? AND country_b = ? AND pattern_length = ? AND start_year_a = ? AND start_year_b = ?",
              (org, version, main, index_name, country_a, country_b, pattern_length, start_year_a, start_year_b))
    result = sqlite_execute_query(query)
    return len(result) > 0


def mark_index_patternized(org: str, version: int, main_name: str, index_name: str, index_patternizing_duration: str) -> None:
    """
    Mark a given index as patternized in the database.

    Parameters:
    - conn (sqlite3.Connection): SQLite database connection.
    - org (str): Name of the organization.
    - version (int): Year this index was made.
    - main_name (str): Main name of the index.
    - index_name (str): Name of the sub-index to mark.
    - country_a_patternizing_duration (str): Duration of the patternization process. 

    Returns:
    - None
    """
    query  = ("INSERT OR IGNORE INTO patternized_indexes (org, version, main_name, index_name, processing_duration) VALUES (?, ?, ?, ?, ?)",
              (org, version, main_name, index_name, index_patternizing_duration))
    sqlite_execute_query(query)


def mark_country_patternized(org: str, version: int, main_name: str, index_name: str, country_name: str, country_a_patternizing_duration: str) -> None:
    """
    Mark a given country as patternized for a specific index in the database.

    Parameters:
    - conn (sqlite3.Connection): SQLite database connection.
    - org (str): Name of the organization.
    - version (int): Year this index was made.
    - main_name (str): Main name of the index.
    - index_name (str): Name of the sub-index.
    - country_name (str): Name of the country to mark.
    - country_a_patternizing_duration (str): Duration of the patternization process. 

    Returns:
    - None
    """
    query  = ("INSERT OR IGNORE INTO patternized_countries (org, version, main_name, index_name, country_name, processing_duration) VALUES (?, ?, ?, ?, ?, ?)",
              (org, version, main_name, index_name, country_name, country_a_patternizing_duration))
    sqlite_execute_query(query)


def identify_patterns():
    # Fetch new patternized indexes
    new_indexes = sqlite_execute_query(("SELECT * FROM patternized_indexes",))

    for index in new_indexes:
        org, version, main_name, index_name, _ = index
        # Logic to find matching patterns for the new index
        patterns = sqlite_execute_query((
            """
            SELECT country_a, country_b, pattern_length, start_year_a, start_year_b, COUNT(DISTINCT index_name) as strength, 
            GROUP_CONCAT(DISTINCT index_name) as indexes, GROUP_CONCAT(DISTINCT index_values_a) as index_values_a, 
            GROUP_CONCAT(DISTINCT index_values_b) as index_values_b
            FROM patterns
            WHERE index_name = ? AND org = ? AND version = ? AND main_name = ?
            GROUP BY country_a, country_b, pattern_length, start_year_a, start_year_b
            HAVING strength > 1
            """,
            (index_name, org, version, main_name)
        ))

        for pattern in patterns:
            country_a, country_b, pattern_length, start_year_a, start_year_b, strength, indexes, index_values_a, index_values_b = pattern
            # Check if this pattern already exists
            existing_pattern = sqlite_execute_query((
                """
                SELECT * FROM pattern_summary WHERE country_a = ? AND country_b = ? AND pattern_length = ? AND start_year_a = ? AND start_year_b = ?
                """,
                (country_a, country_b, pattern_length, start_year_a, start_year_b)
            ))

            if existing_pattern:
                # Update the existing pattern
                existing_pattern = existing_pattern[0]
                new_strength = existing_pattern[5] + 1
                new_indexes = existing_pattern[6] + ',' + index_name
                sqlite_execute_query((
                    """
                    UPDATE pattern_summary SET strength = ?, indexes = ?, last_updated = ? 
                    WHERE country_a = ? AND country_b = ? AND pattern_length = ? AND start_year_a = ? AND start_year_b = ?
                    """,
                    (new_strength, new_indexes, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), country_a, country_b, pattern_length, start_year_a, start_year_b)
                ))
            else:
                # Insert new pattern
                sqlite_execute_query((
                    """
                    INSERT INTO pattern_summary (country_a, country_b, pattern_length, start_year_a, start_year_b, strength, indexes, index_values_a, index_values_b, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (country_a, country_b, pattern_length, start_year_a, start_year_b, strength, indexes, index_values_a, index_values_b, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                ))
