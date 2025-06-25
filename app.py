# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path  # <-- 1. IMPORT PATHLIB


from data_loader import load_data, get_schema
from ai_handler import generate_sql, generate_plotly_code
from query_executor import execute_query


# --- 2. CONSTRUCT A RELIABLE FILE PATH ---
# Get the directory where this script (app.py) is located
APP_DIR = Path(__file__).parent
# Construct the full, absolute path to the data file
DATA_FILE_PATH = APP_DIR / "data" / "Data Dump - Accrual Accounts.xlsx"


# --- Page Configuration ---
st.set_page_config(
   page_title="AI Data Analysis",
   page_icon="🤖",
   layout="wide"
)


# --- Main Application ---
st.title("🤖 AI-Powered Data Analysis")
st.caption("A Proof of Concept for natural language data interaction.")


# --- Load Data ---
# Using a cached function is best practice for loading data
@st.cache_data
def cached_load_data(file_path):
   return load_data(file_path)


# --- 3. USE THE NEW, ROBUST PATH ---
# This now uses the absolute path we created above
df_main = cached_load_data(DATA_FILE_PATH)


if df_main is not None:
   # --- Raw Data Preview ---
   with st.expander("View Raw Data Source"):
       st.dataframe(df_main, use_container_width=True)


   # --- Initialize Chat ---
   # (The rest of your code continues as before)
   # ...


   # --- Initialize Chat ---
   st.subheader("Chat with your data")


   if 'messages' not in st.session_state:
       st.session_state.messages = [{
           "role": "assistant",
           "content": "Hello! I'm your AI Data Analyst. How can I help you explore your data today? Try asking 'What is the total transaction value for each year?'",
           "dataframe": None,
           "plot": None
       }]


   # Display all past messages
   for msg in st.session_state.messages:
       with st.chat_message(msg["role"]):
           st.markdown(msg["content"])
           # Display DataFrame if it exists and is not empty
           if isinstance(msg.get("dataframe"), pd.DataFrame) and not msg["dataframe"].empty:
               st.dataframe(msg["dataframe"], use_container_width=True)
           # Display plot if it exists
           if msg.get("plot") is not None:
               st.plotly_chart(msg["plot"], use_container_width=True)


   # --- Chat Input and Full AI Logic ---
   if prompt := st.chat_input("Ask a question about your data..."):
       # Append user message and display it immediately
       st.session_state.messages.append({"role": "user", "content": prompt})
       with st.chat_message("user"):
           st.markdown(prompt)


       # Generate and display AI response
       with st.chat_message("assistant"):
           with st.spinner("Analyzing your request..."):
               # Prepare context for the AI
               chat_history_for_api = [
                   {"role": msg["role"], "content": msg["content"]}
                   for msg in st.session_state.messages
               ]
               schema = get_schema(df_main)
              
               # Step 1: Generate SQL
               sql_query = generate_sql(chat_history=chat_history_for_api, schema=schema)


               if sql_query.startswith("Error:"):
                   response_content = f"Sorry, I encountered an error during SQL generation:\n\n`{sql_query}`"
                   st.error(response_content)
                   st.session_state.messages.append({"role": "assistant", "content": response_content})
                   st.rerun()


               with st.expander("View Generated SQL Query"):
                   st.code(sql_query, language="sql")
              
               # Step 2: Execute SQL Query
               result_df, error = execute_query(sql_query, df_main)


               if error:
                   response_content = f"I encountered an error running the query:\n\n`{error}`"
                   st.error(response_content)
                   st.session_state.messages.append({"role": "assistant", "content": response_content})
                   st.rerun()


               # Step 3: Handle Query Results and Generate Plot
               if result_df is None or result_df.empty:
                   response_content = "The query ran successfully but returned no results."
                   st.warning(response_content)
                   st.session_state.messages.append({"role": "assistant", "content": response_content})
              
               else:
                   response_content = "Here are the results of your query:"
                   st.markdown(response_content)
                   st.dataframe(result_df, use_container_width=True)
                  
                   fig = None
                   # Attempt to generate a plot if the data is suitable
                   numeric_cols = result_df.select_dtypes(include='number').columns
                   if len(result_df.columns) >= 2 and len(numeric_cols) > 0:
                       with st.spinner("Generating visualization..."):
                           plotly_code = generate_plotly_code(data=result_df, question=prompt)
                          
                           if plotly_code:
                               with st.expander("View Generated Visualization Code"):
                                   st.code(plotly_code, language="python")
                               try:
                                   local_vars = {'df': result_df, 'px': px}
                                   exec(plotly_code, {}, local_vars)
                                   fig = local_vars.get('fig')
                                  
                                   if fig:
                                       st.plotly_chart(fig, use_container_width=True)
                                   else:
                                       st.warning("The AI generated code that did not produce a chart.")
                               except Exception as e:
                                   st.error(f"An error occurred while rendering the visualization: {e}")
                           else:
                               st.info("A visualization could not be generated for this query result.")


                   # Append the final message with all its parts
                   st.session_state.messages.append({
                       "role": "assistant",
                       "content": response_content,
                       "dataframe": result_df,
                       "plot": fig
                   })
       # Rerun at the very end to reflect the new state
       st.rerun()


else:
   st.error("🔴 Critical Error: The data file could not be loaded. The application cannot continue.")




