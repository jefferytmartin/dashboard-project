import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the datasets
try:
    df_unit_economics = pd.read_csv('unit_economics.csv')
    df_unit_economics_by_segment = pd.read_csv('unit_economics_by_segment.csv')
except FileNotFoundError:
    print("Error: Make sure 'unit_economics.csv' and 'unit_economics_by_segment.csv' are in the same directory.")
    # Exit or handle error appropriately in a real application
    # For this example, we'll assume the files are present for the dashboard to run.
    exit()

# Data Preprocessing
df_unit_economics['latest_end'] = pd.to_datetime(df_unit_economics['latest_end'])

# Fill missing values for health and sentiment scores for visualization purposes
df_unit_economics['Avg_Sentiment_Score'] = df_unit_economics['Avg_Sentiment_Score'].fillna(df_unit_economics['Avg_Sentiment_Score'].mean())
df_unit_economics['Customer_Health_Score'] = df_unit_economics['Customer_Health_Score'].fillna(df_unit_economics['Customer_Health_Score'].mean())
df_unit_economics['Active_Days'] = df_unit_economics['Active_Days'].fillna(0)
df_unit_economics['Usage_Events'] = df_unit_economics['Usage_Events'].fillna(0)
df_unit_economics['Usage_Score'] = df_unit_economics['Usage_Score'].fillna(0)

# Initialize the Dash app
app = dash.Dash(__name__)

