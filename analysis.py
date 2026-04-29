# ==========================================
# analysis.py (FINAL PRODUCTION VERSION)
# ==========================================

import pandas as pd
import boto3
import plotly.express as px
import streamlit as st
from io import StringIO
from botocore.exceptions import ClientError

# ==========================================
# AWS CONFIG (KEEPING YOUR KEYS)
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
    try:
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

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "NoSuchKey":
            st.warning("⚠️ Data file not found in S3. Please try again later.")
        else:
            st.error(f"❌ AWS Error: {error_code}")

        return None

    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


# ==========================================
# MAIN ANALYSIS FUNCTION
# ==========================================

def run_analysis():

    df = load_data_from_s3()

    # ------------------------------------------
    # HANDLE NO DATA
    # ------------------------------------------
    if df is None or df.empty:
        return None

    required_cols = [
        "production_per_capita", "electricity",
        "renewable", "losses", "access",
        "gdp_per_capita", "year", "country_name"
    ]

    missing_cols = [c for c in required_cols if c not in df.columns]

    if missing_cols:
        st.error(f"❌ Dataset is corrupted. Missing columns: {missing_cols}")
        return None

    # ------------------------------------------
    # CLEANING
    # ------------------------------------------
    numeric_cols = [
        "production_per_capita", "electricity",
        "renewable", "losses", "access", "gdp_per_capita"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    df = df.dropna(subset=[
        "year",
        "production_per_capita",
        "electricity"
    ])

    if df.empty:
        st.warning("⚠️ Dataset contains no usable records.")
        return None

    df["year"] = df["year"].astype(int)

    latest_year = int(df["year"].max())
    df_latest = df[df["year"] == latest_year].copy()

    if df_latest.empty:
        st.warning("⚠️ No data available for latest year.")
        return None

    # ------------------------------------------
    # ENERGY EQUITY
    # ------------------------------------------
    max_electricity = df_latest["electricity"].max()

    if max_electricity == 0 or pd.isna(max_electricity):
        st.warning("⚠️ Electricity data invalid.")
        return None

    df_latest["electricity_norm"] = (
        df_latest["electricity"] / max_electricity
    ) * 100

    df_latest["energy_equity_score"] = (
        df_latest["access"] * 0.6 +
        df_latest["electricity_norm"] * 0.4
    )

    # ------------------------------------------
    # ANALYSIS 1: ENERGY GAP
    # ------------------------------------------
    df_latest["energy_gap_per_capita"] = (
        df_latest["production_per_capita"] - df_latest["electricity"]
    )

    df_latest["status"] = df_latest["energy_gap_per_capita"].apply(
        lambda x: "Surplus" if x > 0 else "Deficit"
    )

    top_surplus = df_latest.sort_values(
        "energy_gap_per_capita", ascending=False
    ).head(10)

    top_deficit = df_latest.sort_values(
        "energy_gap_per_capita", ascending=True
    ).head(10)

    fig_energy_gap = px.scatter(
        df_latest,
        x="production_per_capita",
        y="electricity",
        color="status",
        hover_name="country_name",
        title="Energy Gap (Production vs Consumption)"
    )

    # ------------------------------------------
    # ANALYSIS 2: RENEWABLE
    # ------------------------------------------
    fig_renewable_access = px.scatter(
        df_latest,
        x="renewable",
        y="access",
        hover_name="country_name",
        title="Renewable vs Access"
    )

    fig_renewable_losses = px.scatter(
        df_latest,
        x="renewable",
        y="losses",
        hover_name="country_name",
        title="Renewable vs Losses"
    )

    df_latest["sustainability_score"] = (
        df_latest["renewable"] * 0.4 +
        df_latest["access"] * 0.4 -
        df_latest["losses"] * 0.2
    )

    top5_sustainable = df_latest.sort_values(
        "sustainability_score", ascending=False
    ).head(10)

    # ------------------------------------------
    # ANALYSIS 3: LOSSES
    # ------------------------------------------
    fig_losses_access = px.scatter(
        df_latest,
        x="losses",
        y="access",
        hover_name="country_name"
    )

    fig_losses_consumption = px.scatter(
        df_latest,
        x="losses",
        y="electricity",
        hover_name="country_name"
    )

    top_high_losses = df_latest.sort_values("losses", ascending=False).head(10)
    top_low_losses = df_latest.sort_values("losses", ascending=True).head(10)

    # ------------------------------------------
    # GDP ANALYSIS
    # ------------------------------------------
    df_gdp = df_latest.dropna(subset=["gdp_per_capita", "losses"]).copy()

    if df_gdp.empty:
        st.warning("⚠️ GDP data not available.")
        return None

    fig_gdp_losses = px.scatter(
        df_gdp,
        x="gdp_per_capita",
        y="losses",
        hover_name="country_name",
        trendline="ols",
        title="GDP vs Transmission Losses"
    )

    gdp_loss_corr = df_gdp["gdp_per_capita"].corr(df_gdp["losses"])
    avg_loss = df_gdp["losses"].mean()
    avg_gdp = df_gdp["gdp_per_capita"].mean()

    top_inefficient = df_gdp.sort_values("losses", ascending=False).head(10)
    top_efficient = df_gdp.sort_values("losses", ascending=True).head(10)

    # ------------------------------------------
    # ENERGY EQUITY
    # ------------------------------------------
    df_equity = df_latest.dropna(subset=["gdp_per_capita", "energy_equity_score"])

    fig_equity = px.scatter(
        df_equity,
        x="gdp_per_capita",
        y="energy_equity_score",
        hover_name="country_name",
        trendline="ols",
        title="GDP vs Energy Equity"
    )

    top_equity = df_equity.sort_values("energy_equity_score", ascending=False).head(10)
    low_equity = df_equity.sort_values("energy_equity_score", ascending=True).head(10)

    # ------------------------------------------
    # RETURN
    # ------------------------------------------
    return {
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