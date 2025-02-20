import pandas as pd
import plotly.express as px

def calculate_kpis(filtered_df):
    total_appointments = filtered_df['count'].sum()
    completed_appointments = filtered_df[filtered_df['status'] == 'attended']['count'].sum()
    cancellations = filtered_df[filtered_df['status'] == 'cancelled']['count'].sum()
    no_show = filtered_df[filtered_df['status'] == 'did not attend']['count'].sum()
    
    return total_appointments, completed_appointments, cancellations, no_show

def create_figures(filtered_df):
    fig_line = px.line(filtered_df, x='appointment_date', y='count', color='status', title='Appointments Over Time by Status')
    fig_pie = px.pie(filtered_df, names='status', values='count', title='Appointment Status Distribution')
    return fig_line, fig_pie