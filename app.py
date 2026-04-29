import streamlit as st
from analysis import run_analysis

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Energy Dashboard",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================
st.title("⚡ Global Energy Analysis Dashboard")

# ==========================================
# LOAD DATA (SAFE)
# ==========================================
with st.spinner("Loading data from S3..."):
    analysis_results = run_analysis()

# ------------------------------------------
# HANDLE NO DATA (CRITICAL)
# ------------------------------------------
if analysis_results is None:
    st.error("🚫 No data available right now")
    st.caption("The dataset is temporarily unavailable or invalid. Please try again later.")
    st.stop()

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

st.subheader("Top Sustainable Countries")
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
# GDP ANALYSIS
# ==========================================
st.header("📊 GDP vs Energy Efficiency")

col1, col2 = st.columns(2)

col1.metric(
    "Avg GDP per Capita",
    f"${analysis_results['avg_gdp']:.0f}"
)

col2.metric(
    "Avg Transmission Losses",
    f"{analysis_results['avg_loss']:.2f}%"
)

st.plotly_chart(
    analysis_results["gdp_losses_fig"],
    use_container_width=True
)

st.markdown(f"""
**Correlation between GDP and Losses:**  
`{analysis_results['gdp_loss_corr']:.2f}`

👉 Negative correlation means richer countries tend to have better infrastructure.
""")

st.subheader("🔻 Most Inefficient Countries")
st.dataframe(analysis_results["top_inefficient"], use_container_width=True)

st.subheader("🔺 Most Efficient Countries")
st.dataframe(analysis_results["top_efficient"], use_container_width=True)

# ==========================================
# ENERGY EQUITY
# ==========================================
st.markdown("---")
st.header("🌍 Energy Equity vs Economic Development")

st.plotly_chart(
    analysis_results["equity_fig"],
    use_container_width=True
)

# ==========================================
# KEY INSIGHT (A+ SECTION)
# ==========================================
st.markdown("### 📈 Key Insight")

st.markdown("""
- There is a **strong positive relationship** between GDP and energy equity  
- High-income countries achieve **near-universal access and high consumption**  
- Some countries **underperform despite high GDP**, indicating inefficiencies  

👉 Economic growth alone does not guarantee fair energy distribution
""")

# ==========================================
# TABLES
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Highest Energy Equity")
    st.dataframe(
        analysis_results["top_equity"],
        use_container_width=True
    )

with col2:
    st.subheader("⚠️ Lowest Energy Equity")
    st.dataframe(
        analysis_results["low_equity"],
        use_container_width=True
    )