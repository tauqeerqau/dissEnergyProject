import streamlit as st
from analysis import analysis_results

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Energy Dashboard", layout="wide")

# ==========================================
# TITLE
# ==========================================
st.title("⚡ Global Energy Analysis Dashboard")

# ==========================================
# ANALYSIS 1
# ==========================================
st.markdown("## **Analysis 1: Energy Gap (Production vs Consumption per Capita)**")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Surplus Countries")
    st.dataframe(
        analysis_results["top_surplus"],
        use_container_width=True
    )

with col2:
    st.subheader("Top 10 Deficit Countries")
    st.dataframe(
        analysis_results["top_deficit"],
        use_container_width=True
    )

st.plotly_chart(
    analysis_results["energy_gap_fig"],
    use_container_width=True
)

st.markdown("---")

# ==========================================
# ANALYSIS 2
# ==========================================
st.markdown("## **Analysis 2: Impact of Renewable Energy on Access & Efficiency**")

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        analysis_results["renewable_access_fig"],
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        analysis_results["renewable_losses_fig"],
        use_container_width=True
    )

st.subheader("Top 5 Sustainable Countries")
st.dataframe(
    analysis_results["top_sustainable"],
    use_container_width=True
)

st.markdown("---")

# ==========================================
# ANALYSIS 3
# ==========================================
st.markdown("## **Analysis 3: Infrastructure Efficiency (Transmission Losses Impact)**")

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        analysis_results["loss_access_fig"],
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        analysis_results["loss_consumption_fig"],
        use_container_width=True
    )

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 10 Highest Loss Countries")
    st.dataframe(
        analysis_results["top_high_losses"],
        use_container_width=True
    )

with col4:
    st.subheader("Top 10 Lowest Loss Countries")
    st.dataframe(
        analysis_results["top_low_losses"],
        use_container_width=True
    )
    
# ==========================================
# 📊 ANALYSIS 4: GDP vs ENERGY EFFICIENCY
# ==========================================

st.header("📊 Economic Efficiency Analysis (GDP vs Losses)")

st.markdown("""
This analysis explores how a country's economic strength (GDP per capita) 
relates to electricity transmission efficiency. Lower losses indicate better infrastructure.
""")

# --- Scatter Plot ---
st.plotly_chart(
    analysis_results["gdp_losses_fig"],
    use_container_width=True
)

# --- Correlation Metric ---
corr = analysis_results["gdp_loss_corr"]

st.metric(
    label="GDP vs Losses Correlation",
    value=f"{corr:.2f}"
)

# --- Interpretation ---
if corr < 0:
    st.success("Higher GDP is associated with LOWER transmission losses (better efficiency)")
elif corr > 0:
    st.warning("Higher GDP is associated with HIGHER losses (unexpected trend)")
else:
    st.info("No strong relationship between GDP and losses")

# --- Layout: Side-by-side tables ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔴 Least Efficient Countries (High Losses)")
    st.dataframe(analysis_results["top_inefficient"])

with col2:
    st.subheader("🟢 Most Efficient Countries (Low Losses)")
    st.dataframe(analysis_results["top_efficient"])