from typing import Any, List
import numpy as np
import pandas as pd
from src.utils.utils import import_config, get_stage_processes


STAGE              = "transform"
COUNTRIES_CSV_PATH = r"/workspace/qgi\trojan 2.0\data\countries\countries.csv"

def transform_handler(CONFIG_FILE_PATH: str, result: Any):
    """dummy docstring"""

    config    = import_config(CONFIG_FILE_PATH)
    processes = get_stage_processes(config, STAGE)

    print("Transformation in progress...")
    for process in processes:
        func_name  = process["action"]
        parameters = process["parameters"]
        func       = globals()[func_name]
        result     = func(result, **parameters)

    print("Transformation has concluded. ")
    return result


def extract_columns_from_dataframe(df: pd.DataFrame, cols_to_extract: List[str]):
    """dummy docstring"""
    return df[cols_to_extract]


def extract_columns_from_dataframes(
    dataframes_list: List[pd.DataFrame],
    cols_to_extract: List[str]):
    """dummy docstring"""

    # Extract the relevant columns from each dataframe
    extracted_dataframes = [extract_columns_from_dataframe(df, cols_to_extract) \
                                for df in dataframes_list]

    return extracted_dataframes


def concatenate_dataframes(dataframes: List[pd.DataFrame], columns: List[str]) -> pd.DataFrame:
    """
    Concatenate a list of dataframes row-wise based on specific columns.

    Parameters:
    - dataframes (List[pd.DataFrame]): List of dataframes to concatenate.
    - columns (List[str]): List of column names to consider for concatenation.

    Returns:
    - pd.DataFrame: Concatenated dataframe based on the specified columns.

    Example:
    >>> df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4], 'C': [5, 6]})
    >>> df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8], 'C': [9, 10]})
    >>> concatenate_dataframes([df1, df2], columns=['A', 'B'])
       A  B
    0  1  3
    1  2  4
    2  5  7
    3  6  8
    """
    # Filter each dataframe based on the specified columns before concatenating
    filtered_dataframes = [df[columns] for df in dataframes]
    return pd.concat(filtered_dataframes, ignore_index = True)


def convert_year_col_to_string_yyyy(df: pd.DataFrame) -> pd.DataFrame:
    ### OPTIMIZED
    """
    Convert the 'Year' column of a DataFrame from a datetime-like string format 
    ("2006-01-01 00:00:00") or other formats to an integer format (2006).
    
    The function ensures that the 'Year' column is of type string, extracts the 
    first four characters, and then converts them to an integer format.
    
    Parameters:
    - df (pd.DataFrame): DataFrame containing a 'Year' column.
    
    Returns:
    - pd.DataFrame: DataFrame with the 'Year' column converted to integer format.
    
    Example:
    >>> df = pd.DataFrame({
        'Year': ['2006-01-01 00:00:00', '2007-01-01 00:00:00'],
        'Value': [100, 200]
        })
    >>> convert_year_col_to_string_yyyy(df)
       Year  Value
    0  2006    100
    1  2007    200
    """
    df["Year"] = df["Year"].astype(str)
    df["Year"] = df["Year"].str[:4].astype(int)
    return df


