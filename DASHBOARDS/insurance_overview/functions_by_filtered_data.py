import polars as pl
import plotly.express as px

# Function to create the figures based on the filtered data
def create_figures(df_merged):

    result = df_merged.group_by(["status", "insurance"]).agg(
        pl.len().alias("count")
    )
    result = result.sort("count", descending=True)
    df = result.to_pandas()
    fig_bar = px.bar(df, x='insurance', y='count', color='status', title='top insurance')

    result = df_merged.group_by(["age", "insurance"]).agg(
        pl.len().alias("count")
    )
    result = result.sort(["age","count"], descending=True)
    df = result.to_pandas()
    fig_line = px.line(df, x='age', y='count', color='insurance', title='top insurance', markers=True)

    result = df_merged.group_by(["appointment_duration", "insurance"]).agg(
        pl.len().alias("count")
    )
    result = result.sort(["appointment_duration","count"], descending=True)
    df = result.to_pandas()
    df['time_diff_minutes'] = df['appointment_duration'].dt.total_seconds() / 60
    fig = px.scatter(
        df, x='time_diff_minutes', y='count', color='insurance',
        trendline='lowess',  # Locally weighted regression
        trendline_options=dict(frac=0.2)  # Smoothness of the curve
    )
    fig.for_each_trace(
        lambda trace: trace.update(marker=dict(opacity=0)) if 'trendline' not in trace.name else None
    )
    y_max = df['count'].max()
    fig.update_xaxes(range=[0, 60]) 
    fig.update_yaxes(range=[0, 110]) 

    return fig_line, fig_bar, fig