import pandas as pd
import streamlit as st
from typing import Optional

@st.cache_data
def load_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Loads data from an Excel file into a pandas DataFrame and caches the result.

    The `@st.cache_data` decorator ensures that the data is loaded only once,
    improving the performance of the Streamlit application.

    Args:
        file_path (str): The path to the Excel file.

    Returns:
        Optional[pd.DataFrame]: The loaded data as a pandas DataFrame, or None if an error occurs.
    """
    try:
        # Load the Excel file into a pandas DataFrame
        df = pd.read_excel(file_path)
        # Perform basic data cleaning by removing any unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        # Sanitize column names for SQL compatibility (replace spaces and special chars with underscores)
        df.columns = [col.strip().replace(' ', '_').replace('.', '_').replace('-', '_') for col in df.columns]
        return df
    except FileNotFoundError:
        # Display an error in the Streamlit app if the file is not found
        st.error(f"Error: The file at {file_path} was not found.")
        return None
    except Exception as e:
        # Display a general error message for other exceptions
        st.error(f"An error occurred while loading the Excel file: {e}")
        return None

def get_schema(df: Optional[pd.DataFrame]) -> str:
    """
    Extracts the schema (column names and data types) from a DataFrame.

    This helper function generates a string representation of the DataFrame's schema,
    which is essential context for the language model to generate accurate SQL queries.

    Args:
        df (Optional[pd.DataFrame]): The pandas DataFrame.

    Returns:
        str: A string representation of the DataFrame's schema, or an empty string if the DataFrame is None.
    """
    if df is None:
        return ""

    # Create a descriptive string for the schema
    schema = "Table 'df' has the following columns and data types:\n"
    for column in df.columns:
        schema += f"- Column: '{column}' (Type: {df[column].dtype})\n"
    return schema

# Example of how to use the functions for standalone testing
if __name__ == '__main__':
    # Define the path to the data file, now located in the 'data' subfolder
    file_path = 'data/Data Dump - Accrual Accounts.xlsx'
    
    # Load the data using the load_data function
    data_df = load_data(file_path)

    if data_df is not None:
        print("Data loaded successfully!")
        print("First 5 rows of the DataFrame:")
        print(data_df.head())
        print("\n" + "="*50 + "\n")
        
        # Get and print the schema information from the loaded DataFrame
        schema_info = get_schema(data_df)
        print("DataFrame Schema:")
        print(schema_info)