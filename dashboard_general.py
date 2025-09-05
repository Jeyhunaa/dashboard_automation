import streamlit as st
import plotly.express as px
from data_utils_general import load_and_process_data
import pandas as pd

st.set_page_config(page_title="General Dashboard", layout="wide")
st.title("📊 Generalized Dashboard for Any Tabular Dataset")

# Sidebar: data upload
st.sidebar.header("1) Load Data")
uploaded = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

DATA_PATH = "data/customer_shopping_data.csv"

if uploaded is None:
    st.sidebar.info(f"No file uploaded — using default dataset: {DATA_PATH}")
    data_dict = load_and_process_data(DATA_PATH)
else:
    data_dict = load_and_process_data(uploaded)

df = data_dict["df"]
numeric_cols = data_dict["numeric_cols"]
categorical_cols = data_dict["categorical_cols"]
datetime_cols = data_dict["datetime_cols"]

if df.empty:
    st.warning("No valid data found.")
    st.stop()

# ---------------- Filters ----------------
st.sidebar.header("2) Filters")
filtered_df = df.copy()

# Date filters
for dt_col in datetime_cols:
    valid_dates = filtered_df[dt_col].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        date_range = st.sidebar.date_input(
            f"Filter {dt_col}", value=(min_date, max_date),
            min_value=min_date, max_value=max_date
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df[dt_col].notna()) &
                (filtered_df[dt_col].dt.date >= start_date) &
                (filtered_df[dt_col].dt.date <= end_date)
            ]

# Categorical filters
for cat_col in categorical_cols:
    options = st.sidebar.multiselect(
        f"Filter {cat_col}",
        options=sorted(filtered_df[cat_col].dropna().unique())
    )
    if options:
        filtered_df = filtered_df[filtered_df[cat_col].isin(options)]

# ---------------- Data Preview ----------------
st.subheader("📌 Top 5 rows of the dataset")
st.dataframe(filtered_df.head())

# ---------------- KPIs ----------------
st.subheader("📈 KPIs")
col1, col2, col3, col4 = st.columns(4)

if numeric_cols:
    col1.metric(f"Sum of {numeric_cols[0]}", f"{filtered_df[numeric_cols[0]].sum():,.2f}")
    col2.metric(f"Mean of {numeric_cols[0]}", f"{filtered_df[numeric_cols[0]].mean():,.2f}")
else:
    col1.metric("No numeric columns", "-")
    col2.metric("No numeric columns", "-")

if categorical_cols:
    top_cat = filtered_df[categorical_cols[0]].mode()[0]
    col3.metric(f"Most common {categorical_cols[0]}", top_cat)
else:
    col3.metric("No categorical columns", "-")

col4.metric("Total rows", f"{len(filtered_df)}")

# ---------------- Charts ----------------
st.subheader("📊 Charts")

# Numeric vs datetime trends
for dt_col in datetime_cols:
    for num_col in numeric_cols:
        fig = px.line(
            filtered_df,
            x=dt_col,
            y=num_col,
            title=f"{num_col} over {dt_col}"
        )
        st.plotly_chart(fig, use_container_width=True)

# Categorical distributions
for cat_col in categorical_cols:
    counts = filtered_df[cat_col].value_counts().reset_index()
    counts.columns = [cat_col, "count"]
    fig = px.bar(counts, x=cat_col, y="count", title=f"Counts of {cat_col}")
    st.plotly_chart(fig, use_container_width=True)

# Correlation heatmap for numeric columns
if len(numeric_cols) > 1:
    import plotly.figure_factory as ff
    corr = filtered_df[numeric_cols].corr()
    fig = ff.create_annotated_heatmap(
        z=corr.values,
        x=list(corr.columns),
        y=list(corr.index),
        colorscale="Viridis"
    )
    st.plotly_chart(fig, use_container_width=True)
