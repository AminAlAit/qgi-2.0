import datetime
import sqlite3
import warnings
import pandas as pd
from scipy.stats import pearsonr
from src.stages.patternize.patternize_utils import generate_unique_id, get_org_version_main, get_pattern_fromIndex_matrix_profile, get_pattern_lengths_list, identify_patterns, import_and_fix_csv_column_names, is_country_patternized, is_index_patternized, mark_country_patternized, mark_index_patternized, sqlite_execute_query
from scipy.stats import ConstantInputWarning, NearConstantInputWarning
from src.classes.index import Index
from src.utils.utils import take_break

## Log legend
#  D: Disqualified: the algorithm is trying to find, for example, a 5 year pattern in a 3 years long index
#  S: Skipping: skipping pattern searching because index's length does not span beyond 3 years
#  S1: Saved: pattern already saved in db, skipping loop turn
#  S2: Saving: pattern is new to db, it is being saved to it
#  C1: Country patternization is done, country name saved in db table
#  C2: Country already patternized for this index, for this org, for this version
#  I1: Saved: Index patternized and already saved in db, no need to do it again, so skipping loop turn
#  I2: Index patternization is done, Index name saved in db table

## Constants
STAGE                        = "patternize"
PATTERNS_DB_PATH             = r"/workspace/qgi\trojan 2.0\data\database\patterns_database.db"
THROTTLING_THRESHOLD         = 90
THROTTLING_INTERVALS         = 10
THROTTLING_MULTIPLIER        = 1
BREAK_MULTIPLIER_COUNTRY_A   = 1
BREAK_MULTIPLIER_COUNTRY_B   = 0.05
BREAK_PATTERN_LENGTH         = 0.01
BREAK_MULTIPLIER_INDEX       = 0.1
PATTERN_IDENTIFICATION_BREAK = 0.5

def patternize_handler(processed_csv_path: pd.DataFrame, CORRELATION_THRESHOLD: float, index: Index):
    """dummy docstring"""

    df                    = import_and_fix_csv_column_names(processed_csv_path, index)
    patternizable_indexes = index.get_patternizable_indexes()

    print("Patternizing indexes...")
    for index_name in patternizable_indexes:
        index_patternizing_start_time = datetime.datetime.now()  # Start timing here

        # If index is already patternized, skip it
        if is_index_patternized(index.org, index.version, index.main_polished_name, index_name):
            print(f"I1: {index.org} - {index.version} | {index.main_polished_name} - {index_name}. ")
            continue

        ## TODO log progress between indexes here
        find_patterns(df, CORRELATION_THRESHOLD, index_name, index)

        # Marking an index as patternized in sqlite
        index_patternizing_end_time = datetime.datetime.now()  # End timing here
        index_patternizing_duration = index_patternizing_end_time - index_patternizing_start_time
        mark_index_patternized(index.org, index.version, index.main_polished_name, index_name, str(index_patternizing_duration))
        take_break(index_patternizing_duration, BREAK_MULTIPLIER_INDEX)

        # Pattern identification
        pattern_identification_start_time = datetime.datetime.now()
        identify_patterns()
        pattern_identification_end_time = datetime.datetime.now()  # End timing here
        pattern_identification_duration = pattern_identification_end_time - pattern_identification_start_time
        take_break(pattern_identification_duration, PATTERN_IDENTIFICATION_BREAK)
        
        print(f"I2: {index.org} - {index.version} | {index.main_polished_name} - {index_name}. ")

    print("Patternizing has concluded. ")


