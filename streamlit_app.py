import streamlit as st
import pandas as pd
import plotly.express as px

# Load the datasets
try:
    df_unit_economics = pd.read_csv('unit_economics.csv')
    df_unit_economics_by_segment = pd.read_csv('unit_economics_by_segment.csv')
except FileNotFoundError:
    st.error("Make sure 'unit_economics.csv' and 'unit_economics_by_segment.csv' are in the same directory.")
    st.stop()

# Data Preprocessing (if needed)
# Convert 'latest_end' to datetime if time-series analysis is required
df_unit_economics['latest_end'] = pd.to_datetime(df_unit_economics['latest_end'])

# Fill missing values for health and sentiment scores for visualization purposes
df_unit_economics['Avg_Sentiment_Score'] = df_unit_economics['Avg_Sentiment_Score'].fillna(df_unit_economics['Avg_Sentiment_Score'].mean())
df_unit_economics['Customer_Health_Score'] = df_unit_economics['Customer_Health_Score'].fillna(df_unit_economics['Customer_Health_Score'].mean())
df_unit_economics['Active_Days'] = df_unit_economics['Active_Days'].fillna(0) # or median/mean
df_unit_economics['Usage_Events'] = df_unit_economics['Usage_Events'].fillna(0) # or median/mean
df_unit_economics['Usage_Score'] = df_unit_economics['Usage_Score'].fillna(0) # or median/mean


# --- Streamlit Dashboard Layout ---
st.set_page_config(layout="wide", page_title="SaaS Unit Economics Dashboard")

st.title("🚀 SaaS Unit Economics Dashboard")

st.markdown("""
This dashboard provides insights into the unit economics of your SaaS business,
allowing you to analyze key metrics at both the individual customer and aggregated segment levels.
""")

# --- Sidebar for Filters ---
st.sidebar.header("Filter Options")

# Global filters for the aggregated data (and potentially individual data)
selected_industries = st.sidebar.multiselect(
    "Select Industry:",
    options=df_unit_economics_by_segment['industry'].unique(),
    default=df_unit_economics_by_segment['industry'].unique()
)

selected_company_sizes = st.sidebar.multiselect(
    "Select Company Size:",
    options=df_unit_economics_by_segment['company_size'].unique(),
    default=df_unit_economics_by_segment['company_size'].unique()
)

selected_plan_names = st.sidebar.multiselect(
    "Select Plan Name:",
    options=df_unit_economics_by_segment['plan_name'].unique(),
    default=df_unit_economics_by_segment['plan_name'].unique()
)

selected_billing_frequencies = st.sidebar.multiselect(
    "Select Billing Frequency:",
    options=df_unit_economics_by_segment['billing_frequency'].unique(),
    default=df_unit_economics_by_segment['billing_frequency'].unique()
)

# Apply filters to both dataframes
filtered_df_unit_economics = df_unit_economics[
    (df_unit_economics['industry'].isin(selected_industries)) &
    (df_unit_economics['company_size'].isin(selected_company_sizes)) &
    (df_unit_economics['plan_name'].isin(selected_plan_names)) &
    (df_unit_economics['billing_frequency'].isin(selected_billing_frequencies))
]

filtered_df_unit_economics_by_segment = df_unit_economics_by_segment[
    (df_unit_economics_by_segment['industry'].isin(selected_industries)) &
    (df_unit_economics_by_segment['company_size'].isin(selected_company_sizes)) &
    (df_unit_economics_by_segment['plan_name'].isin(selected_plan_names)) &
    (df_unit_economics_by_segment['billing_frequency'].isin(selected_billing_frequencies))
]

# --- Main Dashboard Content ---

st.header("Key Performance Indicators (KPIs)")
if not filtered_df_unit_economics.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Average LTV/CAC Ratio", value=f"{filtered_df_unit_economics['LTV_CAC_Ratio'].mean():.2f}")
    with col2:
        st.metric(label="Average CAC Payback Months", value=f"{filtered_df_unit_economics['CAC_Payback_Months'].mean():.2f}")
    with col3:
        churn_rate = filtered_df_unit_economics['Churned'].mean() * 100
        st.metric(label="Churn Rate", value=f"{churn_rate:.2f}%")
    with col4:
        st.metric(label="Average Customer Health Score", value=f"{filtered_df_unit_economics['Customer_Health_Score'].mean():.2f}")
else:
    st.warning("No data available for the selected filters in customer-level data.")


st.header("Customer-Level Unit Economics Distributions")

