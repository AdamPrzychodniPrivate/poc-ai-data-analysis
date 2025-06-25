import pandas as pd
from pandasql import sqldf, PandaSQLException
from typing import Tuple, Optional

def execute_query(sql_query: str, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Executes a SQL query on a pandas DataFrame using pandasql.

    This function takes a SQL query string and a DataFrame, executes the query,
    and returns the result. It includes error handling to catch and report
    issues with the SQL syntax or execution.

    Args:
        sql_query (str): The SQL query to be executed. The table in the query
                         should be referred to as 'df'.
        df (pd.DataFrame): The pandas DataFrame on which the query will be run.

    Returns:
        Tuple[Optional[pd.DataFrame], Optional[str]]: A tuple containing:
        - The resulting pandas DataFrame if the query is successful, otherwise None.
        - An error message string if an exception occurs, otherwise None.
    """
    # Define a local namespace for sqldf to find the DataFrame 'df'.
    pysqldf = lambda q: sqldf(q, {'df': df})
    
    try:
        # Execute the query using the lambda function
        result_df = pysqldf(sql_query)
        return result_df, None
    except PandaSQLException as e:
        # Catch specific pandasql errors (e.g., SQL syntax errors)
        error_message = f"SQL Error: {e}. Please check your query syntax."
        return None, error_message
    except Exception as e:
        # Catch any other unexpected errors during query execution
        error_message = f"An unexpected error occurred: {e}"
        return None, error_message
