# 📘 User Documentation: AI-Powered Data Analysis PoC

Welcome to your new AI Data Analyst! This guide will help you get started with the application, understand its features, and empower you to ask questions about your data using plain English.

---

### 1. Getting Started Guide

This guide covers the initial steps to begin using the application.

#### **Purpose of the Application**

This tool is designed to give you direct access to your data without needing to write any code. You can ask questions about data quality, explore trends, and get answers to specific business questions through a simple chat interface. Think of it as having a conversation with a data analyst who instantly responds with tables, charts, and summaries.

#### **First Use**

1.  **Access the Application:** Open the web link provided to you. The application will load directly in your browser.
2.  **View Your Data:** At the top of the page, you will see a section titled **"View Raw Data Source"**. You can click this to expand and see the entire raw dataset you are working with. Click it again to collapse it.
3.  **Ask Your First Question:** A chat window is the main feature of the page. At the very bottom, you will find a text box that says *"Ask a question about your data..."*. Simply type your question here and press Enter.

    * **Not sure what to ask?** Click the example button (e.g., **Try: 'What is the total transaction value for each fiscal year...'**) to automatically send a pre-written question and see how the AI works.

---

### 2. User Manual

This section details the features of the application and how to use them effectively.

#### **How to Ask Questions**

You can ask three main types of questions:

* **Data Profiling & Exploration:** Use these to understand the shape and content of your data.
    * *"What are all the unique values in the 'Country Key' column?"*
    * *"Show me a summary of the 'Transaction Value' column."*
    * *"How many transactions are there for each fiscal year?"*
* **Data Quality & Anomaly Detection:** Use these to find potential errors or inconsistencies.
    * *"Are there any rows where the 'Clearing Date' is empty or null?"*
    * *"Show me any transactions with a negative value."*
    * *"Are there any duplicate records in the data?"*
* **Simple Business Questions:** Use these to get specific insights related to your business operations.
    * *"What's the total transaction value for credit transactions (S) versus debit transactions (H)?"*
    * *"Filter the data to only show me transactions from Fiscal Year 2017."*
    * *"What percentage of the total transaction value comes from the US?"*

#### **Understanding the AI's Response**

When you ask a question, the AI provides a comprehensive, multi-part response right in the chat window. Each response block may contain:

1.  **Summary:** A one or two-sentence summary at the top, giving you the key insight immediately.
2.  **Textual Answer:** A brief introductory sentence like "Here are the results of your query:".
3.  **Data Table:** The detailed data that answers your question, presented in a sortable table.
4.  **Interactive Chart:** If your data can be visualized (e.g., for comparisons or trends), an interactive chart will be automatically generated. You can hover your mouse over the chart elements to see precise values.
5.  **Code (Optional):** For transparency, you can click on **"View Generated SQL Query"** or **"View Generated Visualization Code"** to see the code the AI used behind the scenes. This is completely optional and can be ignored.

#### **Using Conversational Context (Follow-up Questions)**

The AI remembers the context of your conversation. This means you can ask follow-up questions without having to repeat yourself.

* **Example Flow:**
    1.  **You ask:** *"Show me the total transaction value for each country."*
    2.  The AI responds with a table and a bar chart.
    3.  **You ask:** *"Now, can you show that as a pie chart?"*
    4.  The AI will understand you're referring to the previous result and will generate a pie chart of the same data.

---

### 3. UI Guide

This guide explains the components of the application screen.

![A diagram of the user interface showing the main sections: the title, the raw data expander, the chat history, and the chat input box.](https://storage.googleapis.com/bard-public/images/2024/06/25/11/image_0.png)

1.  **Application Title:** At the top of the page, displays the name of the application.
2.  **View Raw Data Source:** A single, collapsible section that contains your full, original dataset. Click to open, click again to close.
3.  **Chat History:** The main area of the screen. It displays the entire conversation between you and the AI, with the newest responses at the bottom.
4.  **Example Question Button:** Appears at the start of a session to help you get started. Clicking it sends a sample question to the AI.
5.  **Chat Input:** The text box at the very bottom of the screen where you type your questions.
6.  **AI Response Block:** Each response from the assistant is a self-contained block within the chat history, holding the summary, data table, chart, and optional code viewers.

---

### 4. FAQs (Frequently Asked Questions)

**Q: What happens if I ask a question the AI doesn't understand or makes a mistake?**

**A:** If the AI cannot generate a valid query or if the query results in an error, it will display an error message in the chat. This helps you know that the request could not be completed, and you can try rephrasing your question.

**Q: What if my question results in no data?**

**A:** If your query is valid but returns no results (for example, asking for data from a year that doesn't exist in the set), the AI will inform you with a message like: "The query ran successfully but returned no results."

**Q: How do I see the exact data a chart is based on?**

**A:** Every time the AI generates a chart, it *also* displays the data table it used to create that chart. The table is always located just above the chart in the same response block.

**Q: Can I combine filters in my questions?**

**A:** Yes. You can ask complex questions that combine multiple conditions. For example: *"Show me all back-posted credit transactions from the US in 2018."*