import streamlit as st
import plotly.express as px
import pandas as pd
from data_utils import load_and_clean_data

st.set_page_config(page_title="Business Dashboard", layout="wide")

st.title("📈 Automated Business Dashboard")

# Sidebar: Data upload
st.sidebar.header("1) Load Data")
uploaded = st.sidebar.file_uploader("Upload data", type=["csv"])

if uploaded is None:
    st.sidebar.info("No file uploaded — using sample dataset.")
    df = load_and_clean_data("data/customer_shopping_data.csv")
else:
    df = load_and_clean_data(uploaded)

if df.empty:
    st.warning("No data available. Please upload a valid CSV.")
    st.stop()

# Sidebar: filters
st.sidebar.header("2) Filters")
min_date, max_date = df["invoice_date"].min(), df["invoice_date"].max()
date_range = st.sidebar.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date, end_date = min_date, max_date

categories = st.sidebar.multiselect("Category", options=sorted(df["category"].dropna().unique()))
malls = st.sidebar.multiselect("Shopping Mall", options=sorted(df["shopping_mall"].dropna().unique()))
payment_methods = st.sidebar.multiselect("Payment Method", options=sorted(df["payment_method"].dropna().unique()))
genders = st.sidebar.multiselect("Gender", options=sorted(df["gender"].dropna().unique()))

# Apply filters
mask = (df["invoice_date"] >= start_date) & (df["invoice_date"] <= end_date)
if categories:
    mask &= df["category"].isin(categories)
if malls:
    mask &= df["shopping_mall"].isin(malls)
if payment_methods:
    mask &= df["payment_method"].isin(payment_methods)
if genders:
    mask &= df["gender"].isin(genders)

f = df.loc[mask].copy()

# KPIs
total_revenue = float(f["revenue"].sum())
transactions = int(f["invoice_no"].nunique())
unique_customers = int(f["customer_id"].nunique())
aov = float(f.groupby("invoice_no")["revenue"].sum().mean()) if transactions > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"{total_revenue:,.2f}")
col2.metric("Transactions", f"{transactions:,}")
col3.metric("Unique Customers", f"{unique_customers:,}")
col4.metric("Avg Order Value", f"{aov:,.2f}")

st.divider()

# Charts
monthly = f.groupby("month", as_index=False)["revenue"].sum()
st.plotly_chart(px.line(monthly, x="month", y="revenue", title="Revenue Over Time (Monthly)"), use_container_width=True)

cat_rev = f.groupby("category", as_index=False)["revenue"].sum()
st.plotly_chart(px.bar(cat_rev, x="category", y="revenue", title="Revenue by Category"), use_container_width=True)

pay_rev = f.groupby("payment_method", as_index=False)["revenue"].sum()
st.plotly_chart(px.pie(pay_rev, names="payment_method", values="revenue", title="Revenue by Payment Method"), use_container_width=True)

cust_rev = f.groupby("customer_id", as_index=False)["revenue"].sum().nlargest(10, "revenue")
st.plotly_chart(px.bar(cust_rev, x="customer_id", y="revenue", title="Top 10 Customers by Revenue"), use_container_width=True)

mall_rev = f.groupby("shopping_mall", as_index=False)["revenue"].sum()
st.plotly_chart(px.bar(mall_rev, x="shopping_mall", y="revenue", title="Revenue by Shopping Mall"), use_container_width=True)

age_rev = f.groupby("age_group", as_index=False)["revenue"].sum()
st.plotly_chart(px.bar(age_rev, x="age_group", y="revenue", title="Revenue by Age Group"), use_container_width=True)

st.caption("Tip: Use the sidebar filters. KPIs and charts update automatically.")
