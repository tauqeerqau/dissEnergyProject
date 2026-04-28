# ==========================================
# visualization.py (INTERACTIVE DASHBOARD)
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px
from analysis import load_data_from_s3

st.set_page_config(layout="wide")

# ==========================================
# LOAD DATA
# ==========================================

df = load_data_from_s3()

# Clean
numeric_cols = ["production_per_capita", "electricity", "renewable", "losses", "access"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna()

# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.title("Filters")

# Country dropdown
countries = sorted(df["country_name"].unique())
selected_country = st.sidebar.selectbox("Select Country", countries)

# Year range slider
min_year = int(df["year"].min())
max_year = int(df["year"].max())

year_range = st.sidebar.slider(
    "Select Year Range",
    min_year,
    max_year,
    (min_year, max_year)
)

# ==========================================
# FILTER DATA
# ==========================================

filtered_df = df[
    (df["country_name"] == selected_country) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

# ==========================================
# TITLE
# ==========================================

st.title("🌍 Global Electricity Analysis")

st.write(
    "This dashboard explores electricity consumption, renewable share, "
    "and transmission losses for selected countries."
)

# ==========================================
# KPI METRICS
# ==========================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Mean Electricity Consumption (kWh per capita)",
    round(filtered_df["electricity"].mean(), 1)
)

col2.metric(
    "Mean Renewable Share (%)",
    round(filtered_df["renewable"].mean(), 1)
)

col3.metric(
    "Mean Transmission Losses (%)",
    round(filtered_df["losses"].mean(), 1)
)

# ==========================================
# CHART 1: Electricity Over Time
# ==========================================

st.subheader("Electricity Consumption per Capita Over Time")

fig1 = px.line(
    filtered_df,
    x="year",
    y="electricity",
    markers=True
)

st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# CHART 2: Renewable Over Time
# ==========================================

st.subheader("Renewable Energy Share Over Time")

fig2 = px.line(
    filtered_df,
    x="year",
    y="renewable",
    markers=True,
    color_discrete_sequence=["green"]
)

st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# CHART 3: Losses Over Time
# ==========================================

st.subheader("Transmission Losses Over Time")

fig3 = px.line(
    filtered_df,
    x="year",
    y="losses",
    markers=True,
    color_discrete_sequence=["red"]
)

st.plotly_chart(fig3, use_container_width=True)