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

if df_main is not None:
    # --- Raw Data Preview ---
    with st.expander("View Raw Data"):
        st.dataframe(df_main, use_container_width=True)

    # --- Chat Interface ---
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

        # Process and generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your request and generating a response..."):
                chat_history_for_api = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                ]
                schema = get_schema(df_main)
                sql_query = generate_sql(chat_history=chat_history_for_api, schema=schema)

                # *** FIX APPLIED HERE: The indented blocks are now correctly filled in. ***

                if sql_query.startswith("Error:"):
                    # This block was missing its content, causing the error.
                    response_content = f"Sorry, I encountered an error during SQL generation:\n\n`{sql_query}`"
                    st.error(response_content)
                    st.session_state.messages.append({
                        "role": "assistant", "content": response_content, "dataframe": None, "plot": None
                    })
                else:
                    with st.expander("View Generated SQL Query"):
                        st.code(sql_query, language="sql")
                    
                    result_df, error = execute_query(sql_query, df_main)

                    if error:
                        # This block was also missing.
                        response_content = f"I encountered an error running the query:\n\n`{error}`"
                        st.error(response_content)
                        st.session_state.messages.append({
                            "role": "assistant", "content": response_content, "dataframe": None, "plot": None
                        })
                    
                    elif result_df is not None:
                        if result_df.empty:
                            # And this block was missing.
                            response_content = "The query ran successfully but returned no results."
                            st.warning(response_content)
                            st.session_state.messages.append({
                                "role": "assistant", "content": response_content, "dataframe": None, "plot": None
                            })
                        else:
                            response_content = "Here are the results of your query:"
                            st.success(response_content)
                            st.dataframe(result_df, use_container_width=True)
                            
                            fig = None
                            
                            # Robust plotting logic
                            numeric_cols = result_df.select_dtypes(include='number').columns
                            if not result_df.empty and len(result_df.columns) >= 2 and len(numeric_cols) > 0:
                                
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

                            st.session_state.messages.append({
                                "role": "assistant", "content": response_content, "dataframe": result_df, "plot": fig
                            })
        st.rerun()

else:
    st.error("🔴 Critical Error: The data file could not be loaded. The application cannot continue.")