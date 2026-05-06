# Basket Craft Dashboard — Minimal Streamlit Setup

## Overview

Bootstrap a runnable Streamlit app as the starting point for the Basket Craft Dashboard. Scope is intentionally minimal: environment, one app file, one title.

## Environment

- Python virtual environment managed with `venv`, located at `.venv/` in the project root.
- Dependencies tracked in `requirements.txt` at the project root, pinning `streamlit`.

## App

- Single file: `app.py` at the project root.
- Contents: one `st.title("Basket Craft Dashboard")` call — nothing else.

## Running

```bash
source .venv/bin/activate
streamlit run app.py
```

## Out of Scope

- Data connections (Snowflake integration comes later)
- Sidebar, pages, charts, or any UI beyond the title
- Authentication or secrets management beyond the existing `.env`
