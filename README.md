# Basket Craft Dashboard

**Live app:** https://nquek-basket-craft-dashboard-app-nmlh74.streamlit.app/

A Streamlit dashboard connected to Snowflake for analysing Basket Craft sales data.

## Features

- **Headline metrics** — Total Revenue, Total Orders, Avg Order Value, and Items Sold with month-over-month comparison
- **Revenue Trend** — Daily revenue line chart with a date range filter
- **Top Products by Revenue** — Horizontal bar chart of the top 10 products
- **Bundle Finder** — Pick any product and see what gets bought with it most often

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Create a `.env` file in the project root with your Snowflake credentials:

```
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_USER=...
SNOWFLAKE_PASSWORD=...
SNOWFLAKE_ROLE=...
SNOWFLAKE_WAREHOUSE=...
SNOWFLAKE_DATABASE=...
SNOWFLAKE_SCHEMA=...
```
