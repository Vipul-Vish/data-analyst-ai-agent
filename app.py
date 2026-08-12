
"""
app.py
Streamlit UI for the "Chat with Your Data" AI Agent.
Upload a CSV, ask questions in plain English, get SQL + answers + charts.
"""
 
import streamlit as st
import pandas as pd
import plotly.express as px
import os
 
from db_utils import load_csv_to_sqlite, get_schema
from agent import TextToSQLAgent
 
st.set_page_config(page_title="Chat with Your Data", page_icon="📊", layout="wide")
 
st.title("📊 Chat with Your Data — AI Analyst Agent")
st.caption("Upload a CSV, ask questions in plain English, get instant SQL + insights.")
 
# ---------------------------
# API key: loaded from backend only (env var / HF secret), never shown in UI
# ---------------------------
api_key_input = os.getenv("GROQ_API_KEY", "")
 
if not api_key_input:
    st.error("API key not configured. Please contact the app owner.")
    st.stop()
 
# ---------------------------
# Sidebar: setup
# ---------------------------
with st.sidebar:
    st.header("⚙️ Setup")
 
    uploaded_file = st.file_uploader(
        "Upload your dataset (CSV or Excel)", type=["csv", "xlsx", "xls"]
    )
 
    st.markdown("---")
    st.markdown(
        "**Example questions:**\n"
        "- Top 5 rows by revenue\n"
        "- How many records per category?\n"
        "- Average value by group, sorted descending"
    )
 
# ---------------------------
# Session state init
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "schema" not in st.session_state:
    st.session_state.schema = None
if "db_ready" not in st.session_state:
    st.session_state.db_ready = False
 
# ---------------------------
# Load data
# ---------------------------
if uploaded_file is not None and not st.session_state.db_ready:
    with st.spinner("Loading dataset..."):
        file_ext = uploaded_file.name.split(".")[-1].lower()
        temp_path = f"uploaded_data.{file_ext}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
 
        load_csv_to_sqlite(temp_path, db_path="data.db", table_name="data")
        st.session_state.schema = get_schema("data.db")
        st.session_state.db_ready = True
 
    st.sidebar.success("Dataset loaded! Table name: `data`")
 
if st.session_state.schema:
    with st.sidebar.expander("View detected schema"):
        st.text(st.session_state.schema)
 
# ---------------------------
# Chat interface
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("dataframe") is not None:
            st.dataframe(msg["dataframe"], use_container_width=True)
        if msg.get("sql"):
            with st.expander("View SQL query used"):
                st.code(msg["sql"], language="sql")
 
question = st.chat_input("Ask a question about your data...")
 
if question:
    if not st.session_state.db_ready:
        st.error("Please upload a CSV or Excel file first.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
 
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                agent = TextToSQLAgent(api_key=api_key_input)
                result = agent.ask(question, st.session_state.schema, db_path="data.db")
 
            st.markdown(result["explanation"])
 
            if result["dataframe"] is not None and not result["dataframe"].empty:
                st.dataframe(result["dataframe"], use_container_width=True)
 
                # Auto-chart if there are 2 columns and one is numeric
                df = result["dataframe"]
                if df.shape[1] == 2:
                    numeric_cols = df.select_dtypes(include="number").columns
                    if len(numeric_cols) >= 1:
                        try:
                            fig = px.bar(df, x=df.columns[0], y=numeric_cols[0])
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception:
                            pass
 
            with st.expander("View SQL query used"):
                st.code(result["sql"], language="sql")
 
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["explanation"],
            "dataframe": result["dataframe"],
            "sql": result["sql"],
        })
