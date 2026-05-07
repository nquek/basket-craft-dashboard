# Headline Metrics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add four headline KPI metrics (Total Revenue, Total Orders, Avg Order Value, Items Sold) to the dashboard, each showing the last complete calendar month's value and a percentage change versus the month before.

**Architecture:** A single new `get_headline_metrics()` function in `db.py` runs one Snowflake query using two CTEs — `order_agg` aggregates revenue and order count from `ORDERS`, and `item_agg` counts rows in `ORDER_ITEMS` joined to `ORDERS` for the date. Both CTEs are left-joined for the two target months. `app.py` calls this function and renders a four-column `st.metric` row immediately below the title. AOV is derived in Python.

**Tech Stack:** Python 3, Streamlit, Snowflake Connector, pytest (new dev dependency)

---

### Task 1: Add `get_headline_metrics()` to `db.py`

**Files:**
- Modify: `db.py`
- Create: `tests/__init__.py`
- Create: `tests/test_db.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add pytest to requirements and write failing tests**

Add `pytest` to `requirements.txt`:

```
streamlit
snowflake-connector-python
python-dotenv
pytest
```

Install it:

```bash
source .venv/bin/activate && pip install pytest
```

Create `tests/__init__.py` (empty file).

Create `tests/test_db.py`:

```python
from unittest.mock import MagicMock, patch

import db


def _make_mock_conn(row):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = row
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


def test_get_headline_metrics_returns_six_keys():
    db.get_headline_metrics.clear()
    mock_conn = _make_mock_conn((50000.0, 1500, 3000, 45000.0, 1400, 2800))
    with patch("db._connect", return_value=mock_conn):
        result = db.get_headline_metrics()
    expected_keys = {"revenue_current", "orders_current", "items_current",
                     "revenue_prior", "orders_prior", "items_prior"}
    assert set(result.keys()) == expected_keys


def test_get_headline_metrics_maps_row_to_dict():
    db.get_headline_metrics.clear()
    mock_conn = _make_mock_conn((50000.0, 1500, 3000, 45000.0, 1400, 2800))
    with patch("db._connect", return_value=mock_conn):
        result = db.get_headline_metrics()
    assert result["revenue_current"] == 50000.0
    assert result["orders_current"] == 1500
    assert result["items_current"] == 3000
    assert result["revenue_prior"] == 45000.0
    assert result["orders_prior"] == 1400
    assert result["items_prior"] == 2800
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
source .venv/bin/activate && python -m pytest tests/test_db.py -v
```

Expected: both tests FAIL with `AttributeError: module 'db' has no attribute 'get_headline_metrics'`

- [ ] **Step 3: Implement `get_headline_metrics()` in `db.py`**

Append this function after the existing `get_product_count` function in `db.py`:

```python
@st.cache_data(ttl=600)
def get_headline_metrics() -> dict:
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute("""
            WITH target_months AS (
                SELECT
                    DATE_TRUNC('month', DATEADD('month', -1, CURRENT_DATE())) AS current_month,
                    DATE_TRUNC('month', DATEADD('month', -2, CURRENT_DATE())) AS prior_month
            ),
            order_agg AS (
                SELECT
                    DATE_TRUNC('month', TO_TIMESTAMP_NTZ(CREATED_AT / 1000000000)) AS order_month,
                    SUM(PRICE_USD)  AS revenue,
                    COUNT(ORDER_ID) AS orders
                FROM ORDERS
                WHERE DATE_TRUNC('month', TO_TIMESTAMP_NTZ(CREATED_AT / 1000000000))
                    IN (SELECT current_month FROM target_months
                        UNION ALL SELECT prior_month FROM target_months)
                GROUP BY 1
            ),
            item_agg AS (
                SELECT
                    DATE_TRUNC('month', TO_TIMESTAMP_NTZ(o.CREATED_AT / 1000000000)) AS order_month,
                    COUNT(oi.ORDER_ITEM_ID) AS items
                FROM ORDERS o
                JOIN ORDER_ITEMS oi ON o.ORDER_ID = oi.ORDER_ID
                WHERE DATE_TRUNC('month', TO_TIMESTAMP_NTZ(o.CREATED_AT / 1000000000))
                    IN (SELECT current_month FROM target_months
                        UNION ALL SELECT prior_month FROM target_months)
                GROUP BY 1
            )
            SELECT
                COALESCE(oa_curr.revenue, 0)  AS revenue_current,
                COALESCE(oa_curr.orders,  0)  AS orders_current,
                COALESCE(ia_curr.items,   0)  AS items_current,
                COALESCE(oa_prior.revenue, 0) AS revenue_prior,
                COALESCE(oa_prior.orders,  0) AS orders_prior,
                COALESCE(ia_prior.items,   0) AS items_prior
            FROM target_months tm
            LEFT JOIN order_agg oa_curr  ON oa_curr.order_month  = tm.current_month
            LEFT JOIN order_agg oa_prior ON oa_prior.order_month = tm.prior_month
            LEFT JOIN item_agg  ia_curr  ON ia_curr.order_month  = tm.current_month
            LEFT JOIN item_agg  ia_prior ON ia_prior.order_month = tm.prior_month
        """)
        row = cur.fetchone()
        keys = ["revenue_current", "orders_current", "items_current",
                "revenue_prior", "orders_prior", "items_prior"]
        return dict(zip(keys, row))
    finally:
        conn.close()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
source .venv/bin/activate && python -m pytest tests/test_db.py -v
```

Expected: both tests PASS

- [ ] **Step 5: Commit**

```bash
git add db.py tests/__init__.py tests/test_db.py requirements.txt
git commit -m "feat: add get_headline_metrics() to db.py"
```

---

### Task 2: Add headline metrics row to `app.py`

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Update `app.py`**

Replace the full contents of `app.py` with:

```python
import streamlit as st

from db import get_headline_metrics, get_product_count

st.title("Basket Craft Dashboard")

m = get_headline_metrics()


def _pct_delta(current, prior):
    if prior == 0:
        return None
    return f"{(current - prior) / prior * 100:+.1f}%"


aov_current = m["revenue_current"] / m["orders_current"] if m["orders_current"] else 0.0
aov_prior   = m["revenue_prior"]   / m["orders_prior"]   if m["orders_prior"]   else 0.0
aov_delta   = _pct_delta(aov_current, aov_prior) if m["orders_current"] and m["orders_prior"] else None

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue",   f"${m['revenue_current']:,.2f}", _pct_delta(m["revenue_current"], m["revenue_prior"]))
col2.metric("Total Orders",    f"{m['orders_current']:,}",      _pct_delta(m["orders_current"],  m["orders_prior"]))
col3.metric("Avg Order Value", f"${aov_current:,.2f}",          aov_delta)
col4.metric("Items Sold",      f"{m['items_current']:,}",       _pct_delta(m["items_current"],   m["items_prior"]))

st.metric("products rows", get_product_count())
```

- [ ] **Step 2: Run the app and verify**

```bash
source .venv/bin/activate && streamlit run app.py
```

Open the browser URL shown. Confirm:
- Four metric cards appear in a row directly below the title
- Each shows a value and a colored percentage delta (green for positive, red for negative)
- Revenue and AOV are formatted with `$` and two decimal places
- Orders and Items Sold are whole numbers with comma separators
- The "products rows" metric still appears below the headline row

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add headline metrics row to dashboard"
```
