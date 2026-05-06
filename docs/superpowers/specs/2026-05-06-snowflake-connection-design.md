# Snowflake Connection — Design Spec

## Overview

Connect the Basket Craft Dashboard to Snowflake and display a smoke-test row count from `dim_products`. Credentials are loaded from the existing `.env` file. The query result is cached for 10 minutes.

## Architecture

Two files change or are created:

| File | Change | Purpose |
|---|---|---|
| `db.py` | Create | All Snowflake logic — connection + cached query |
| `app.py` | Modify | Display the row count from `db.get_product_count()` |
| `requirements.txt` | Modify | Add `snowflake-connector-python` and `python-dotenv` |

## `db.py`

- Load credentials from `.env` using `python-dotenv` (`load_dotenv()`).
- Build a Snowflake connection using `snowflake.connector.connect()` with these keys from `.env`: `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`.
- Expose one public function: `get_product_count() -> int`.
  - Decorated with `@st.cache_data(ttl=600)`.
  - Runs `SELECT COUNT(*) FROM dim_products`.
  - Returns the integer result.
  - Opens and closes its own connection (no shared connection state).

## `app.py`

- Import `get_product_count` from `db`.
- Add `st.metric("dim_products rows", get_product_count())` below the existing title.

## `requirements.txt`

- Append pinned versions of `snowflake-connector-python` and `python-dotenv` (versions determined at install time).

## Out of Scope

- Connection pooling or shared connection objects
- Multiple queries or tables
- Error UI (connection failures will surface as Streamlit exceptions for now)
- Streamlit secrets migration
- Any other Snowflake tables beyond `dim_products`
