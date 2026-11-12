"""Deterministic daily-bar indicators and APPROVED strategy candidates."""
from __future__ import annotations
import numpy as np
import pandas as pd

STRATEGIES = ("EMA_TREND", "RSI_REVERSION", "BREAKOUT")


def enrich_one_symbol(x: pd.DataFrame) -> pd.DataFrame:
    x = x.sort_values("Date").copy()
    c, h, l = x.Close.astype(float), x.High.astype(float), x.Low.astype(float)
    x["EMA20"] = c.ewm(span=20, adjust=False, min_periods=20).mean()
    x["EMA50"] = c.ewm(span=50, adjust=False, min_periods=50).mean()
    change = c.diff()
    gain = change.clip(lower=0).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    loss = (-change.clip(upper=0)).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rs = gain / loss.replace(0, np.nan)
    x["RSI14"] = (100 - (100 / (1 + rs))).fillna(50)
    prev_c = c.shift(1)
    tr = pd.concat([(h-l), (h-prev_c).abs(), (l-prev_c).abs()], axis=1).max(axis=1)
    x["ATR14"] = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    up, down = h.diff(), -l.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0), index=x.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0), index=x.index)
    plus_di = 100 * plus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / x.ATR14.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / x.ATR14.replace(0, np.nan)
    dx = 100 * (plus_di-minus_di).abs() / (plus_di+minus_di).replace(0, np.nan)
    x["ADX14"] = dx.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    x["Prior20High"] = h.shift(1).rolling(20, min_periods=20).max()
    x["RealizedVol20"] = c.pct_change().rolling(20, min_periods=20).std() * np.sqrt(252)
    x["Ready"] = x[["EMA20", "EMA50", "ATR14", "ADX14", "Prior20High", "RealizedVol20"]].notna().all(axis=1)
    def regime(row):
        if not row.Ready:
            return "WARMUP"
        if row.RealizedVol20 > 0.48 or row.ATR14/row.Close > 0.065:
            return "HIGH_VOL"
        if row.Close > row.Prior20High and row.ADX14 >= 18:
            return "BREAKOUT"
        if row.ADX14 >= 22 and row.EMA20 > row.EMA50:
            return "TREND"
        if row.ADX14 < 22:
            return "RANGE"
        return "UNCERTAIN"
    x["Regime"] = x.apply(regime, axis=1)
    x["RoutedStrategy"] = x.Regime.map({"TREND": "EMA_TREND", "RANGE": "RSI_REVERSION", "BREAKOUT": "BREAKOUT"}).fillna("NONE")
    return x


def prepare_indicators(df: pd.DataFrame) -> pd.DataFrame:
    parts = [enrich_one_symbol(x) for _, x in df.groupby("Symbol", sort=False)]
    return pd.concat(parts, ignore_index=True).sort_values(["Date", "Symbol"]).reset_index(drop=True)


def entry_signal(row, strategy: str) -> bool:
    if not bool(row.Ready):
        return False
    if strategy == "EMA_TREND":
        return bool(row.EMA20 > row.EMA50 and row.Close > row.EMA20)
    if strategy == "RSI_REVERSION":
        return bool(row.RSI14 < 42 and row.Close > row.EMA50 * 0.88)
    if strategy == "BREAKOUT":
        return bool(row.Close > row.Prior20High and row.ADX14 >= 18)
    return False


def exit_signal(row, strategy: str) -> bool:
    if not bool(row.Ready):
        return False
    if strategy == "EMA_TREND":
        return bool(row.EMA20 < row.EMA50)
    if strategy == "RSI_REVERSION":
        return bool(row.RSI14 > 58)
    if strategy == "BREAKOUT":
        return bool(row.Close < row.EMA20)
    return False


def chosen_strategy(row, mode: str = "ROUTER") -> str:
    return str(row.RoutedStrategy) if mode == "ROUTER" else mode
