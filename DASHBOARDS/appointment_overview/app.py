import sys
import os
import polars as pl
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_requests import get_appointments_df
from functions_by_filtered_data import calculate_kpis, create_figures


def create_dash_app(): 
    # Get appointment data
    appointments_url = 'http://localhost:8000/app/appointments/'
    appointments_df = get_appointments_df(appointments_url)

    # Made simple wrangling to get the data in the right format
    grouped_df = appointments_df.group_by(["appointment_date", "status"]).agg(
        pl.len().alias("count")
    )
    ordered_df = grouped_df.sort(["appointment_date", "status"])
    pd_df = ordered_df.to_pandas()

    # Initialize Dash app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # App layout
    app.layout = html.Div([
        dbc.Row([
            dbc.Col(html.H1("Appointment Analysis Dashboard"), width=12)
        ], style={'padding': '20px'}),
        
        # Date Picker Range to filter data
        dbc.Row([
            dbc.Col(dcc.DatePickerRange(
                id='date-picker-range',
                start_date=pd_df['appointment_date'].min().date(),
                end_date=pd_df['appointment_date'].max().date(),
                display_format='YYYY-MM-DD',
                style={'width': '100%'}
            ), width=12)
        ], style={'padding': '20px'}),

        # KPI Cards
        dbc.Row([
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H4("Total Appointments", className="card-title"),
                    html.P(id="total-appointments", className="card-text")
                ])
            ), width=3, style={'padding': '10px'}),
            
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H4("Completed Appointments", className="card-title"),
                    html.P(id="completed-appointments", className="card-text")
                ])
            ), width=3, style={'padding': '10px'}),
            
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H4("Cancellations", className="card-title"),
                    html.P(id="cancellations", className="card-text")
                ])
            ), width=3, style={'padding': '10px'}),
            
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H4("No-show", className="card-title"),
                    html.P(id="no-show", className="card-text")
                ])
            ), width=3, style={'padding': '10px'})
        ], style={'padding': '20px'}),

        # Charts
        dbc.Row([
            dbc.Col(dcc.Graph(id='line-plot'), width=8, style={'padding': '10px'}),
            dbc.Col(dcc.Graph(id='pie-plot'), width=4, style={'padding': '10px'})
        ], style={'padding': '20px'})
    ])

    # Callback to update the graphs and KPIs based on the date range filter
    @app.callback(
        [Output('total-appointments', 'children'),
        Output('completed-appointments', 'children'),
        Output('cancellations', 'children'),
        Output('no-show', 'children'),
        Output('line-plot', 'figure'),
        Output('pie-plot', 'figure')],
        [Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')]
    )

    def update_dashboard(start_date, end_date):
        # Filter data based on selected date range
        filtered_df = pd_df[(pd_df['appointment_date'] >= start_date) & (pd_df['appointment_date'] <= end_date)]
        
        # Calculate KPIs
        total_appointments, completed_appointments, cancellations, no_show = calculate_kpis(filtered_df)
        
        # Create figures
        fig_line, fig_pie = create_figures(filtered_df)
        
        # Return updated KPIs and figures
        return total_appointments, completed_appointments, cancellations, no_show, fig_line, fig_pie
    

    return app
