# ==========================================
# analysis.py (FINAL COMPLETE VERSION)
# ==========================================

import pandas as pd
import boto3
import plotly.express as px
import streamlit as st
from io import StringIO

# ==========================================
# AWS CONFIG
# ==========================================
AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]
REGION = st.secrets["AWS_REGION"]

BUCKET_NAME = "energy-data-backup"
FILE_KEY = "final/final_dataset.csv"

# ==========================================
# LOAD DATA
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
        return pd.read_csv(StringIO(data))
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# ==========================================
# RANK FIX
# ==========================================
def add_rank(df):
    df = df.reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df

# ==========================================
# MAIN ANALYSIS
# ==========================================
def run_analysis():

    df = load_data_from_s3()
    if df is None or df.empty:
        return None

    # ==========================================
    # RENAME
    # ==========================================
    df = df.rename(columns={
        "country_name": "Country Name",
        "production_per_capita": "Production Per Capita",
        "electricity": "Electricity Consumption Per Capita",
        "renewable": "Renewable Energy %",
        "losses": "Transmission Losses %",
        "access": "Electricity Access %",
        "gdp_per_capita": "GDP Per Capita",
        "year": "Year"
    })

    # ==========================================
    # CLEAN
    # ==========================================
    num_cols = [
        "Production Per Capita",
        "Electricity Consumption Per Capita",
        "Renewable Energy %",
        "Transmission Losses %",
        "Electricity Access %",
        "GDP Per Capita"
    ]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year","Production Per Capita","Electricity Consumption Per Capita"])
    df["Year"] = df["Year"].astype(int)

    df_latest = df[df["Year"] == df["Year"].max()].copy()

    # ==========================================
    # CATEGORY COLORS
    # ==========================================
    category_colors = {"Low":"red","Medium":"orange","High":"green"}

    df_latest["Renewable Cat"] = pd.cut(df_latest["Renewable Energy %"], [0,30,70,100], labels=["Low","Medium","High"])
    df_latest["Losses Cat"] = pd.cut(df_latest["Transmission Losses %"], [0,10,25,100], labels=["Low","Medium","High"])
    df_latest["Access Cat"] = pd.cut(df_latest["Electricity Access %"], [0,50,90,100], labels=["Low","Medium","High"])

    # ==========================================
    # GDP ANALYSIS (Analysis 1)
    # ==========================================
    df_gdp = df_latest.dropna(subset=["GDP Per Capita","Transmission Losses %"])

    fig_gdp_losses = px.scatter(
        df_gdp,
        x="GDP Per Capita",
        y="Transmission Losses %",
        color="Losses Cat",
        color_discrete_map=category_colors,
        hover_name="Country Name"
    )

    avg_gdp = df_gdp["GDP Per Capita"].mean()
    avg_loss = df_gdp["Transmission Losses %"].mean()
    gdp_loss_corr = df_gdp["GDP Per Capita"].corr(df_gdp["Transmission Losses %"])

    top_inefficient = add_rank(df_gdp.sort_values("Transmission Losses %", ascending=False)[
        ["Country Name","GDP Per Capita","Transmission Losses %"]
    ].head(10))

    top_efficient = add_rank(df_gdp.sort_values("Transmission Losses %")[
        ["Country Name","GDP Per Capita","Transmission Losses %"]
    ].head(10))

    # ==========================================
    # ENERGY GAP (Analysis 2)
    # ==========================================
    df_latest["Energy Gap"] = df_latest["Production Per Capita"] - df_latest["Electricity Consumption Per Capita"]
    df_latest["Status"] = df_latest["Energy Gap"].apply(lambda x: "Surplus" if x > 0 else "Deficit")

    fig_energy_gap = px.scatter(
        df_latest,
        x="Production Per Capita",
        y="Electricity Consumption Per Capita",
        color="Status",
        color_discrete_map={"Surplus":"green","Deficit":"red"},
        hover_name="Country Name"
    )

    top_surplus = add_rank(df_latest.sort_values("Energy Gap", ascending=False)[
        ["Country Name","Production Per Capita","Electricity Consumption Per Capita","Energy Gap"]
    ].head(10))

    top_deficit = add_rank(df_latest.sort_values("Energy Gap")[
        ["Country Name","Production Per Capita","Electricity Consumption Per Capita","Energy Gap"]
    ].head(10))

    # ==========================================
    # RENEWABLE (Analysis 3)
    # ==========================================
    fig_renewable_access = px.scatter(
        df_latest, x="Renewable Energy %", y="Electricity Access %",
        color="Renewable Cat", color_discrete_map=category_colors
    )

    fig_renewable_losses = px.scatter(
        df_latest, x="Renewable Energy %", y="Transmission Losses %",
        color="Renewable Cat", color_discrete_map=category_colors
    )

    df_latest["Sustainability Score"] = (
        df_latest["Renewable Energy %"]*0.4 +
        df_latest["Electricity Access %"]*0.4 -
        df_latest["Transmission Losses %"]*0.2
    )

    top_sustainable = add_rank(df_latest.sort_values("Sustainability Score", ascending=False)[
        ["Country Name","Renewable Energy %","Electricity Access %","Transmission Losses %","Sustainability Score"]
    ].head(10))

    # ==========================================
    # LOSSES (Analysis 4)
    # ==========================================
    fig_losses_access = px.scatter(df_latest, x="Transmission Losses %", y="Electricity Access %",
                                  color="Losses Cat", color_discrete_map=category_colors)

    fig_losses_consumption = px.scatter(df_latest, x="Transmission Losses %", y="Electricity Consumption Per Capita",
                                       color="Losses Cat", color_discrete_map=category_colors)

    top_high_losses = add_rank(df_latest.sort_values("Transmission Losses %", ascending=False)[
        ["Country Name","Transmission Losses %","Electricity Consumption Per Capita"]
    ].head(10))

    top_low_losses = add_rank(df_latest.sort_values("Transmission Losses %")[
        ["Country Name","Transmission Losses %","Electricity Consumption Per Capita"]
    ].head(10))

    # ==========================================
    # EQUITY (Analysis 5)
    # ==========================================
    df_latest["Electricity Norm"] = (df_latest["Electricity Consumption Per Capita"] / df_latest["Electricity Consumption Per Capita"].max())*100
    df_latest["Energy Equity Score"] = df_latest["Electricity Access %"]*0.6 + df_latest["Electricity Norm"]*0.4

    df_eq = df_latest.dropna(subset=["GDP Per Capita","Energy Equity Score"])

    fig_equity = px.scatter(df_eq, x="GDP Per Capita", y="Energy Equity Score",
                            color="Access Cat", color_discrete_map=category_colors)

    top_equity = add_rank(df_eq.sort_values("Energy Equity Score", ascending=False)[
        ["Country Name","GDP Per Capita","Energy Equity Score"]
    ].head(10))

    low_equity = add_rank(df_eq.sort_values("Energy Equity Score")[
        ["Country Name","GDP Per Capita","Energy Equity Score"]
    ].head(10))

    # ==========================================
    # RETURN
    # ==========================================
    return {
        "avg_gdp": avg_gdp,
        "avg_loss": avg_loss,
        "gdp_loss_corr": gdp_loss_corr,
        "gdp_losses_fig": fig_gdp_losses,
        "top_inefficient": top_inefficient,
        "top_efficient": top_efficient,

        "energy_gap_fig": fig_energy_gap,
        "top_surplus": top_surplus,
        "top_deficit": top_deficit,

        "renewable_access_fig": fig_renewable_access,
        "renewable_losses_fig": fig_renewable_losses,
        "top_sustainable": top_sustainable,

        "loss_access_fig": fig_losses_access,
        "loss_consumption_fig": fig_losses_consumption,
        "top_high_losses": top_high_losses,
        "top_low_losses": top_low_losses,

        "equity_fig": fig_equity,
        "top_equity": top_equity,
        "low_equity": low_equity
    }