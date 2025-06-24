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

# Example of how to use the function for standalone testing
if __name__ == '__main__':
    # Create a sample DataFrame for testing purposes
    data = {
        'country': ['USA', 'UK', 'Canada', 'USA', 'Germany'],
        'sales': [150, 200, 120, 180, 130],
        'year': [2021, 2021, 2022, 2022, 2021]
    }
    sample_df = pd.DataFrame(data)

    print("--- Sample DataFrame ---")
    print(sample_df)
    print("\n" + "="*50 + "\n")

    # --- Test Case 1: Successful Query ---
    print("--- Testing a successful query ---")
    successful_query = "SELECT country, SUM(sales) as total_sales FROM df GROUP BY country ORDER BY total_sales DESC;"
    print(f"Query: {successful_query}")
    
    result, error = execute_query(successful_query, sample_df)
    
    if error:
        print(f"Error executing query: {error}")
    else:
        print("Query executed successfully. Result:")
        print(result)
    
    print("\n" + "="*50 + "\n")

    # --- Test Case 2: Query with a Syntax Error ---
    print("--- Testing a query with a syntax error ---")
    erroneous_query = "SELECT country, SUM(sales) FROM df GROUP BY;" # Invalid GROUP BY
    print(f"Query: {erroneous_query}")

    result, error = execute_query(erroneous_query, sample_df)

    if error:
        print(f"Caught expected error: {error}")
    else:
        print("Query executed without expected error. Result:")
        print(result)