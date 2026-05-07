import datetime

import altair as alt
import streamlit as st

from db import get_daily_revenue, get_headline_metrics, get_product_count


def _pct_delta(current, prior):
    if prior == 0:
        return None
    return f"{(current - prior) / prior * 100:+.1f}%"


st.title("Basket Craft Dashboard")

m = get_headline_metrics()

aov_current = m["revenue_current"] / m["orders_current"] if m["orders_current"] else 0.0
aov_prior   = m["revenue_prior"]   / m["orders_prior"]   if m["orders_prior"]   else 0.0
aov_delta   = _pct_delta(aov_current, aov_prior) if m["orders_current"] and m["orders_prior"] else None

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue",   f"${m['revenue_current']:,.2f}", _pct_delta(m["revenue_current"], m["revenue_prior"]))
col2.metric("Total Orders",    f"{m['orders_current']:,}",      _pct_delta(m["orders_current"],  m["orders_prior"]))
col3.metric("Avg Order Value", f"${aov_current:,.2f}",          aov_delta)
col4.metric("Items Sold",      f"{m['items_current']:,}",       _pct_delta(m["items_current"],   m["items_prior"]))

with st.sidebar:
    st.header("Filters")
    start_date, end_date = st.slider(
        "Date range",
        min_value=datetime.date(2023, 3, 1),
        max_value=datetime.date(2026, 3, 31),
        value=(datetime.date(2023, 3, 1), datetime.date(2026, 3, 31)),
        format="MMM D, YYYY",
    )

st.subheader("Revenue Trend")

if True:
    df = get_daily_revenue(start_date, end_date)
    if df.empty:
        st.info("No revenue data for the selected date range.")
    else:
        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x=alt.X("order_date:T", title="Date"),
                y=alt.Y("revenue:Q", title="Revenue ($)"),
                tooltip=[
                    alt.Tooltip("order_date:T", title="Date",    format="%b %d, %Y"),
                    alt.Tooltip("revenue:Q",    title="Revenue", format="$,.2f"),
                ],
            )
        )
        st.altair_chart(chart, use_container_width=True)

st.metric("products rows", get_product_count())