# --- Dashboard Layout ---
app.layout = html.Div(style={'font-family': 'Arial, sans-serif'}, children=[
    html.H1("🚀 SaaS Unit Economics Dashboard", style={'textAlign': 'center', 'color': '#2C3E50'}),

    html.Div([
        html.P("This dashboard provides insights into the unit economics of your SaaS business, allowing you to analyze key metrics at both the individual customer and aggregated segment levels.", style={'textAlign': 'center', 'color': '#7F8C8D'}),
    ]),

    # --- Filters Section ---
    html.Div(style={'backgroundColor': '#ECF0F1', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px'}, children=[
        html.H3("Filter Options", style={'textAlign': 'center', 'color': '#34495E'}),
        html.Div([
            html.Div(style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}, children=[
                html.Label("Select Industry:"),
                dcc.Dropdown(
                    id='industry-filter',
                    options=[{'label': i, 'value': i} for i in df_unit_economics_by_segment['industry'].unique()],
                    value=df_unit_economics_by_segment['industry'].unique().tolist(), # Default to all selected
                    multi=True
                )
            ]),
            html.Div(style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}, children=[
                html.Label("Select Company Size:"),
                dcc.Dropdown(
                    id='company-size-filter',
                    options=[{'label': i, 'value': i} for i in df_unit_economics_by_segment['company_size'].unique()],
                    value=df_unit_economics_by_segment['company_size'].unique().tolist(),
                    multi=True
                )
            ]),
            html.Div(style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}, children=[
                html.Label("Select Plan Name:"),
                dcc.Dropdown(
                    id='plan-name-filter',
                    options=[{'label': i, 'value': i} for i in df_unit_economics_by_segment['plan_name'].unique()],
                    value=df_unit_economics_by_segment['plan_name'].unique().tolist(),
                    multi=True
                )
            ]),
            html.Div(style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}, children=[
                html.Label("Select Billing Frequency:"),
                dcc.Dropdown(
                    id='billing-frequency-filter',
                    options=[{'label': i, 'value': i} for i in df_unit_economics_by_segment['billing_frequency'].unique()],
                    value=df_unit_economics_by_segment['billing_frequency'].unique().tolist(),
                    multi=True
                )
            ]),
        ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-around'}),
    ]),

    # --- KPIs Section ---
    html.Div(style={'backgroundColor': '#FBFCFC', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px', 'border': '1px solid #D7DBDD'}, children=[
        html.H2("Key Performance Indicators (KPIs)", style={'textAlign': 'center', 'color': '#2C3E50'}),
        html.Div(id='kpi-output', style={'display': 'flex', 'justify-content': 'space-around', 'padding': '10px'}),
    ]),

    # --- Customer-Level Distributions ---
    html.Div(style={'backgroundColor': '#FBFCFC', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px', 'border': '1px solid #D7DBDD'}, children=[
        html.H2("Customer-Level Unit Economics Distributions", style={'textAlign': 'center', 'color': '#2C3E50'}),
        html.Div([
            dcc.Graph(id='ltv-cac-ratio-dist', style={'width': '33%', 'display': 'inline-block'}),
            dcc.Graph(id='cac-payback-dist', style={'width': '33%', 'display': 'inline-block'}),
            dcc.Graph(id='customer-health-dist', style={'width': '33%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justify-content': 'space-around'}),
    ]),

    # --- Segment-Level Analysis ---
    html.Div(style={'backgroundColor': '#FBFCFC', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px', 'border': '1px solid #D7DBDD'}, children=[
        html.H2("Segment-Level Unit Economics Analysis", style={'textAlign': 'center', 'color': '#2C3E50'}),
        html.Div([
            dcc.Graph(id='avg-ltv-cac-industry', style={'width': '49%', 'display': 'inline-block'}),
            dcc.Graph(id='avg-payback-industry', style={'width': '49%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justify-content': 'space-around'}),
        html.Div([
            dcc.Graph(id='cust-count-company-size', style={'width': '49%', 'display': 'inline-block'}),
            dcc.Graph(id='avg-ltv-cac-plan', style={'width': '49%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justify-content': 'space-around'}),
    ]),

    # --- Customer Stream List ---
    html.Div(style={'backgroundColor': '#FBFCFC', 'padding': '20px', 'borderRadius': '8px', 'border': '1px solid #D7DBDD'}, children=[
        html.H2("Customer Stream List (Filtered Data)", style={'textAlign': 'center', 'color': '#2C3E50'}),
        html.Div([
            dcc.Checklist(
                id='show-churned-customers',
                options=[{'label': ' Show only Churned Customers', 'value': 'churned'}],
                value=[],
                style={'marginBottom': '10px'}
            ),
            html.Div(style={'width': '30%', 'display': 'inline-block', 'paddingRight': '20px'}, children=[
                html.Label("Sort Customer List by:"),
                dcc.Dropdown(
                    id='sort-column',
                    options=[
                        {'label': 'Customer ID', 'value': 'customer_id'},
                        {'label': 'LTV/CAC Ratio', 'value': 'LTV_CAC_Ratio'},
                        {'label': 'CAC Payback Months', 'value': 'CAC_Payback_Months'},
                        {'label': 'Customer Health Score', 'value': 'Customer_Health_Score'},
                        {'label': 'Monthly Revenue', 'value': 'Monthly_Revenue'},
                        {'label': 'Latest End Date', 'value': 'latest_end'}
                    ],
                    value='customer_id'
                )
            ]),
            html.Div(style={'width': '30%', 'display': 'inline-block'}, children=[
                html.Label("Sort Order:"),
                dcc.RadioItems(
                    id='sort-order',
                    options=[
                        {'label': ' Ascending', 'value': 'asc'},
                        {'label': ' Descending', 'value': 'desc'}
                    ],
                    value='asc',
                    inline=True
                )
            ])
        ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'marginBottom': '20px'}),
        html.Div(id='customer-list-table')
    ]),

    html.Div(html.P("Dashboard created using Plotly Dash.", style={'textAlign': 'center', 'marginTop': '30px', 'color': '#7F8C8D'}))
])

# --- Callbacks ---
@app.callback(
    [Output('kpi-output', 'children'),
     Output('ltv-cac-ratio-dist', 'figure'),
     Output('cac-payback-dist', 'figure'),
     Output('customer-health-dist', 'figure'),
     Output('avg-ltv-cac-industry', 'figure'),
     Output('avg-payback-industry', 'figure'),
     Output('cust-count-company-size', 'figure'),
     Output('avg-ltv-cac-plan', 'figure'),
     Output('customer-list-table', 'children')],
    [Input('industry-filter', 'value'),
     Input('company-size-filter', 'value'),
     Input('plan-name-filter', 'value'),
     Input('billing-frequency-filter', 'value'),
     Input('show-churned-customers', 'value'),
     Input('sort-column', 'value'),
     Input('sort-order', 'value')]
)
def update_dashboard(selected_industries, selected_company_sizes, selected_plan_names,
                     selected_billing_frequencies, show_churned_customers, sort_column, sort_order):

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

    # --- KPI Updates ---
    if not filtered_df_unit_economics.empty:
        avg_ltv_cac = f"{filtered_df_unit_economics['LTV_CAC_Ratio'].mean():.2f}"
        avg_cac_payback = f"{filtered_df_unit_economics['CAC_Payback_Months'].mean():.2f}"
        churn_rate = f"{filtered_df_unit_economics['Churned'].mean() * 100:.2f}%"
        avg_health_score = f"{filtered_df_unit_economics['Customer_Health_Score'].mean():.2f}"
    else:
        avg_ltv_cac = "N/A"
        avg_cac_payback = "N/A"
        churn_rate = "N/A"
        avg_health_score = "N/A"

    kpi_cards = [
        html.Div(style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '15px', 'borderRadius': '8px', 'width': '22%', 'textAlign': 'center', 'boxShadow': '2px 2px 5px rgba(0,0,0,0.2)'}, children=[
            html.H4("Avg. LTV/CAC Ratio"),
            html.P(avg_ltv_cac, style={'fontSize': '2em', 'fontWeight': 'bold'})
        ]),
        html.Div(style={'backgroundColor': '#2ECC71', 'color': 'white', 'padding': '15px', 'borderRadius': '8px', 'width': '22%', 'textAlign': 'center', 'boxShadow': '2px 2px 5px rgba(0,0,0,0.2)'}, children=[
            html.H4("Avg. CAC Payback (Months)"),
            html.P(avg_cac_payback, style={'fontSize': '2em', 'fontWeight': 'bold'})
        ]),
        html.Div(style={'backgroundColor': '#E74C3C', 'color': 'white', 'padding': '15px', 'borderRadius': '8px', 'width': '22%', 'textAlign': 'center', 'boxShadow': '2px 2px 5px rgba(0,0,0,0.2)'}, children=[
            html.H4("Churn Rate"),
            html.P(churn_rate, style={'fontSize': '2em', 'fontWeight': 'bold'})
        ]),
        html.Div(style={'backgroundColor': '#F39C12', 'color': 'white', 'padding': '15px', 'borderRadius': '8px', 'width': '22%', 'textAlign': 'center', 'boxShadow': '2px 2px 5px rgba(0,0,0,0.2)'}, children=[
            html.H4("Avg. Customer Health Score"),
            html.P(avg_health_score, style={'fontSize': '2em', 'fontWeight': 'bold'})
        ])
    ]

    # --- Customer-Level Distributions Plots ---
    if not filtered_df_unit_economics.empty:
        fig_ltv_cac = px.histogram(filtered_df_unit_economics, x='LTV_CAC_Ratio',
                                   title='Distribution of LTV to CAC Ratio', nbins=50,
                                   color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_payback = px.histogram(filtered_df_unit_economics, x='CAC_Payback_Months',
                                    title='Distribution of CAC Payback Months', nbins=50,
                                    color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_health = px.histogram(filtered_df_unit_economics, x='Customer_Health_Score',
                                   title='Distribution of Customer Health Score', nbins=20,
                                   color_discrete_sequence=px.colors.qualitative.Plotly)
    else:
        fig_ltv_cac = px.scatter(title="No data for LTV/CAC Ratio Distribution")
        fig_payback = px.scatter(title="No data for CAC Payback Months Distribution")
        fig_health = px.scatter(title="No data for Customer Health Score Distribution")

    # --- Segment-Level Analysis Plots ---
    if not filtered_df_unit_economics_by_segment.empty:
        avg_ltv_cac_by_industry = filtered_df_unit_economics_by_segment.groupby('industry')['Avg_LTV_CAC'].mean().reset_index().sort_values(by='Avg_LTV_CAC', ascending=False)
        fig_avg_ltv_cac_industry = px.bar(avg_ltv_cac_by_industry, x='Avg_LTV_CAC', y='industry', orientation='h',
                                          title='Average LTV/CAC Ratio by Industry', color_discrete_sequence=px.colors.qualitative.Set2)

        avg_payback_by_industry = filtered_df_unit_economics_by_segment.groupby('industry')['Avg_Payback_Months'].mean().reset_index().sort_values(by='Avg_Payback_Months', ascending=True)
        fig_avg_payback_industry = px.bar(avg_payback_by_industry, x='Avg_Payback_Months', y='industry', orientation='h',
                                          title='Average Payback Months by Industry', color_discrete_sequence=px.colors.qualitative.Set2)

        customer_count_by_company_size = filtered_df_unit_economics_by_segment.groupby('company_size')['Customer_Count'].sum().reset_index().sort_values(by='Customer_Count', ascending=False)
        fig_cust_count_company_size = px.bar(customer_count_by_company_size, x='company_size', y='Customer_Count',
                                             title='Total Customer Count by Company Size', color_discrete_sequence=px.colors.qualitative.Set3)

        avg_ltv_cac_by_plan = filtered_df_unit_economics_by_segment.groupby('plan_name')['Avg_LTV_CAC'].mean().reset_index().sort_values(by='Avg_LTV_CAC', ascending=False)
        fig_avg_ltv_cac_plan = px.bar(avg_ltv_cac_by_plan, x='Avg_LTV_CAC', y='plan_name', orientation='h',
                                      title='Average LTV/CAC Ratio by Plan Name', color_discrete_sequence=px.colors.qualitative.Set1)
    else:
        fig_avg_ltv_cac_industry = px.scatter(title="No data for Avg LTV/CAC by Industry")
        fig_avg_payback_industry = px.scatter(title="No data for Avg Payback by Industry")
        fig_cust_count_company_size = px.scatter(title="No data for Customer Count by Company Size")
        fig_avg_ltv_cac_plan = px.scatter(title="No data for Avg LTV/CAC by Plan Name")


    # --- Customer Stream List Table ---
    filtered_df_customers_display = filtered_df_unit_economics.copy()
    if 'churned' in show_churned_customers:
        filtered_df_customers_display = filtered_df_customers_display[filtered_df_customers_display['Churned'] == 1]

    # Sort the dataframe
    if sort_column and not filtered_df_customers_display.empty:
        ascending = True if sort_order == 'asc' else False
        filtered_df_customers_display = filtered_df_customers_display.sort_values(by=sort_column, ascending=ascending)

    customer_table_data = []
    if not filtered_df_customers_display.empty:
        # Select relevant columns for the table display
        display_columns = ['customer_id', 'industry', 'company_size', 'plan_name',
                           'LTV', 'CAC', 'LTV_CAC_Ratio', 'CAC_Payback_Months',
                           'Monthly_Revenue', 'Customer_Health_Score', 'Churned', 'latest_end',
                           'Avg_Sentiment_Score', 'Active_Days', 'Usage_Events', 'Usage_Score']
        
        # Ensure only columns present in the dataframe are selected
        display_columns = [col for col in display_columns if col in filtered_df_customers_display.columns]

        customer_table_data = filtered_df_customers_display[display_columns].to_dict('records')
        
        # Convert datetime objects in `latest_end` to string for display, if it's there
        if 'latest_end' in display_columns:
            for row in customer_table_data:
                if isinstance(row['latest_end'], pd.Timestamp):
                    row['latest_end'] = row['latest_end'].strftime('%Y-%m-%d')


    customer_list_table = html.Div([
        dash.dash_table.DataTable(
            id='table-container',
            columns=[{"name": i.replace('_', ' ').title(), "id": i} for i in display_columns],
            data=customer_table_data,
            page_size=15, # Number of rows per page
            style_table={'overflowX': 'auto'},
            style_cell={'minWidth': '100px', 'width': '120px', 'maxWidth': '180px', 'textAlign': 'left', 'padding': '8px'},
            style_header={
                'backgroundColor': '#2C3E50',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            export_format='csv',
            sort_action='native', # Enable native sorting
            filter_action='native' # Enable native filtering
        )
    ])


    return (kpi_cards, fig_ltv_cac, fig_payback, fig_health,
            fig_avg_ltv_cac_industry, fig_avg_payback_industry,
            fig_cust_count_company_size, fig_avg_ltv_cac_plan,
            customer_list_table)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

