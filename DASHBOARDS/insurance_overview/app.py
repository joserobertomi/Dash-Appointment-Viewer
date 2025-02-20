import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import polars as pl
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_requests import get_appointments_df, get_patients_df
from functions_by_filtered_data import create_figures


def create_dash_app():

    # Get appointment and patient data
    appointments_url = 'http://localhost:8000/app/appointments/'
    appointments_df = get_appointments_df(appointments_url)
    patients_url = 'http://localhost:8000/app/patients'
    patients_df = get_patients_df(patients_url)

    # Made simple wrangling to get the data in the right format
    df_merged = appointments_df.join(patients_df.select(["patient_id", "insurance"]), on="patient_id", how="left")
    df_merged = df_merged[["sex", "age", "insurance", "patient_id", "status", "appointment_duration"]]

    # Initialize Dash app
    app = dash.Dash(__name__)

    # App layout
    app.layout = html.Div([
        html.H1("Medical Appointments Dashboard"),

        # Dropdown para filtrar por insurance
        dcc.Dropdown(
            id='insurance-filter',
            options=[{'label': i, 'value': i} for i in df_merged['insurance'].unique().to_list()],
            multi=True,
            placeholder="Select Insurance Plans",
        ),

        dcc.Graph(id='bar-chart'),
        dcc.Graph(id='line-chart'),
        dcc.Graph(id='scatter-chart'),
    ])

    # Callback to update the charts based on the selected insurance
    @app.callback(
        [Output('bar-chart', 'figure'),
        Output('line-chart', 'figure'),
        Output('scatter-chart', 'figure')],
        [Input('insurance-filter', 'value')]
    )
    def update_charts(selected_insurances):
        if selected_insurances is None or len(selected_insurances) == 0:
            filtered_df = df_merged
        else:
            filtered_df = df_merged.filter(
                df_merged['insurance'].is_in(selected_insurances)
            )

        fig_bar, fig_line, fig_scatter = create_figures(filtered_df)
        return fig_bar, fig_line, fig_scatter

    app.run_server(debug=True, port=8052)