def find_patterns(df: pd.DataFrame, correlation_threshold: float, index_name: str, ind: Index):
    """
    Identify and compare patterns in time series data of countries based on a specified index.

    The function extracts patterns from the time series data of a specified country 
    (or all countries if not specified) and compares them with patterns from another 
    country (or all countries if not specified) based on their Pearson correlation.
    Only patterns with a correlation above the specified threshold are considered.

    Parameters:
    - df (pd.DataFrame): The input dataframe containing columns "Year", "Country", 
        and the specified index name.
    - correlation_threshold (float): The minimum Pearson correlation required 
        to consider two patterns as similar.
    - index_name (str): The name of the column in the dataframe that contains 
        the time series data to be analyzed.
    - country_A (str, optional): The name of the country from which patterns are 
        to be extracted. If not provided, all countries are considered.
    - country_B (str, optional): The name of the country with which patterns from 
        country_A are to be compared. If not provided, all countries are considered.
    - pattern_lengths_list (list, optional): List of integers representing the lengths 
        of patterns to be considered. If not provided, it's generated based on the 
        range of years in the dataset.

    Returns:
    - pd.DataFrame: A dataframe containing details of the identified patterns, 
        their start and end years, correlation values, and other related information.

    Note:
    - The function uses the STUMPY library for matrix profile computation to 
        identify patterns in time series data.
    - Patterns with a length less than 3 years are not considered.
    - The function generates a unique ID for each identified pattern 
        combination for tracking purposes.
    """
    print("Patternizing Index:", index_name)

    # Getting neccessary vars
    org, version, main   = get_org_version_main(ind)       # Fetching class essentials
    countries_in_df      = df["Country"].unique().tolist() # List of countries in the dataframe
    pattern_lengths_list = get_pattern_lengths_list(df)  # Generate it based on the range of years in the dataset minus one.

    # Ensure pattern_length is at least 3
    if min(pattern_lengths_list) < 3:
        # Ensure pattern_length is at least 3
        disqualified_reason = f"Pattern length {min(pattern_lengths_list)} is less than 3 years."
        print(f"Index {index_name} is disqualified from patternizing: {disqualified_reason}")
        # Insert into disqualified_indexes table
        sqlite_execute_query((
            '''
            INSERT INTO disqualified_indexes (org, version, main_name, index_name, reason) VALUES (?, ?, ?, ?, ?)
            ''',
            (org, version, main, index_name, disqualified_reason)
        ))
        return None

    patternized_countries_query = '''
    SELECT country_name FROM patternized_countries WHERE org = ? AND version = ? AND main_name = ? AND index_name = ?
    '''
    patternized_countries = sqlite_execute_query((patternized_countries_query, (org, version, main, index_name)))
    patternized_countries_list = [country[0] for country in patternized_countries]

    for country_a in countries_in_df:
        # Exit condition: country already patternized
        if country_a in patternized_countries_list:
            print(f"C2: {country_a} | {org} - {version} - {main} - {index_name}")
            continue
        
        country_a_patternizing_start_time = datetime.datetime.now()  # Start timing here

        for pattern_length in pattern_lengths_list:
            # Extract the time series for the current country_a
            country_ts = df[df["Country"] == country_a][index_name].values

            # Check if the pattern_length is valid for the current country's time series
            if pattern_length > len(country_ts):
                print(f"{index_name} | {country_a}- S {pattern_length} - {len(country_ts)}")
                continue

            # Compute the matrix profile for the current country using stumpy
            pattern, from_index, matrix_profile = get_pattern_fromIndex_matrix_profile(country_ts, pattern_length)

            # Register starting time for country_b loop
            country_b_patternizing_start_time = datetime.datetime.now()

            # Iterate over countries_to_compare to find patterns
            for country_b in countries_in_df:

                if country_b == country_a:
                    continue

                other_country_df = df[df["Country"] == country_b]
                other_country_ts = other_country_df[index_name].values

                patt_len_patternizing_start_time = datetime.datetime.now()

                for i in range(len(other_country_ts) - pattern_length + 1):
                    other_pattern = other_country_ts[i: i + pattern_length]

                    ## Try/except block is here just to supress warnings coming out of `pearsonr`.
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", category = ConstantInputWarning)
                            warnings.simplefilter("ignore", category = NearConstantInputWarning)
                            corr, _ = pearsonr(pattern, other_pattern)
                    except Exception as e:
                        print(f"Patternize Error: {e}")

                    if corr >= correlation_threshold:
                        start_year_a   = int(df[df["Country"] == country_a]["Year"].iloc[from_index])                      # Start Year A
                        end_year_a     = int(df[df["Country"] == country_a]["Year"].iloc[from_index + pattern_length - 1]) # End Year A
                        index_values_a = ','.join(map(str, pattern))                                                       # Index Values A
                        start_year_b   = int(other_country_df["Year"].iloc[i])                                             # Start Year B
                        end_year_b     = int(other_country_df["Year"].iloc[i + pattern_length - 1])                        # End Year B
                        index_values_b = ','.join(map(str, other_pattern))                                                 # Index Values B
                        creation_date  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")                             # Creation Date
                        unique_id      = generate_unique_id(country_a, country_b, pattern_length, index_name)

                        if not is_country_patternized(org, version, main, index_name, country_a, country_b, pattern_length, start_year_a, start_year_b):
                            # Insert the pattern into the SQLite database
                            print(f"S2: {index_name} | {country_a} ({start_year_a}) - {pattern_length} - ({start_year_b}) {country_b}. ")
                            sqlite_execute_query((
                                '''
                                INSERT INTO patterns (
                                    org, version, main_name, index_name, country_a, country_b, pattern_length, correlation,
                                    start_year_a, end_year_a, index_values_a,
                                    start_year_b, end_year_b, index_values_b,
                                    creation_date, matrix_profile, unique_id
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''',
                            (org, version, main, index_name, country_a, country_b, pattern_length, corr, start_year_a, end_year_a, index_values_a,
                                start_year_b, end_year_b, index_values_b, creation_date,
                                matrix_profile,
                                unique_id
                            )))
                        else:
                            print(f"S1: {index_name} | {country_a} ({start_year_a}) - {pattern_length} - ({start_year_b}) {country_b}. ")

                    # Else, corr < 0.5

                ## Loop that patternizes pattern lengths ends here
                ## TODO better logging?
                patt_len_patternizing_end_time = datetime.datetime.now()
                patt_len_patternizing_duration = patt_len_patternizing_end_time - patt_len_patternizing_start_time
                take_break(patt_len_patternizing_duration, BREAK_PATTERN_LENGTH)

            ## Loop that Patternizes Country B ends here
            ## TODO better logging?
            
            # Register ending time and duration for country_b loop, then take a break
            country_b_patternizing_end_time = datetime.datetime.now()
            country_b_patternizing_duration = country_b_patternizing_end_time - country_b_patternizing_start_time
            take_break(country_b_patternizing_duration, BREAK_MULTIPLIER_COUNTRY_B)

        ## Loop that patternizes Country A ends here
        ## TODO better logging?

        # Marking Country A as patternized in sqlite
        country_a_patternizing_end_time = datetime.datetime.now()  # End timing here
        country_a_patternizing_duration = country_a_patternizing_end_time - country_a_patternizing_start_time
        mark_country_patternized(org, version, main, index_name, country_a, str(country_a_patternizing_duration))

        # Logging to terminal
        # Execute the query and fetch the results
        current_patterns_count = sqlite_execute_query(("SELECT COUNT(*) FROM patterns", ()))[0][0]

        # Extract the count from the result
        print("C1: {:<10} | {:<15} | {:<10} | {:<10}".format(index_name, country_a, current_patterns_count, str(country_a_patternizing_duration)))

        # Take a break
        take_break(country_a_patternizing_duration, BREAK_MULTIPLIER_COUNTRY_A)
