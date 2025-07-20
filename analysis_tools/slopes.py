import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from scipy.stats import kendalltau
import pandas as pd


def rolling_ols_slope(y: pd.Series, window) -> pd.Series:
    """
    Compute rolling OLS slope (per second) of y, over a time-based or fixed window.
    y.index must be a DateTimeIndex.
    """
    def _slope(y_window: pd.Series) -> float:
        # y_window.index is the timestamps in the window
        t_ns = y_window.index.astype('int64')    # nanoseconds since epoch
        t_s  = t_ns / 1e9                        # convert to seconds
        t_rel = t_s - t_s[0]                     # relative to window start

        X = sm.add_constant(t_rel)
        model = sm.OLS(y_window.values, X).fit()
        return float(model.params[1])            # slope in units y per second

    # Apply with raw=False so func gets a Series (not a numpy array)
    return y.rolling(window, min_periods=2).apply(_slope, raw=False)

def rolling_sklearn_slope(y: pd.Series, window) -> pd.Series:
    def _slope(y_window: pd.Series) -> float:
        if y_window.isna().any():
            return np.nan

        # pull timestamps out as a numpy array of seconds
        t_ns = y_window.index.astype('int64').to_numpy()
        t_s  = t_ns / 1e9
        t_rel = t_s - t_s[0]

        # now reshape works
        X = t_rel.reshape(-1, 1)
        lr = LinearRegression().fit(X, y_window.values)
        return float(lr.coef_[0])

    return y.rolling(window, min_periods=2).apply(_slope, raw=False)


def rolling_kendall_tau(y: pd.Series, window) -> pd.Series:
    def _tau(y_window: pd.Series) -> float:
        if y_window.isna().any():
            return np.nan

        t_ns  = y_window.index.astype('int64').to_numpy()
        t_s   = t_ns / 1e9
        t_rel = t_s - t_s[0]

        tau, _ = kendalltau(t_rel, y_window.values)
        return float(tau)

    return y.rolling(window, min_periods=2).apply(_tau, raw=False)