def sort_processed_df_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts the input dataframe by the "Year" column in ascending order.

    Parameters:
    - df (pd.DataFrame): The input dataframe containing a "Year" column.

    Returns:
    - pd.DataFrame: The sorted dataframe with rows ordered by the "Year" column.

    Example:
    >>> df = pd.DataFrame({
        'Year': [2007, 2006, 2008],
        'Value': [100, 200, 150]
        })
    >>> sort_processed_df_by_year(df)
       Year  Value
    1  2006    200
    0  2007    100
    2  2008    150
    """
    return df.sort_values(by = "Year")


def interpolate_single_best_missing_value(df: pd.DataFrame) -> pd.DataFrame:
    """
    Interpolate a single missing value for each country's time series in the dataframe.

    The function identifies and interpolates only one missing 
    value per country for each column based on two conditions:
    1. The missing value should have actual numerical values both before and after it.
    2. Interpolating this missing value should result in the longest possible consecutive sequence 
       of numerical observations within the country's time series.

    Parameters:
    - df (pd.DataFrame): The input dataframe containing columns "Year", 
        "Country", and other columns with time series data.

    Returns:
    - pd.DataFrame: The dataframe with the interpolated value(s).

    Note:
    The function uses linear interpolation to estimate the missing value.
    """
    countries     = df["Country"].unique()
    index_columns = [col for col in df.columns if col not in ["Year", "Country"]]

    for country in countries:
        country_df = df[df["Country"] == country].copy()
        country_df.set_index("Year", inplace=True)

        for index_name in index_columns:
            # Find missing values
            missing_years = country_df[country_df[index_name].isna()].index.tolist()

            # If there are no missing values or only one missing value, continue to next index
            if len(missing_years) <= 1:
                continue

            # Find the best missing year to interpolate based on the conditions
            best_missing_year = None
            best_sequence_length = 0

            for year in missing_years:
                if year - 1 in country_df.index and year + 1 in country_df.index:
                    if not np.isnan(country_df.at[year - 1, index_name]) \
                        and not np.isnan(country_df.at[year + 1, index_name]):
                        # Calculate sequence length if this year is interpolated
                        sequence_length = 2  # Including the year before and after
                        y = year + 1
                        while y + 1 in country_df.index \
                            and not np.isnan(country_df.at[y + 1, index_name]):
                            sequence_length += 1
                            y += 1
                        y = year - 1
                        while y - 1 in country_df.index \
                            and not np.isnan(country_df.at[y - 1, index_name]):
                            sequence_length += 1
                            y -= 1

                        # Update best year if this year produces a longer sequence
                        if sequence_length > best_sequence_length:
                            best_sequence_length = sequence_length
                            best_missing_year = year

            # Interpolate the best missing year
            if best_missing_year:
                interpolated_value = (country_df.at[best_missing_year - 1, index_name] \
                    + country_df.at[best_missing_year + 1, index_name]) / 2
                country_df.at[best_missing_year, index_name] = interpolated_value
                df.update(country_df)

    return df


def remove_nan_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with NaN values in all columns except "Year" and "Country".

    Parameters:
    - df (pd.DataFrame): The input dataframe containing columns "Year", 
        "Country", and other columns with time series data.

    Returns:
    - pd.DataFrame: The dataframe with rows containing NaN values removed.

    Note:
    Rows are removed only if they have NaN values in all columns other than "Year" and "Country".
    """
    index_columns = [col for col in df.columns if col not in ["Year", "Country"]]
    return df.dropna(subset = index_columns, how = "all")


def remove_rank_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove the 'rank', 'RANK', or 'Rank' column from a DataFrame if it exists.
    
    Parameters:
    - df (pd.DataFrame): DataFrame that may contain a 'rank', 'RANK', or 'Rank' column.
    
    Returns:
    - pd.DataFrame: DataFrame with the rank column removed if it existed.
    
    Example:
    >>> df = pd.DataFrame({
        'rank': [1, 2, 3],
        'Value': [100, 200, 300]
        })
    >>> remove_rank_column(df)
       Value
    0    100
    1    200
    2    300
    """
    rank_columns = ["rank", "RANK", "Rank"]
    for col in rank_columns:
        if col in df.columns:
            df = df.drop(columns=[col])
            break
    return df


def transform_country_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize the country names in the DataFrame based on a reference CSV.
    
    Parameters:
    - df (pd.DataFrame): The input DataFrame with country names to be standardized.
    - countries_csv_path (str): Path to the CSV file containing standardized country names.
    
    Returns:
    - pd.DataFrame: DataFrame with standardized country names.
    """

    # Load the countries DataFrame
    countries = pd.read_csv(COUNTRIES_CSV_PATH)

    # Create a mapping dictionary from the countries DataFrame
    mapping_dict = {}
    for _, row in countries.iterrows():
        for col in row.index:
            if pd.notna(row[col]):
                mapping_dict[row[col]] = row["Name"]

    # Replace country names in the DataFrame based on the mapping and print the renamed countries
    for original_name, standardized_name in mapping_dict.items():
        if original_name in df["Country"].values and original_name != standardized_name:
            df["Country"] = df["Country"].replace(original_name, standardized_name)
            print(f"Renamed '{original_name}' to '{standardized_name}'")

    # Check for any country names that couldn't be standardized
    all_country_names_in_csv = countries.melt(value_vars = countries.columns).dropna()["value"].unique()
    unmatched_countries = df[~df["Country"].isin(all_country_names_in_csv)]["Country"].unique()

    if unmatched_countries.size > 0:
        raise ValueError(f"The following countries were not found in the CSV: {', '.join(unmatched_countries)}. Please add them as a new country or new version of a current country in the CSV.")

    return df


def trim_country_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trims whitespace from the "Country" column values in the DataFrame.
    
    Parameters:
    - df (pd.DataFrame): The input DataFrame with country names to be trimmed.
    
    Returns:
    - pd.DataFrame: DataFrame with trimmed country names.
    """

    df["Country"] = df["Country"].str.strip()

    return df
