# ==========================================
# analysis.py (FINAL FIXED VERSION)
# ==========================================

import pandas as pd
import boto3
import plotly.express as px
import streamlit as st
from io import StringIO

# ==========================================
# AWS CONFIG (UNCHANGED)
# ==========================================

AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]
REGION = st.secrets["AWS_REGION"]

BUCKET_NAME = "energy-data-backup"
FILE_KEY = "final/final_dataset.csv"

# ==========================================
# LOAD DATA FROM S3
# ==========================================

def load_data_from_s3():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=REGION
    )

    obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    data = obj["Body"].read().decode("utf-8")

    df = pd.read_csv(StringIO(data))
    return df


# ==========================================
# LOAD + CLEAN DATA (FIXED)
# ==========================================

df = load_data_from_s3()

# Convert numeric columns safely
numeric_cols = ["production_per_capita", "electricity", "renewable", "losses", "access", "gdp_per_capita"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ✅ CRITICAL FIX: YEAR CLEANING
df["year"] = pd.to_numeric(df["year"], errors="coerce")

# ✅ ONLY DROP IMPORTANT NULLS (NOT EVERYTHING)
df = df.dropna(subset=[
    "year",
    "production_per_capita",
    "electricity"
])

df["year"] = df["year"].astype(int)

# Latest year selection
latest_year = int(df["year"].max())
df_latest = df[df["year"] == latest_year].copy()

print("Using year:", latest_year)

# ==========================================
# ENERGY EQUITY SCORE (NEW)
# ==========================================

# Normalize electricity consumption (0–100 scale)
df_latest["electricity_norm"] = (
    df_latest["electricity"] / df_latest["electricity"].max()
) * 100

# Energy Equity Score (balanced metric)
df_latest["energy_equity_score"] = (
    df_latest["access"] * 0.6 +
    df_latest["electricity_norm"] * 0.4
)
# ✅ TEMP DEBUG (PUT IT HERE)
print(df_latest[[
    "country_name",
    "access",
    "electricity",
    "energy_equity_score"
]].head())
# ==========================================
# ================= ANALYSIS 1 =============
# Energy Gap
# ==========================================

df_latest["energy_gap_per_capita"] = (
    df_latest["production_per_capita"] - df_latest["electricity"]
)

df_latest["status"] = df_latest["energy_gap_per_capita"].apply(
    lambda x: "Surplus" if x > 0 else "Deficit"
)

top_surplus = df_latest.sort_values(
    "energy_gap_per_capita", ascending=False
).head(10)[
    ["country_name", "production_per_capita", "electricity", "energy_gap_per_capita"]
]

top_deficit = df_latest.sort_values(
    "energy_gap_per_capita", ascending=True
).head(10)[
    ["country_name", "production_per_capita", "electricity", "energy_gap_per_capita"]
]

fig_energy_gap = px.scatter(
    df_latest,
    x="production_per_capita",
    y="electricity",
    color="status",
    hover_name="country_name",
    title="Energy Gap (Production vs Consumption per Capita)",
    color_discrete_map={"Surplus": "green", "Deficit": "red"}
)

# ==========================================
# ================= ANALYSIS 2 =============
# Renewable Impact
# ==========================================

def renewable_group(x):
    if x < 20:
        return "Low"
    elif x < 50:
        return "Medium"
    else:
        return "High"

df_latest["renewable_group"] = df_latest["renewable"].apply(renewable_group)

fig_renewable_access = px.scatter(
    df_latest,
    x="renewable",
    y="access",
    color="renewable_group",
    hover_name="country_name",
    title="Renewable vs Electricity Access"
)

fig_renewable_losses = px.scatter(
    df_latest,
    x="renewable",
    y="losses",
    color="renewable_group",
    hover_name="country_name",
    title="Renewable vs Transmission Losses"
)

df_latest["sustainability_score"] = (
    df_latest["renewable"] * 0.4 +
    df_latest["access"] * 0.4 -
    df_latest["losses"] * 0.2
)

top5_sustainable = df_latest.sort_values(
    "sustainability_score", ascending=False
).head(10)[
    ["country_name", "renewable", "access", "losses", "sustainability_score"]
]

# ==========================================
# ================= ANALYSIS 3 =============
# Infrastructure Efficiency
# ==========================================

def loss_group(x):
    if x < 10:
        return "Low"
    elif x < 20:
        return "Medium"
    else:
        return "High"

df_latest["loss_group"] = df_latest["losses"].apply(loss_group)

fig_losses_access = px.scatter(
    df_latest,
    x="losses",
    y="access",
    color="loss_group",
    hover_name="country_name",
    title="Transmission Losses vs Access"
)

fig_losses_consumption = px.scatter(
    df_latest,
    x="losses",
    y="electricity",
    color="loss_group",
    hover_name="country_name",
    title="Transmission Losses vs Consumption"
)

top_high_losses = df_latest.sort_values(
    "losses", ascending=False
).head(10)[
    ["country_name", "losses", "electricity", "access"]
]

top_low_losses = df_latest.sort_values(
    "losses", ascending=True
).head(10)[
    ["country_name", "losses", "electricity", "access"]
]

# ==========================================
# GDP vs Energy Efficiency (A+ VERSION)
# ==========================================

df_gdp = df_latest.dropna(subset=["gdp_per_capita", "losses"]).copy()

def gdp_group(x):
    if x < 5000:
        return "Low Income"
    elif x < 20000:
        return "Middle Income"
    else:
        return "High Income"

df_gdp["gdp_group"] = df_gdp["gdp_per_capita"].apply(gdp_group)

# 🔥 A+ SCATTER WITH TRENDLINE
fig_gdp_losses = px.scatter(
    df_gdp,
    x="gdp_per_capita",
    y="losses",
    color="gdp_group",
    hover_name="country_name",
    title="GDP per Capita vs Transmission Losses",
    log_x=True,
    trendline="ols"   # ⭐ THIS IS KEY FOR A+
)

# Correlation
gdp_loss_corr = df_gdp["gdp_per_capita"].corr(df_gdp["losses"])

# KPIs
avg_loss = df_gdp["losses"].mean()
avg_gdp = df_gdp["gdp_per_capita"].mean()

top_inefficient = df_gdp.sort_values("losses", ascending=False).head(10)
top_efficient = df_gdp.sort_values("losses", ascending=True).head(10)

# ==========================================
# ================= ANALYSIS 5 =============
# Energy Equity vs GDP
# ==========================================

# Remove missing values
df_equity = df_latest.dropna(subset=["gdp_per_capita", "energy_equity_score"]).copy()

# GDP grouping (reuse logic if already exists)
def gdp_group(x):
    if x < 5000:
        return "Low Income"
    elif x < 20000:
        return "Middle Income"
    else:
        return "High Income"

df_equity["gdp_group"] = df_equity["gdp_per_capita"].apply(gdp_group)

# 🔥 MAIN VISUAL
fig_equity = px.scatter(
    df_equity,
    x="gdp_per_capita",
    y="energy_equity_score",
    color="gdp_group",
    hover_name="country_name",
    title="GDP vs Energy Equity",
    log_x=True,
    trendline="ols"
)

# Top performers
top_equity = df_equity.sort_values(
    "energy_equity_score", ascending=False
).head(10)[
    ["country_name", "gdp_per_capita", "energy_equity_score"]
]

# Lowest performers
low_equity = df_equity.sort_values(
    "energy_equity_score", ascending=True
).head(10)[
    ["country_name", "gdp_per_capita", "energy_equity_score"]
]
# ==========================================
# EXPORT FOR STREAMLIT
# ==========================================

analysis_results = {
    "energy_gap_fig": fig_energy_gap,
    "top_surplus": top_surplus,
    "top_deficit": top_deficit,

    "renewable_access_fig": fig_renewable_access,
    "renewable_losses_fig": fig_renewable_losses,
    "top_sustainable": top5_sustainable,

    "loss_access_fig": fig_losses_access,
    "loss_consumption_fig": fig_losses_consumption,
    "top_high_losses": top_high_losses,
    "top_low_losses": top_low_losses,
    
    "gdp_losses_fig": fig_gdp_losses,
    "gdp_loss_corr": gdp_loss_corr,
    "avg_loss": avg_loss,
    "avg_gdp": avg_gdp,
    "top_inefficient": top_inefficient,
    "top_efficient": top_efficient,
    
    "equity_fig": fig_equity,
    "top_equity": top_equity,
    "low_equity": low_equity
}