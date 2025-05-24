import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="SaaS Unit Economics Dashboard", layout="wide")

st.title("🚀 SaaS Unit Economics Dashboard")

# Load CSVs from project directory
unit_econ = pd.read_csv("unit_economics.csv")
unit_seg = pd.read_csv("unit_economics_by_segment.csv")

# Sidebar filters
st.sidebar.header("Filters")
industry_filter = st.sidebar.multiselect("Industry", unit_econ['industry'].dropna().unique())
plan_filter = st.sidebar.multiselect("Plan", unit_econ['plan_name'].dropna().unique())
company_size_filter = st.sidebar.multiselect("Company Size", unit_econ['company_size'].dropna().unique())
billing_filter = st.sidebar.multiselect("Billing Frequency", unit_econ['billing_frequency'].dropna().unique())

# Apply filters
filtered = unit_econ.copy()
if industry_filter:
    filtered = filtered[filtered['industry'].isin(industry_filter)]
if plan_filter:
    filtered = filtered[filtered['plan_name'].isin(plan_filter)]
if company_size_filter:
    filtered = filtered[filtered['company_size'].isin(company_size_filter)]
if billing_filter:
    filtered = filtered[filtered['billing_frequency'].isin(billing_filter)]

# KPIs
st.markdown("### 📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Avg CAC", f"${filtered['CAC'].mean():,.2f}")
col2.metric("Avg LTV", f"${filtered['LTV'].mean():,.2f}")
col3.metric("Avg LTV/CAC", f"{filtered['LTV_CAC_Ratio'].mean():.2f}")

col4, col5, col6 = st.columns(3)
col4.metric("Avg Payback (Months)", f"{filtered['CAC_Payback_Months'].mean():.2f}")
col5.metric("Avg Health Score", f"{filtered['Customer_Health_Score'].mean():.2f}")
col6.metric("Total Customers", len(filtered))

# Scatterplot LTV vs CAC
st.markdown("### 🔍 LTV vs CAC by Plan")
scatter = alt.Chart(filtered).mark_circle(size=60).encode(
    x='CAC', y='LTV', color='plan_name', tooltip=['customer_id', 'CAC', 'LTV']
).interactive()
st.altair_chart(scatter, use_container_width=True)

# Churn Status
st.markdown("### 🔄 Churn Breakdown")
churn_counts = filtered['Churned'].value_counts().rename({0: 'Active', 1: 'Churned'}).reset_index()
churn_chart = alt.Chart(churn_counts).mark_bar().encode(
    x='index:N',
    y='Churned:Q',
    tooltip=['index', 'Churned']
)
st.altair_chart(churn_chart, use_container_width=True)

# Segment Summary Table
st.markdown("### 📊 Segment-Level Summary")
st.dataframe(unit_seg)

# Download buttons
st.sidebar.download_button("Download Filtered Unit Economics", filtered.to_csv(index=False), file_name="filtered_unit_economics.csv")
st.sidebar.download_button("Download Segment Summary", unit_seg.to_csv(index=False), file_name="unit_economics_by_segment.csv")
