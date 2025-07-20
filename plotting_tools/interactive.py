import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

def plot_trend_intervals_interactive(
    df,
    trend_results,
    hrv_col: str = 'hrv_lnrmssd_ms',
    window: str = '5min',
    alpha: float = 0.3
) -> go.Figure:
    """
    Interactive Plotly time series with shaded trend intervals and vertical lines.

    df:             DataFrame with a DateTimeIndex and an `hrv_col` column
    trend_results:  dict of {method_name: pd.Series of top slopes}
    window:         string for window size (e.g. '5min')
    alpha:          transparency for the shaded intervals (0.0 to 1.0)
    """
    colors = px.colors.qualitative.Plotly
    ymin, ymax = df[hrv_col].min(), df[hrv_col].max()

    fig = go.Figure()

    # 1) main series in bright cyan
    fig.add_trace(go.Scatter(
        x=df.index, y=df[hrv_col],
        mode='lines', name=hrv_col,
        line=dict(color='#00FFFF', width=2)
    ))

    # 2) shaded windows
    for i, (method, slopes) in enumerate(trend_results.items()):
        col = colors[i % len(colors)]
        r, g, b = hex_to_rgb(col)
        fillcol = f'rgba({r},{g},{b},{alpha})'
        for ts in slopes.index:
            start = ts - pd.Timedelta(window)
            end = ts
            fig.add_trace(go.Scatter(
                x=[start, end, end, start],
                y=[ymin, ymin, ymax, ymax],
                fill='toself',
                fillcolor=fillcol,
                line=dict(width=0),
                hoverinfo='skip',
                showlegend=False
            ))

    # 3) markers & vertical lines
    for i, (method, slopes) in enumerate(trend_results.items()):
        col = colors[i % len(colors)]
        # marker at window end
        fig.add_trace(go.Scatter(
            x=slopes.index,
            y=df.loc[slopes.index, hrv_col],
            mode='markers',
            marker=dict(color=col, size=8),
            name=f"{method} end"
        ))
        # vertical line
        for ts in slopes.index:
            fig.add_shape(
                type='line',
                x0=ts, x1=ts,
                y0=ymin, y1=ymax,
                line=dict(color=col, dash='dash', width=2),
                layer='above'
            )

    # layout & interactivity
    fig.update_layout(
        title=f"{hrv_col} Top {len(next(iter(trend_results.values())))} Slopes ({window})",
        xaxis_title="Time",
        yaxis_title=hrv_col,
        legend_title="Method",
        hovermode="x unified",
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=1,  label="1h",  step="hour",   stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    return fig
