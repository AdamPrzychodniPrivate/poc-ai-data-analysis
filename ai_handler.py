import streamlit as st
from openai import OpenAI
import pandas as pd
from typing import List, Dict, cast
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import os # Import the os module

# --- Securely Load API Key ---
# Load the key from an environment variable, not hardcoded in the file.
API_KEY = os.getenv("OPENAI_API_KEY")

# --- OpenAI Client Initialization ---
# Check if the API key was found in the environment.
if not API_KEY:
    st.error("OpenAI API key is not set. Please set it as an environment variable.")
    st.stop()

client = OpenAI(api_key=API_KEY)
MODEL = "gpt-4o-mini"

# --- Core Functions ---

def generate_sql(chat_history: List[Dict[str, str]], schema: str) -> str:
    """
    Generates a pandasql-compatible SQL query from a full conversation history.

    Args:
        chat_history (List[Dict[str, str]]): The history of the conversation.
        schema (str): A string description of the DataFrame's schema.

    Returns:
        str: The generated SQL query or an error message.
    """
    system_prompt = f"""
    You are an expert data analyst who writes SQL queries.
    Your task is to convert a natural language question into a pandasql-compatible SQL query.
    You will be given the entire conversation history and the database schema.
    Use the conversation history to understand context for follow-up questions.
    You are working with a pandas DataFrame named 'df'.

    **DataFrame Schema:**
    {schema}

    **Instructions:**
    1.  The table name MUST be `df`. For example: `SELECT * FROM df;`.
    2.  Generate a single, complete SQL query that answers the user's latest prompt.
    3.  Do NOT include any explanations, comments, or markdown formatting. Only output the raw SQL query.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=cast(List[ChatCompletionMessageParam], messages),
            temperature=0.0,
        )
        
        message_content = response.choices[0].message.content
        if message_content:
            sql_query = message_content.strip().replace("```sql", "").replace("```", "")
            return sql_query
        else:
            return "Error: The AI model returned an empty response."

    except Exception as e:
        return f"Error: Could not generate SQL query. Details: {e}"

def generate_plotly_code(data: pd.DataFrame, chat_history: List[Dict[str, str]]) -> str:
    """
    Generates Python code for a Plotly chart based on a conversation history.

    Args:
        data (pd.DataFrame): The DataFrame to visualize.
        chat_history (List[Dict[str, str]]): The history of the conversation.

    Returns:
        str: Python code for a Plotly figure, or an empty string on failure.
    """
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    data_sample = data.head(20).to_string()

    prompt = f"""
    You are a data visualization expert. Your task is to write Python code to generate a Plotly chart.
    
    **Analyze the conversation history and the provided data to create a relevant visualization.**
    
    **Conversation History:**
    {history_str}
    
    **Data to Visualize (this is the result of the last query):**
    ```
    {data_sample}
    ```

    **Instructions:**
    1.  Your primary goal is to visualize the data in a way that answers the user's LATEST request.
    2.  Generate only the Python code required to create a Plotly figure. The DataFrame is available as `df`.
    3.  The code must create a variable named `fig`. For example: `fig = px.bar(...)`.
    4.  Do NOT include `import` statements or `fig.show()`.
    5.  If the data has only one row, a bar chart is often the best choice.
    6.  The chart title and labels should be clear and relate to the original data query.
    
    **Your Turn (remember to use the dataframe `df`):**
    Python Code:
    """
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates Python code for Plotly visualizations based on a conversation history."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=cast(List[ChatCompletionMessageParam], messages),
            temperature=0.1,
        )
        message_content = response.choices[0].message.content
        if message_content:
            plotly_code = message_content.strip().replace("```python", "").replace("```", "")
            plotly_code = "\n".join([line for line in plotly_code.split('\n') if not line.strip().startswith('import')])
            return plotly_code
        else:
            return ""

    except Exception as e:
        print(f"Error generating Plotly code: {e}")
        return ""
