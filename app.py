import streamlit as st

from db import get_headline_metrics, get_product_count


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

st.metric("products rows", get_product_count())
