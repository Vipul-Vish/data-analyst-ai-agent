# Chat with Your Data — AI Analyst Agent

An AI-powered Text-to-SQL agent that lets you ask questions about your dataset
in plain English (or Hinglish) and get instant SQL queries + answers + charts.

Built with: **Python, Streamlit, Groq API (Llama 3.1), SQLite, Pandas, Plotly**

---

## How it works

1. Upload any CSV dataset (e.g. your Netflix or Zepto dataset)
2. Ask a question like *"Top 5 countries by number of titles"*
3. The agent:
   - **Decides**: converts your question into a SQL query using Groq's LLM
   - **Acts**: runs that SQL query safely against your data
   - **Observes**: explains the result back to you in plain English
4. Results show up as a table + auto-generated chart (when applicable)

---

## Setup (Windows)

### 1. Install dependencies

Open PowerShell in this project folder and run:

```
pip install -r requirements.txt
```

### 2. Add your Groq API key

Rename `.env.example` to `.env` and paste your key inside:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

(You can also just paste the key directly in the app's sidebar if you skip this step.)

### 3. Run the app

```
streamlit run app.py
```

This opens the app in your browser automatically at `http://localhost:8501`.

---

## Project structure

```
data-analyst-ai-agent/
├── app.py           # Streamlit UI (chat interface)
├── agent.py         # Core AI agent (Groq API calls, SQL generation)
├── db_utils.py      # CSV -> SQLite loading + schema extraction + query runner
├── requirements.txt # Python dependencies
├── .env.example     # Template for API key
└── README.md
```

---

## Safety notes

- Only `SELECT` queries are ever executed — the agent cannot modify or delete data.
- Your data stays local (SQLite file on your machine); only the question + schema
  + small data samples are sent to Groq's API to generate SQL.

---

## Deploying online (for your portfolio/resume)

To showcase this as a live demo instead of just code:

1. Push this folder to GitHub (e.g. `23f3003765/chat-with-data-agent`)
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud) (free)
3. Connect your GitHub repo, set `app.py` as the entry point
4. Add your `GROQ_API_KEY` under Streamlit's "Secrets" settings
5. Deploy — you'll get a public link to add to your resume/LinkedIn

---

## Resume line you can use

> Built an AI-powered Text-to-SQL agent enabling natural language querying
> over datasets (8,000+ rows), using Groq's LLM API, Python, and Streamlit;
> deployed as a live web app.
