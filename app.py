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
st.title("Global Energy Analysis Dashboard")

# ==========================================
# LOAD DATA
# ==========================================
with st.spinner("Loading data from S3..."):
    analysis_results = run_analysis()

if analysis_results is None:
    st.error("No data available right now")
    st.stop()

# ==========================================
# ANALYSIS 1: GDP vs ENERGY EFFICIENCY
# ==========================================
st.markdown("## Analysis 1: GDP vs Energy Efficiency")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Most Inefficient Countries")
    st.dataframe(
        analysis_results["top_inefficient"],
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("Most Efficient Countries")
    st.dataframe(
        analysis_results["top_efficient"],
        use_container_width=True,
        hide_index=True
    )

st.subheader("GDP vs Transmission Losses")
st.plotly_chart(
    analysis_results["gdp_losses_fig"],
    use_container_width=True
)

st.markdown(f"""
Correlation between GDP and Losses:  
`{analysis_results['gdp_loss_corr']:.2f}`
""")

st.markdown("---")

# ==========================================
# ANALYSIS 2: ENERGY GAP
# ==========================================
st.markdown("## Analysis 2: Energy Gap (Production vs Consumption per Capita)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Surplus Countries")
    st.dataframe(
        analysis_results["top_surplus"],
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("Top Deficit Countries")
    st.dataframe(
        analysis_results["top_deficit"],
        use_container_width=True,
        hide_index=True
    )

st.subheader("Production vs Consumption")
st.plotly_chart(
    analysis_results["energy_gap_fig"],
    use_container_width=True
)

st.markdown("---")

# ==========================================
# ANALYSIS 3: RENEWABLE IMPACT
# ==========================================
st.markdown("## Analysis 3: Impact of Renewable Energy")

st.subheader("Top Sustainable Countries")
st.dataframe(
    analysis_results["top_sustainable"],
    use_container_width=True,
    hide_index=True
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Renewable Energy vs Electricity Access")
    st.plotly_chart(
        analysis_results["renewable_access_fig"],
        use_container_width=True
    )

with col2:
    st.subheader("Renewable Energy vs Transmission Losses")
    st.plotly_chart(
        analysis_results["renewable_losses_fig"],
        use_container_width=True
    )

st.markdown("---")

# ==========================================
# ANALYSIS 4: LOSSES IMPACT
# ==========================================
st.markdown("## Analysis 4: Transmission Losses Impact")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Highest Loss Countries")
    st.dataframe(
        analysis_results["top_high_losses"],
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("Lowest Loss Countries")
    st.dataframe(
        analysis_results["top_low_losses"],
        use_container_width=True,
        hide_index=True
    )

col3, col4 = st.columns(2)

with col3:
    st.subheader("Transmission Losses vs Electricity Access")
    st.plotly_chart(
        analysis_results["loss_access_fig"],
        use_container_width=True
    )

with col4:
    st.subheader("Transmission Losses vs Electricity Consumption")
    st.plotly_chart(
        analysis_results["loss_consumption_fig"],
        use_container_width=True
    )

st.markdown("---")

# ==========================================
# ANALYSIS 5: ENERGY EQUITY
# ==========================================
st.markdown("## Analysis 5: Energy Equity vs Economic Development")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Highest Energy Equity")
    st.dataframe(
        analysis_results["top_equity"],
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("Lowest Energy Equity")
    st.dataframe(
        analysis_results["low_equity"],
        use_container_width=True,
        hide_index=True
    )

st.subheader("GDP vs Energy Equity Score")
st.plotly_chart(
    analysis_results["equity_fig"],
    use_container_width=True
)