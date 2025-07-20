import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# analysis_tools and plotting_tools should be in src/analysis_tools, src/plotting_tools, etc.
from analysis_tools.slopes import (
    rolling_ols_slope,
    rolling_sklearn_slope,
    rolling_kendall_tau,
)
from plotting_tools.interactive import plot_trend_intervals_interactive

st.set_page_config(
    page_title='TrendScope',
    page_icon=':chart_with_downwards_trend:',
)

@st.cache_data
def load_json_to_df(uploaded_file, gmt_offset_hours: int = 3) -> pd.DataFrame:
    raw = json.load(uploaded_file)
    records = []
    for entry in raw:
        if "timestamp" not in entry:
            continue
        ts = datetime.fromtimestamp(entry["timestamp"] / 1000, tz=timezone.utc) \
             + timedelta(hours=gmt_offset_hours)
        data = entry.get("data", {}) or {}
        flat = {}
        # top-level fields
        for k, v in data.items():
            if k not in ("realtimeMetrics", "frequencyDomainMetricsCustom"):
                flat[k] = v
        # realtimeMetrics
        for k, v in (data.get("realtimeMetrics") or {}).items():
            flat[k] = v
        # freq metrics
        for k, v in (data.get("frequencyDomainMetricsCustom") or {}).items():
            flat[f"freq_{k}"] = v
        flat["timestamp"] = ts
        records.append(flat)

    df = pd.DataFrame(records)
    if "timestamp" in df:
        df = df.set_index("timestamp").sort_index()
    return df

st.title("TrendScope: Time-Series Trend Analyzer")

uploaded = st.file_uploader("Upload your JSON time-series file", type="json")
if uploaded is not None:
    df = load_json_to_df(uploaded)

    st.subheader("Raw data preview")
    st.dataframe(df.head())

    # -------------------------------------------------------------------------
    # Let user pick which numeric columns to plot
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    st.subheader("Select variables to plot")
    selected_vars = st.multiselect(
        "Which variables would you like to view?",
        options=numeric_cols,
        default=numeric_cols[:1] if numeric_cols else []
    )
    if selected_vars:
        st.subheader("Time-Series Plot")
        st.line_chart(df[selected_vars])

    # -------------------------------------------------------------------------
    # NEW: pick exactly one series to analyze (no default)
    st.subheader("Pick one series for trend analysis")
    ts_column = st.selectbox(
        "Select a single time-series column to analyze",
        options=numeric_cols
    )

    # 2) choose which methods to run
    method_map = {
        "OLS slope":              rolling_ols_slope,
        "LinearRegression slope": rolling_sklearn_slope,
        "Kendall’s tau":          rolling_kendall_tau,
    }
    selected_methods = st.multiselect(
        "Which analysis methods?",
        options=list(method_map.keys()),
        default=[]
    )

    # 3) rolling window size in minutes
    window_mins = st.slider(
        "Rolling window size (minutes)",
        min_value=1, max_value=20, value=5
    )
    window_str = f"{window_mins}min"

    # 4) detect decreasing or increasing trend
    direction = st.radio(
        "Detect...",
        options=["Decreasing trend", "Increasing trend"]
    )

    # 5) how many top intervals to mark
    top_n = st.slider(
        "Number of intervals to highlight",
        min_value=1, max_value=10, value=1
    )

        # -------------------------------------------------------------------------
    # Compute and collect results
    if ts_column and selected_methods:
        serie = df[ts_column]
        trend_results = {}
        for name in selected_methods:
            func   = method_map[name]
            slopes = func(serie, window=window_str).dropna()
            if direction.startswith("Decreasing"):
                top = slopes.nsmallest(top_n)
            else:
                top = slopes.nlargest(top_n)
            trend_results[name] = top

        # 6) embed the interactive Plotly chart
        if trend_results:
            fig = plot_trend_intervals_interactive(
                df,
                trend_results,
                hrv_col=ts_column,
                window=window_str
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No intervals found for the selected settings.")
    else:
        st.info("Choose exactly one time-series column and at least one method.")

       # -------------------------------------------------------------------------
    # Download the detected intervals as CSV
    st.subheader("Download detected intervals")

    filename = st.text_input(
        "Filename for download (include .csv):",
        value="trend_intervals.csv"
    )

    # Only show download once we've actually computed trend_results
    if 'trend_results' in locals() and trend_results:
        # Build a list of dicts, one per interval
        rows = []
        for method, slopes in trend_results.items():
            for ts, slope in slopes.items():
                start = ts - pd.Timedelta(window_str)
                rows.append({
                    "method": method,
                    "direction": "Decreasing" if direction.startswith("Decreasing") else "Increasing",
                    "start": start,
                    "end": ts,
                    "slope": slope
                })

        download_df = pd.DataFrame(rows)

        csv_bytes = download_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name=filename,
            mime="text/csv"
        )
    else:
        st.info("Run an analysis above to generate intervals you can download.")
