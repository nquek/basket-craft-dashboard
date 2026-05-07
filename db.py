import os

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
