import streamlit as st

from db import get_product_count

st.title("Basket Craft Dashboard")
st.metric("dim_products rows", get_product_count())
