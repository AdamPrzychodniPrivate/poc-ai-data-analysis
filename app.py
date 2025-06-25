import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from data_loader import load_data, get_schema
from ai_handler import generate_sql, generate_plotly_code, generate_data_summary
from query_executor import execute_query


# --- 2. CONSTRUCT A RELIABLE FILE PATH ---
# Get the directory where this script (app.py) is located
APP_DIR = Path(__file__).parent
# Construct the full, absolute path to the data file
DATA_FILE_PATH = APP_DIR / "data" / "Data Dump - Accrual Accounts.xlsx"


# --- Page Configuration ---
st.set_page_config(
    page_title="AI Data Analysis",
    page_icon="�",
    layout="wide"
)


# --- Main Application ---
st.title("🤖 AI-Powered Data Analysis")
st.caption("A Proof of Concept for natural language data interaction.")


# --- Load Data ---
# Using a cached function is best practice for loading data
@st.cache_data
def cached_load_data(file_path):
    """
    Caches the data loading process for performance.
    """
    return load_data(file_path)


# --- 3. USE THE NEW, ROBUST PATH ---
# This now uses the absolute path we created above
df_main = cached_load_data(DATA_FILE_PATH)


if df_main is not None:
    # --- Raw Data Preview ---
    # Display the raw data in a collapsible expander at the top of the page
    with st.expander("View Raw Data Source"):
        st.dataframe(df_main, use_container_width=True)


    # --- Initialize Chat ---
    st.subheader("Chat with your data")

    # Initialize session state for messages if not already present
    if 'messages' not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            # Updated welcome message, removed the example question
            "content": "Hello! I'm your AI Data Analyst. How can I help you explore your data today?",
            "dataframe": None,
            "plot": None,
            "sql_query": None, # Add a key for SQL query
            "plotly_code": None, # Add a key for Plotly code
            "summary": None # Add a key for the data summary
        }]
    
    # Initialize a state variable to hold the prompt from a button click
    if 'user_input_prompt' not in st.session_state:
        st.session_state.user_input_prompt = ""

    # New state variable to control the visibility of the example button
    if 'show_example_button' not in st.session_state:
        st.session_state.show_example_button = True


    # Display all past messages in the chat interface
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            # Display summary first if it exists in the message
            if msg.get("summary") is not None:
                st.markdown(f"**Summary:** {msg['summary']}") # Bold the summary for emphasis
            
            # Display the main content of the message
            st.markdown(msg["content"])
            
            # Display DataFrame if it exists and is not empty
            if isinstance(msg.get("dataframe"), pd.DataFrame) and not msg["dataframe"].empty:
                st.dataframe(msg["dataframe"], use_container_width=True)
            
            # Display plot if it exists
            if msg.get("plot") is not None:
                st.plotly_chart(msg["plot"], use_container_width=True)
            
            # Display the generated SQL Query in a collapsible expander
            if msg.get("sql_query") is not None:
                with st.expander("View Generated SQL Query"):
                    st.code(msg["sql_query"], language="sql")
            
            # Display the generated Plotly Code in a collapsible expander
            if msg.get("plotly_code") is not None:
                with st.expander("View Generated Visualization Code"):
                    st.code(msg["plotly_code"], language="python")

    # --- Button for Example Question ---
    example_question = "What is the total transaction value for each fiscal year, based on Fiscal_Year_1?"
    # Only show the button if 'show_example_button' is True
    if st.session_state.show_example_button:
        if st.button(f"Try: '{example_question}'"):
            st.session_state.user_input_prompt = example_question
            st.session_state.show_example_button = False # Hide the button after clicking
            st.rerun() # Rerun to process the new prompt


    # --- Chat Input and Full AI Logic ---
    # Handle user input from the chat input box
    # Use the prompt from the button if available, otherwise use the regular chat input
    if st.session_state.user_input_prompt:
        prompt = st.session_state.user_input_prompt
        st.session_state.user_input_prompt = "" # Clear the prompt after using it
    else:
        prompt = st.chat_input("Ask a question about your data...")

    if prompt: # Only proceed if there is a prompt
        # If a prompt is submitted (either by typing or from the button), hide the example button
        st.session_state.show_example_button = False 

        # Append user message to session state and display it immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare a dictionary to store all parts of the new assistant message
        new_assistant_message = {
            "role": "assistant",
            "content": "", # Will be filled later with the main textual response
            "dataframe": None,
            "plot": None,
            "sql_query": None,
            "plotly_code": None,
            "summary": None # Initialize summary as None
        }

        # Generate and display AI response
        with st.chat_message("assistant"):
            # Display a spinner while processing the request
            with st.spinner("Analyzing your request..."):
                # Prepare context for the AI model: full chat history and data schema
                chat_history_for_api = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                ]
                schema = get_schema(df_main)
                
                # Step 1: Generate SQL query using the AI
                sql_query = generate_sql(chat_history=chat_history_for_api, schema=schema)
                new_assistant_message["sql_query"] = sql_query # Store the generated SQL query

                # Handle errors during SQL generation
                if sql_query.startswith("Error:"):
                    response_content = f"Sorry, I encountered an error during SQL generation:\n\n`{sql_query}`"
                    st.error(response_content)
                    new_assistant_message["content"] = response_content
                    st.session_state.messages.append(new_assistant_message)
                    st.rerun() # Rerun to display the error message

                # Display the generated SQL query in an expander for transparency
                with st.expander("View Generated SQL Query"):
                    st.code(sql_query, language="sql")
                
                # Step 2: Execute the generated SQL Query
                result_df, error = execute_query(sql_query, df_main)

                # Handle errors during SQL execution
                if error:
                    response_content = f"I encountered an error running the query:\n\n`{error}`"
                    st.error(response_content)
                    new_assistant_message["content"] = response_content
                    st.session_state.messages.append(new_assistant_message)
                    st.rerun() # Rerun to display the error message

                # Step 3: Handle Query Results, Generate Plot, and Generate Summary
                if result_df is None or result_df.empty:
                    response_content = "The query ran successfully but returned no results."
                    st.warning(response_content)
                    new_assistant_message["content"] = response_content
                    st.session_state.messages.append(new_assistant_message)
                
                else:
                    # --- NEW: Generate and display a summary of the data ---
                    with st.spinner("Generating summary..."):
                        summary_text = generate_data_summary(result_df, prompt)
                        new_assistant_message["summary"] = summary_text # Store the summary
                        # Display the summary text directly in the chat message
                        st.markdown(f"**Summary:** {summary_text}") 

                    # Main textual response and display of the result DataFrame
                    response_content = "Here are the results of your query:"
                    st.markdown(response_content)
                    st.dataframe(result_df, use_container_width=True)
                    new_assistant_message["dataframe"] = result_df # Store the result DataFrame
                    
                    fig = None # Initialize plot variable
                    plotly_code = None # Initialize plotly code variable

                    # Attempt to generate a plot only if the data is suitable for visualization
                    numeric_cols = result_df.select_dtypes(include='number').columns
                    if len(result_df.columns) >= 2 and len(numeric_cols) > 0:
                        with st.spinner("Generating visualization..."):
                            plotly_code = generate_plotly_code(data=result_df, question=prompt)
                            new_assistant_message["plotly_code"] = plotly_code # Store the generated Plotly code
                            
                            if plotly_code:
                                # Display the generated Plotly code in an expander for transparency
                                with st.expander("View Generated Visualization Code"):
                                    st.code(plotly_code, language="python")
                                try:
                                    # Execute the Plotly code to create a figure object
                                    local_vars = {'df': result_df, 'px': px}
                                    exec(plotly_code, {}, local_vars)
                                    fig = local_vars.get('fig') # Get the 'fig' object from the executed code
                                    
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True)
                                        new_assistant_message["plot"] = fig # Store the Plotly figure
                                    else:
                                        st.warning("The AI generated code that did not produce a chart.")
                                except Exception as e:
                                    st.error(f"An error occurred while rendering the visualization: {e}")
                            else:
                                st.info("A visualization could not be generated for this query result.")
                    else:
                        st.info("The query result is not suitable for a visualization at this time.")

                    # Update the 'content' field of the new assistant message (primarily for historical display)
                    new_assistant_message["content"] = response_content

                    # Append the complete assistant message with all its parts to the session state
                    st.session_state.messages.append(new_assistant_message)
        
        # Rerun the app at the very end to reflect the new state (including newly appended messages)
        st.rerun()

else:
    # Display a critical error if the data file could not be loaded
    st.error("🔴 Critical Error: The data file could not be loaded. The application cannot continue.")
    