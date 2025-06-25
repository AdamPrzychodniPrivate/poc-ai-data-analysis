import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from typing import List, Dict, cast
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam


# Load environment variables from .env file
load_dotenv()

# Securely Load API Key
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("OpenAI API key is not set. Please set it as an environment variable.")
    st.stop()

client = OpenAI(api_key=API_KEY)
MODEL = "gpt-4o-mini"


def generate_sql(chat_history: List[Dict[str, str]], schema: str) -> str:
    """
    Generates a pandasql-compatible SQL query from a full conversation history.
    Returns: The generated SQL query string, or an error message if generation fails.
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


def generate_plotly_code(data: pd.DataFrame, question: str) -> str:
    """
    Generates enhanced Python code for a Plotly chart.

    Returns:
        str: A string containing the Python code for the Plotly figure.
    """
    # Limit the data sample to save tokens and focus the summary on key aspects
    data_sample = data.head(5).to_markdown(index=False)

    columns = data.columns.tolist()

    # Identify numeric and categorical columns to help the AI
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()

    prompt = f"""
    You are a data visualization expert specializing in the Plotly library in Python.
    Your task is to write Python code to generate a single, visually appealing, and informative Plotly figure
    that effectively answers the user's question based on the provided data sample.

    **User's Original Question:**
    "{question}"

    **Data Sample to Visualize (this is a sample, the full data is available in the `df` variable):**
    ```markdown
    {data_sample}
    ```

    **DataFrame Column Information:**
    - All Columns: `{columns}`
    - Numeric Columns: `{numeric_cols}`
    - Categorical Columns: `{categorical_cols}`

    **CRITICAL INSTRUCTIONS:**

    1.  **Figure Variable:** The generated Plotly figure **MUST** be assigned to a variable named `fig`.
    2.  **No Imports or Displaying:** The code block must NOT include any `import` statements or `fig.show()`.
    3.  **Chart Type Selection:** Choose the best chart type to answer the question.
        - Use `px.bar` for comparisons of categorical data.
        - Use `px.line` for time-series data or trends over continuous intervals.
        - Use `px.pie` or `px.donut` for showing parts of a whole (use sparingly, preferably with few categories).
        - Use `px.scatter` for relationships between two numeric variables.
        - Use `px.histogram` for distributions of a single variable.
    4.  **Aesthetics and Clarity:**
        - **Template:** Use `template='plotly_dark'` for a modern look.
        - **Title:** Create a clear, descriptive title for the chart that directly relates to the user's question.
        - **Axis Labels:** Use clear and descriptive labels for the x and y axes. If an axis represents a monetary value, reflect that in the label (e.g., 'Total Sales ($)').
        - **Colors:** If creating a bar or pie chart, use a visually appealing, non-default color scale like `color_discrete_sequence=px.colors.qualitative.Pastel`.
        - **Hover Data:** Enhance the tooltips (`hover_data`). Format them to be readable. For example, for currency, format it like `':$,.2f'`.
        - **Categorical Axes:** If an axis (especially the x-axis) represents categories like years or names, ensure it's treated as a categorical type to prevent weird spacing issues (e.g., `fig.update_xaxes(type='category')`).
    5.  **Data Columns:** You **MUST** use the exact column names provided: `{columns}`. Do not invent or assume column names.

    **Example of Excellent Code (for columns ['Year', 'Total_Revenue']):**
    ```python
    # Answering: "What was the total revenue per year?"
    fig = px.bar(
        df,
        x='Year',
        y='Total_Revenue',
        title='Total Revenue by Year',
        color='Year',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='plotly_dark'
    )
    fig.update_layout(
        xaxis_title='Fiscal Year',
        yaxis_title='Total Revenue ($)',
        showlegend=False
    )
    fig.update_xaxes(type='category')
    fig.update_traces(hovertemplate='<b>Year:</b> %{{x}}<br><b>Total Revenue:</b> %{{y:$,.2f}}<extra></extra>')
    ```

    **Your Turn (Use the exact column names `{columns}`):**
    """

    messages_for_plot = [
        {"role": "system", "content": "You are an expert assistant that generates Python code for Plotly visualizations following strict guidelines."},
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
            plotly_code_lines = plotly_code.split('\n')
            cleaned_plotly_code_lines = [line for line in plotly_code_lines if not line.strip().startswith('import ')]
            plotly_code = "\n".join(cleaned_plotly_code_lines)
            return plotly_code
        else:
            return ""

    except Exception as e:
        return f"Error generating Plotly code: {e}"


def generate_data_summary(data: pd.DataFrame, question: str) -> str:
    """
    Generates a concise textual summary of the queried data and its visualization.
    Returns: A concise textual summary string, or an error message if summary generation fails.
    """
    # Limit the data sample to save tokens and focus the summary on key aspects
    data_sample_for_summary = data.head(10).to_markdown(index=False)

    summary_prompt = f"""
    You are an expert data analyst. Your task is to provide a very concise,
    plain-language summary of the insights from the provided data,
    especially focusing on what a visualization of this data would highlight.

    **User's Original Question:**
    "{question}"

    **Queried Data Sample:**
    ```markdown
    {data_sample_for_summary}
    ```

    **Instructions:**
    1.  Keep the summary to 1-2 sentences, max 50 words.
    2.  Focus on the main trend, key figures, or the most important insight presented in the data,
        as if describing what a chart of this data would clearly show.
    3.  Avoid technical jargon. Use natural, business-friendly language.
    4.  Do NOT include any code, markdown formatting (like ```), or conversational filler.
        Just the summary text.
    """

    messages_for_summary = [
        {"role": "system", "content": "You are a concise data summarization expert."},
        {"role": "user", "content": summary_prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=cast(List[ChatCompletionMessageParam], messages_for_summary),
            temperature=0.3, # A bit higher temperature for more varied summaries
        )
        message_content = response.choices[0].message.content
        if message_content:
            return message_content.strip()
        else:
            return "No summary could be generated."
    except Exception as e:
        return f"Error generating summary: {e}"