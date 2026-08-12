"""
agent.py
Core AI agent: takes a natural language question + database schema,
calls Groq's LLM to generate a SQL query, runs it, and explains the result
in plain English.
"""

import os
import re
from groq import Groq
from dotenv import load_dotenv
from db_utils import run_query

load_dotenv()

MODEL_NAME = "llama-3.1-8b-instant"  # fast + free-tier friendly (14,400 req/day)


class TextToSQLAgent:
    def __init__(self, api_key: str = None):
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not found. Set it in .env or pass it directly.")
        self.client = Groq(api_key=key)

    def _extract_sql(self, text: str) -> str:
        """Pulls the SQL query out of the model's response (handles code fences)."""
        match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def generate_sql(self, question: str, schema: str) -> str:
        """Step 1 (Decide): Ask the LLM to write a SQL query for the question."""
        system_prompt = f"""You are a SQL expert. Given a database schema and a
natural language question, write ONE valid SQLite SELECT query that answers it.

Rules:
- Only output the SQL query, wrapped in ```sql code fences.
- Only use SELECT statements. Never write INSERT/UPDATE/DELETE/DROP.
- Use only tables/columns that exist in the schema below.
- If the question is ambiguous, make a reasonable assumption.

Schema:
{schema}
"""
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            temperature=0,
            max_tokens=500,
        )
        raw_output = response.choices[0].message.content
        return self._extract_sql(raw_output)

    def explain_result(self, question: str, sql: str, result_df) -> str:
        """Step 2 (Observe): Ask the LLM to explain the result in plain English."""
        preview = result_df.head(10).to_string(index=False)
        prompt = f"""Question: {question}
SQL used: {sql}
Query result (first rows):
{preview}

In 2-4 short sentences, explain the answer in simple, plain English for a
non-technical business user. Mention key numbers directly."""

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()

    def ask(self, question: str, schema: str, db_path: str = "data.db"):
        """
        Full pipeline: Decide (generate SQL) -> Act (run query) -> Observe (explain).
        Returns a dict with sql, dataframe, and explanation.
        """
        sql = self.generate_sql(question, schema)

        try:
            df = run_query(sql, db_path)
        except Exception as e:
            return {
                "sql": sql,
                "dataframe": None,
                "explanation": f"The generated query failed to run: {e}",
                "error": True,
            }

        explanation = self.explain_result(question, sql, df)
        return {
            "sql": sql,
            "dataframe": df,
            "explanation": explanation,
            "error": False,
        }
