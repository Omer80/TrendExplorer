# TrendScope

Interactive Streamlit app for exploring and detecting trends in time-series data.

---

## Features

* **Raw data preview** – upload any JSON time-series file and preview the first rows.
* **Flexible plotting** – select numeric variables and view them with a built-in line chart.
* **Trend analysis** – pick one series, choose methods (OLS slope, Linear Regression, Kendall’s τ), set window size, trend direction, and number of top intervals.
* **Interactive chart** – embedded Plotly figure with shaded windows, markers, and a range selector.
* **CSV export** – download detected intervals (start, end, method, slope) as CSV, with a custom filename.

---

## Installation

1. **Clone this repo**

   ```bash
   git clone https://github.com/you/your-repo.git
   cd your-repo
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally**

   ```bash
   streamlit run streamlit_app.py
   ```

---

## JSON input format (concise example)

```json
[
  { "timestamp": 1689400000000,
    "data": { "metric1": 12.3, "metric2": 45.6 }
  },
  { "timestamp": 1689400005000,
    "data": { "metric1": 13.1, "metric2": 44.2 }
  }
]
```

* **timestamp**: milliseconds since epoch
* **data**: object with numeric fields (flattened into columns)

---

## Repo structure

```
.
├── analysis_tools/        ← slope modules
│   └── slopes.py
├── plotting_tools/        ← interactive plot module
│   └── interactive.py
├── requirements.txt       ← dependencies
├── streamlit_app.py       ← main Streamlit app
└── README.md              ← this file
```

Enjoy exploring your time-series data with TrendScope!