# Headline Metrics — Design Spec

## Overview

Add four headline KPI metrics to the Basket Craft Dashboard: Total Revenue, Total Orders, Average Order Value (AOV), and Total Items Sold. Each metric displays the value for the last complete calendar month alongside a percentage change versus the month before that.

## Data Layer

**New function:** `get_headline_metrics()` in `db.py`

- Decorated with `@st.cache_data(ttl=600)` (consistent with existing pattern).
- Runs a single Snowflake query against the `ORDERS` table.
- Converts the nanosecond `CREATED_AT` column via `TO_TIMESTAMP_NTZ(CREATED_AT / 1000000000)`.
- Filters to the two most recent complete calendar months using `DATE_TRUNC('month', ...)` and `DATEADD('month', -1/−2, CURRENT_DATE())`.
- Uses `CASE WHEN` conditional aggregation to compute both months in one pass, returning six values in a single row:
  - `revenue_current`, `revenue_prior` — `SUM(PRICE_USD)`
  - `orders_current`, `orders_prior` — `COUNT(*)`
  - `items_current`, `items_prior` — `SUM(ITEMS_PURCHASED)`
- Returns a plain `dict` with those six keys.
- AOV is derived in Python (`revenue / orders`) rather than in SQL to avoid division-by-zero and keep the query simple. If either month has zero orders, AOV and its delta display as `$0.00` with no delta.

**Revenue definition:** Gross revenue (sum of `PRICE_USD` from `ORDERS`). Refunds are excluded.

**Month window:** Last complete calendar month vs. the calendar month before that (not month-to-date).

## UI Layer

In `app.py`, a row of four `st.columns` is added immediately below `st.title`. Each column holds one `st.metric`:

| Column | Label | Value format | Delta |
|--------|-------|--------------|-------|
| 1 | Total Revenue | `$45,231.50` | `+5.2%` |
| 2 | Total Orders | `1,234` | `+3.1%` |
| 3 | Avg Order Value | `$36.65` | `+2.0%` |
| 4 | Items Sold | `2,891` | `+4.8%` |

- Delta is percentage change: `(current − prior) / prior × 100`, formatted to one decimal place with a `%` suffix.
- Streamlit renders positive deltas green and negative deltas red automatically via `st.metric`'s `delta` parameter.
- Revenue and AOV use `$` prefix with two decimal places. Orders and items are whole numbers with comma separators.
- The existing `st.metric("products rows", ...)` line is preserved below the new metrics row.

## Out of Scope

- Refund-adjusted (net) revenue
- Month-to-date comparisons
- Drill-downs, charts, or per-product breakdowns
- Any other tables (ORDER_ITEMS, WEBSITE_SESSIONS, etc.)
