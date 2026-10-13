import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from databricks.sdk.core import Config
from databricks.sql import connect
from datetime import datetime, timedelta

# Initialize Databricks connection
cfg = Config()

warehouse_id = os.environ["DATABRICKS_WAREHOUSE_ID"]
warehouse_http_path = f"/sql/1.0/warehouses/{warehouse_id}"

def get_connection():
    server_hostname = cfg.host.replace("https://", "").replace("http://", "")

    return connect(
        server_hostname=server_hostname,
        http_path=warehouse_http_path,
        credentials_provider=lambda: cfg.authenticate,
        _use_arrow_native_complex_types=False,
    )

def execute_query(query):
    """Execute a SQL query and return results as a DataFrame"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)

# Initialize the Dash app with Bootstrap styling
dash_app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load well list for dropdown
wells_query = """
SELECT DISTINCT
    w.well_id,
    w.well_name,
    w.operator,
    w.basin
FROM istm637_valduarte.oilgas.dim_well w
INNER JOIN istm637_valduarte.oilgas.well_forecast f
    ON w.well_id = f.well_id
WHERE w.well_id IS NOT NULL
ORDER BY w.well_name
"""

wells_df = execute_query(wells_query)
well_options = [
    {"label": f"{row['well_name']} ({row['operator']}) - {row['basin']}", 
     "value": row['well_id']} 
    for _, row in wells_df.iterrows()
]

# Define the app layout
dash_app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Oil & Gas Production Forecasting", className="text-primary mb-0"),
            html.P("180-Day Production Forecast by Well", className="text-muted")
        ], width=12)
    ], className="mb-4 mt-3"),
    
    # Well Selection
    dbc.Row([
        dbc.Col([
            html.Label("Select Well:", className="fw-bold"),
            dcc.Dropdown(
                id='well-selector',
                options=well_options,
                value=well_options[0]['value'] if well_options else None,
                clearable=False,
                className="mb-3"
            )
        ], width=12)
    ]),
    
    # Well Information Cards
    html.Div(id='well-info-cards', className="mb-4"),
    
    # KPI Cards
    dbc.Row(id='kpi-cards', className="mb-4"),
    
    # Production Chart
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Historical & Forecasted Oil Production", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='production-chart', style={'height': '500px'})
                ])
            ])
        ], width=12)
    ])
], fluid=True, style={'maxWidth': '1400px'})

@callback(
    Output('well-info-cards', 'children'),
    Output('kpi-cards', 'children'),
    Output('production-chart', 'figure'),
    Input('well-selector', 'value')
)
def update_dashboard(selected_well):
    if not selected_well:
        return [], [], go.Figure()
    
    # Get well information
    well_info_query = f"""
    SELECT well_name, operator, basin, field_name, status, completion_date
    FROM istm637_valduarte.oilgas.dim_well
    WHERE well_id = '{selected_well}'
    """
    well_info = execute_query(well_info_query).iloc[0]
    
    # Create well info cards
    well_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Well Name", className="text-muted mb-1"),
                    html.H5(well_info['well_name'], className="mb-0")
                ])
            ])
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Operator", className="text-muted mb-1"),
                    html.H5(well_info['operator'], className="mb-0")
                ])
            ])
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Basin", className="text-muted mb-1"),
                    html.H5(well_info['basin'], className="mb-0")
                ])
            ])
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Field", className="text-muted mb-1"),
                    html.H5(well_info['field_name'], className="mb-0")
                ])
            ])
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Status", className="text-muted mb-1"),
                    html.H5(well_info['status'], className="mb-0")
                ])
            ])
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Completion Date", className="text-muted mb-1"),
                    html.H5(str(well_info['completion_date']) if pd.notna(well_info['completion_date']) else 'N/A', className="mb-0")
                ])
            ])
        ], width=2)
    ])
    
    # Get historical production data
    historical_query = f"""
    SELECT dd.calendar_date, fp.oil_bbl
    FROM istm637_valduarte.oilgas.fact_production fp
    INNER JOIN istm637_valduarte.oilgas.dim_date dd ON fp.date_id = dd.date_id
    WHERE fp.well_id = '{selected_well}'
    ORDER BY dd.calendar_date
    """
    historical_df = execute_query(historical_query)
    historical_df['calendar_date'] = pd.to_datetime(historical_df['calendar_date'])
    
    # Get forecast data
    forecast_query = f"""
    SELECT day_ahead, predicted_oil_bbl
    FROM istm637_valduarte.oilgas.well_forecast
    WHERE well_id = '{selected_well}'
    ORDER BY day_ahead
    """
    forecast_df = execute_query(forecast_query)
    
    # Calculate forecast dates starting from last historical date + 1 day
    if not historical_df.empty:
        last_date = historical_df['calendar_date'].max()
        forecast_df['calendar_date'] = [last_date + timedelta(days=int(d)) for d in forecast_df['day_ahead']]
    
    # Calculate KPIs
    total_historical = historical_df['oil_bbl'].sum() if not historical_df.empty else 0
    total_forecast = forecast_df['predicted_oil_bbl'].sum() if not forecast_df.empty else 0
    
    # Create KPI cards
    kpi_cards = [
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Historical Production", className="text-muted mb-2"),
                    html.H3(f"{total_historical:,.0f} bbls", className="text-primary mb-0"),
                    html.P(f"{len(historical_df)} days of data", className="text-muted mb-0 small")
                ])
            ], color="light")
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Forecasted Production", className="text-muted mb-2"),
                    html.H3(f"{total_forecast:,.0f} bbls", className="text-success mb-0"),
                    html.P(f"Next 180 days", className="text-muted mb-0 small")
                ])
            ], color="light")
        ], width=6)
    ]
    
    # Create the production chart
    fig = go.Figure()
    
    # Add historical production
    if not historical_df.empty:
        fig.add_trace(go.Scatter(
            x=historical_df['calendar_date'],
            y=historical_df['oil_bbl'],
            mode='lines',
            name='Historical Production',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Historical</b><br>Date: %{x|%Y-%m-%d}<br>Oil: %{y:.0f} bbls<extra></extra>'
        ))
    
    # Add forecast
    if not forecast_df.empty:
        fig.add_trace(go.Scatter(
            x=forecast_df['calendar_date'],
            y=forecast_df['predicted_oil_bbl'],
            mode='lines',
            name='180-Day Forecast',
            line=dict(color='#2ca02c', width=2, dash='dash'),
            hovertemplate='<b>Forecast</b><br>Date: %{x|%Y-%m-%d}<br>Oil: %{y:.0f} bbls<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Oil Production (bbls)",
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=30, b=50)
    )
    
    return well_cards, kpi_cards, fig

if __name__ == '__main__':
    dash_app.run(debug=True)
