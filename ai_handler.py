import os
import streamlit as st
from openai import OpenAI
import pandas as pd
# FIX: Import the necessary types for casting
from typing import List, Dict, cast
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam


# --- Securely Load API Key ---
# Make sure your OPENAI_API_KEY is set as an environment variable
API_KEY = os.getenv("OPENAI_API_KEY") 

if not API_KEY:
    st.error("OpenAI API key is not set. Please set it as an environment variable.")
    st.stop()

client = OpenAI(api_key=API_KEY)
MODEL = "gpt-4o-mini"


def generate_sql(chat_history: List[Dict[str, str]], schema: str) -> str:
    """
    Generates a pandasql-compatible SQL query from a full conversation history.
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
    
    # FIX: The messages list is created from generic dicts, which is fine.
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)

    try:
        # FIX: We apply the 'cast' here, right as we pass the data to the client.
        # This tells the type checker that the 'messages' list is structured correctly.
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


def generate_plotly_code(data: pd.DataFrame, question: str) -> str:
    """
    Generates Python code for a Plotly chart.
    """
    data_sample = data.to_markdown(index=False)
    columns = data.columns.tolist()
    
    prompt = f"""
    You are a data visualization expert specializing in Plotly. Your task is to write Python code
    to generate a Plotly chart that answers the user's question based on the provided data.

    **User's Original Question:**
    "{question}"

    **Data to Visualize (this is the result of the last query, available as a DataFrame named `df`):**
    ```
    {data_sample}
    ```

    **CRITICAL INSTRUCTIONS:**
    1.  The data to be plotted has the following exact column names: `{columns}`. You **MUST** use these column names for the `x` and `y` axes in your code.
    2.  Generate Python code that creates a Plotly figure and assigns it to a variable named `fig`.
    3.  Choose the best chart type (e.g., bar, line, pie) to answer the question. For the provided data, a bar chart is likely best.
    4.  The code must be a single block. **Do NOT include `import` statements or `fig.show()`**.
    5.  Make the chart title and axis labels clear and descriptive. Use `template='plotly_white'` for a clean look.

    **Example for columns ['Fiscal_Year_1', 'Total_Transaction_Value']:**
    ```python
    fig = px.bar(
        df,
        x='{columns[0]}',
        y='{columns[1]}',
        title='Total Transaction Value by Year',
        template='plotly_white'
    )
    fig.update_xaxes(type='category') # Treat year as a category for correct spacing
    ```

    **Your Turn (Use the exact column names `{columns}`):**
    Python Code:
    """
    
    # This logic does not call the OpenAI client, so it does not need the same fix.
    # We will apply the same fix if we were to change this to also be conversational.
    # For now, keeping the same logic as before is fine.

    # Let's apply the fix here as well for consistency, assuming we might make it conversational later.
    messages_for_plot = [
        {"role": "system", "content": "You are an expert assistant that generates Python code for Plotly visualizations using exact column names."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=cast(List[ChatCompletionMessageParam], messages_for_plot),
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