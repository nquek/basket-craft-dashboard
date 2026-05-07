import datetime
import os

import pandas as pd
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _connect():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )


@st.cache_data(ttl=600)
def get_product_count() -> int:
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM products")
        return cur.fetchone()[0]
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_headline_metrics() -> dict:
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute("""
            WITH latest_months AS (
                SELECT DISTINCT DATE_TRUNC('month', TO_TIMESTAMP_NTZ(CREATED_AT / 1000000000)) AS order_month
                FROM ORDERS
                ORDER BY 1 DESC
                LIMIT 2
            ),
            target_months AS (
                SELECT MAX(order_month) AS current_month, MIN(order_month) AS prior_month
                FROM latest_months
            ),
            order_agg AS (
                SELECT
                    DATE_TRUNC('month', TO_TIMESTAMP_NTZ(CREATED_AT / 1000000000)) AS order_month,
                    SUM(PRICE_USD)  AS revenue,
                    COUNT(ORDER_ID) AS orders
                FROM ORDERS
                WHERE DATE_TRUNC('month', TO_TIMESTAMP_NTZ(CREATED_AT / 1000000000))
                    IN (SELECT current_month FROM target_months
                        UNION SELECT prior_month FROM target_months)
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
                        UNION SELECT prior_month FROM target_months)
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
        if row is None:
            return {k: 0 for k in keys}
        return dict(zip(keys, row))
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_daily_revenue(start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DATE(TO_TIMESTAMP_NTZ(CREATED_AT / 1000000000)) AS order_date,
                   SUM(PRICE_USD) AS revenue
            FROM ORDERS
            WHERE DATE(TO_TIMESTAMP_NTZ(CREATED_AT / 1000000000)) BETWEEN %s AND %s
            GROUP BY 1
            ORDER BY 1
        """, (start_date.isoformat(), end_date.isoformat()))
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=["order_date", "revenue"])
    finally:
        conn.close()
