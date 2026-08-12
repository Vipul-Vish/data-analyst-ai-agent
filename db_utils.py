"""
db_utils.py
Handles loading data (CSV) into an in-memory/local SQLite database
and extracting schema information the AI agent needs to write SQL.
"""

import sqlite3
import pandas as pd
import re


def load_csv_to_sqlite(csv_path: str, db_path: str = "data.db", table_name: str = "data") -> str:
    """
    Loads a CSV file into a SQLite database table.
    Returns the table name used.
    """
    if csv_path.lower().endswith((".xlsx", ".xls")):
       df = pd.read_excel(csv_path)
    else:
       df = pd.read_csv(csv_path)

    # Clean column names: lowercase, replace spaces/special chars with underscore
    df.columns = [
        re.sub(r"[^a-z0-9_]", "_", col.strip().lower().replace(" ", "_"))
        for col in df.columns
    ]

    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    return table_name


def get_schema(db_path: str = "data.db") -> str:
    """
    Returns a text description of all tables and columns in the database.
    This schema string is fed to the LLM so it knows what it can query.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    schema_parts = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        col_descriptions = [f"{col[1]} ({col[2]})" for col in columns]
        schema_parts.append(f"Table: {table}\nColumns: {', '.join(col_descriptions)}")

        # Add a small sample of data so the model understands values/format
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        sample_rows = cursor.fetchall()
        if sample_rows:
            schema_parts.append(f"Sample rows: {sample_rows}")

    conn.close()
    return "\n\n".join(schema_parts)


def run_query(sql: str, db_path: str = "data.db") -> pd.DataFrame:
    """
    Executes a SQL query against the SQLite database and returns a DataFrame.
    Only SELECT statements are allowed for safety.
    """
    cleaned = sql.strip().lower()
    if not cleaned.startswith("select"):
        raise ValueError("Only SELECT queries are allowed for safety reasons.")

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql, conn)
    finally:
        conn.close()
    return df