if not filtered_df_unit_economics.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        fig_ltv_cac = px.histogram(filtered_df_unit_economics, x='LTV_CAC_Ratio',
                                   title='Distribution of LTV to CAC Ratio',
                                   nbins=50, color_discrete_sequence=px.colors.qualitative.Plotly)
        st.plotly_chart(fig_ltv_cac, use_container_width=True)

    with col2:
        fig_payback = px.histogram(filtered_df_unit_economics, x='CAC_Payback_Months',
                                    title='Distribution of CAC Payback Months',
                                    nbins=50, color_discrete_sequence=px.colors.qualitative.Plotly)
        st.plotly_chart(fig_payback, use_container_width=True)

    with col3:
        fig_health = px.histogram(filtered_df_unit_economics, x='Customer_Health_Score',
                                   title='Distribution of Customer Health Score',
                                   nbins=20, color_discrete_sequence=px.colors.qualitative.Plotly)
        st.plotly_chart(fig_health, use_container_width=True)
else:
    st.warning("No data available for the selected filters to display customer-level distributions.")

st.header("Segment-Level Unit Economics Analysis")

if not filtered_df_unit_economics_by_segment.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig_avg_ltv_cac_industry = px.bar(
            filtered_df_unit_economics_by_segment.groupby('industry')['Avg_LTV_CAC'].mean().reset_index().sort_values(by='Avg_LTV_CAC', ascending=False),
            x='Avg_LTV_CAC',
            y='industry',
            orientation='h',
            title='Average LTV/CAC Ratio by Industry',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_avg_ltv_cac_industry, use_container_width=True)

    with col2:
        fig_avg_payback_industry = px.bar(
            filtered_df_unit_economics_by_segment.groupby('industry')['Avg_Payback_Months'].mean().reset_index().sort_values(by='Avg_Payback_Months', ascending=True),
            x='Avg_Payback_Months',
            y='industry',
            orientation='h',
            title='Average Payback Months by Industry',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_avg_payback_industry, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig_cust_count_company_size = px.bar(
            filtered_df_unit_economics_by_segment.groupby('company_size')['Customer_Count'].sum().reset_index().sort_values(by='Customer_Count', ascending=False),
            x='company_size',
            y='Customer_Count',
            title='Total Customer Count by Company Size',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_cust_count_company_size, use_container_width=True)

    with col4:
        fig_avg_ltv_cac_plan = px.bar(
            filtered_df_unit_economics_by_segment.groupby('plan_name')['Avg_LTV_CAC'].mean().reset_index().sort_values(by='Avg_LTV_CAC', ascending=False),
            x='Avg_LTV_CAC',
            y='plan_name',
            orientation='h',
            title='Average LTV/CAC Ratio by Plan Name',
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig_avg_ltv_cac_plan, use_container_width=True)
else:
    st.warning("No data available for the selected filters to display segment-level analysis.")

st.header("Customer Stream List (Filtered Data)")

# Option to filter for 'Churned' customers
show_churned = st.checkbox("Show only Churned Customers", value=False)
if show_churned:
    filtered_df_unit_economics_display = filtered_df_unit_economics[filtered_df_unit_economics['Churned'] == 1]
else:
    filtered_df_unit_economics_display = filtered_df_unit_economics

# Allow sorting
sort_column = st.selectbox(
    "Sort Customer List by:",
    options=['customer_id', 'LTV_CAC_Ratio', 'CAC_Payback_Months', 'Customer_Health_Score', 'Monthly_Revenue', 'latest_end'],
    index=0
)
sort_order = st.radio(
    "Sort Order:",
    ('Ascending', 'Descending'),
    horizontal=True
)

ascending = True if sort_order == 'Ascending' else False
filtered_df_unit_economics_display = filtered_df_unit_economics_display.sort_values(by=sort_column, ascending=ascending)

# Display the filtered customer data
if not filtered_df_unit_economics_display.empty:
    st.dataframe(filtered_df_unit_economics_display[['customer_id', 'industry', 'company_size', 'plan_name',
                                                      'LTV', 'CAC', 'LTV_CAC_Ratio', 'CAC_Payback_Months',
                                                      'Monthly_Revenue', 'Customer_Health_Score', 'Churned', 'latest_end',
                                                      'Avg_Sentiment_Score', 'Active_Days', 'Usage_Events', 'Usage_Score']])
else:
    st.info("No customers match the current filter and churn selection.")

st.markdown("---")
st.markdown("Dashboard created using Streamlit and Plotly.")
