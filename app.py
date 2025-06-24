import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data, get_schema
from ai_handler import generate_sql, generate_plotly_code
from query_executor import execute_query

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Data Analysis for Jäppinen Ltd.",
    page_icon="🤖",
    layout="wide"
)

# --- Main Application ---
st.title("🤖 AI Data Analysis for Jäppinen Ltd.")
st.caption("A Proof of Concept for natural language data interaction.")

# --- Load Data ---
df_main = load_data('data/Data Dump - Accrual Accounts.xlsx')

# --- Main Application Logic ---
# This structure ensures that the rest of the app only runs if the data loads successfully.
if df_main is not None:
    # --- Raw Data Preview (at the top in a collapsible section) ---
    with st.expander("View Raw Data"):
        st.dataframe(df_main, use_container_width=True)

    # --- Chat Interface ---
    st.subheader("Chat with your data")

    # Initialize session state for chat history if it doesn't exist
    if 'messages' not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm your AI Data Analyst. How can I help you explore your data today? Try asking something like: 'What is the total transaction value for each country?'",
            "dataframe": None,
            "plot": None
        }]

    # Display all past messages from the session state
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if isinstance(msg.get("dataframe"), pd.DataFrame):
                st.dataframe(msg["dataframe"], use_container_width=True)
            if msg.get("plot") is not None:
                st.plotly_chart(msg["plot"], use_container_width=True)

    # --- Chat Input and Full AI Logic ---
    if prompt := st.chat_input("Ask a question about your data..."):
        st.session_state.messages.append({
            "role": "user", "content": prompt, "dataframe": None, "plot": None
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process the user's request and generate the AI's response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your request and generating a response..."):
                # Step 1: Generate SQL using the full chat history for context
                chat_history_for_api = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                ]
                schema = get_schema(df_main)
                sql_query = generate_sql(chat_history=chat_history_for_api, schema=schema)

                if sql_query.startswith("Error:"):
                    response_content = f"Sorry, I encountered an error during SQL generation:\n\n`{sql_query}`"
                    st.error(response_content)
                    st.session_state.messages.append({
                        "role": "assistant", "content": response_content, "dataframe": None, "plot": None
                    })
                else:
                    with st.expander("View Generated SQL Query"):
                        st.code(sql_query, language="sql")
                    
                    # Step 2: Execute the SQL query
                    result_df, error = execute_query(sql_query, df_main)

                    if error:
                        response_content = f"I encountered an error running the query:\n\n`{error}`"
                        st.error(response_content)
                        st.session_state.messages.append({
                            "role": "assistant", "content": response_content, "dataframe": None, "plot": None
                        })
                    
                    elif result_df is not None:
                        if result_df.empty:
                            response_content = "The query ran successfully but returned no results."
                            st.warning(response_content)
                            st.session_state.messages.append({
                                "role": "assistant", "content": response_content, "dataframe": None, "plot": None
                            })
                        else:
                            # Step 3: Display results and attempt to generate a visualization
                            response_content = "Here are the results of your query:"
                            st.success(response_content)
                            st.dataframe(result_df, use_container_width=True)
                            
                            fig = None
                            plotly_code = ""

                            # --- START OF ROBUST PLOTTING LOGIC ---

                            # Condition: Try to plot if the result has at least 2 columns and at least one is numeric.
                            numeric_cols = result_df.select_dtypes(include='number').columns
                            if len(result_df.columns) >= 2 and len(numeric_cols) > 0:
                                
                                # A. Hardcoded Fix: If the result has only one row, create a bar chart directly.
                                # This is more reliable than asking the AI for such a simple case.
                                if len(result_df) == 1:
                                    st.write("Generating a bar chart for the summary...")
                                    categorical_cols = result_df.select_dtypes(include=['object', 'category']).columns
                                    # Ensure we have a categorical and numeric column to plot
                                    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                                        x_col, y_col = categorical_cols[0], numeric_cols[0]
                                        # Use a cleaned up version of the prompt for the title
                                        title = prompt.replace("'", "").replace('"', '') if len(prompt) < 50 else "Query Result"
                                        plotly_code = f"fig = px.bar(df, x='{x_col}', y='{y_col}', title='{title}', text_auto=True)"

                                # B. AI Fallback: For multi-row results, ask the AI for the plot.
                                else:
                                    plotly_code = generate_plotly_code(data=result_df, chat_history=chat_history_for_api)

                                # C. Execution & Debugging: Run the generated code (from fix or AI) and add a debug expander.
                                if plotly_code:
                                    with st.expander("View Generated Visualization Code"):
                                        st.code(plotly_code, language="python")
                                    try:
                                        # Execute the code in a controlled environment
                                        local_vars = {'df': result_df, 'px': px}
                                        exec(plotly_code, {}, local_vars)
                                        fig = local_vars.get('fig')
                                        if fig:
                                            st.plotly_chart(fig, use_container_width=True)
                                        else:
                                            st.warning("A chart could not be generated from the provided code.")
                                    except Exception as e:
                                        st.error(f"An error occurred while rendering the visualization: {e}")
                            
                            # --- END OF ROBUST PLOTTING LOGIC ---

                            st.session_state.messages.append({
                                "role": "assistant", "content": response_content, "dataframe": result_df, "plot": fig
                            })
        # Rerun the app to display the new message immediately
        st.rerun()

else:
    # This block handles the critical error where the data file itself can't be loaded.
    st.error("🔴 Critical Error: The data file could not be loaded. The application cannot continue.")
