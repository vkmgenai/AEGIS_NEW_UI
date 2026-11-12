"""Reproducible educational OHLCV data and optional research-only NSE download."""
from __future__ import annotations
import numpy as np
import pandas as pd

DEFAULT_SYMBOLS = ("RELIANCE", "INFY", "HDFCBANK", "ICICIBANK", "NIFTYBEES")


def synthetic_market(n_days: int = 620, symbols=DEFAULT_SYMBOLS, seed: int = 42) -> pd.DataFrame:
    """Simulated historical OHLCV; NOT actual NSE prices, fills, or a market forecast."""
    dates = pd.bdate_range("2022-01-03", periods=n_days)
    records = []
    for j, symbol in enumerate(symbols):
        rng = np.random.default_rng(seed + j * 7)
        phases = np.zeros(n_days)
        for i in range(n_days):
            phase = (i // 110 + j) % 4
            phases[i] = {0: 0.0014, 1: -0.00015, 2: 0.00005, 3: 0.0018}[phase]
        sigma = np.where(((np.arange(n_days) // 110 + j) % 4) == 1, 0.006, 0.014)
        returns = phases + rng.normal(0, sigma)
        close = (180 + 40*j) * np.exp(np.cumsum(returns))
        opens = np.r_[close[0] * 0.998, close[:-1]] * (1 + rng.normal(0, 0.003, n_days))
        upper = np.abs(rng.normal(0.005, 0.003, n_days))
        lower = np.abs(rng.normal(0.005, 0.003, n_days))
        high = np.maximum(opens, close) * (1 + upper)
        low = np.minimum(opens, close) * (1 - lower)
        volume = rng.integers(300_000, 4_000_000, size=n_days)
        for date, o, h, l, c, v in zip(dates, opens, high, low, close, volume):
            records.append((date, symbol, float(o), float(h), float(l), float(c), int(v)))
    return validate_ohlcv(pd.DataFrame(records, columns=["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"]))


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    required = ("Date", "Symbol", "Open", "High", "Low", "Close", "Volume")
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {sorted(missing)}")
    data = df.loc[:, required].copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="raise").dt.tz_localize(None).dt.normalize()
    if data.duplicated(["Date", "Symbol"]).any():
        raise ValueError("Duplicate symbol and date pairs")
    for col in ("Open", "High", "Low", "Close", "Volume"):
        data[col] = pd.to_numeric(data[col], errors="coerce")
    if not np.isfinite(data[["Open", "High", "Low", "Close", "Volume"]].to_numpy()).all():
        raise ValueError("Missing/nonfinite OHLCV data")
    if (data[["Open", "High", "Low", "Close", "Volume"]] <= 0).any().any():
        raise ValueError("Prices and volume must be positive")
    bad = (data.High < data[["Open", "Close", "Low"]].max(axis=1)) | (data.Low > data[["Open", "Close", "High"]].min(axis=1))
    if bad.any():
        raise ValueError(f"Inconsistent high/low on {int(bad.sum())} bars")
    return data.sort_values(["Date", "Symbol"]).reset_index(drop=True)


def download_nse_history(symbols=DEFAULT_SYMBOLS, start="2022-01-01", end="2026-10-31") -> pd.DataFrame:
    """Research/education only; Yahoo terms and data quality must be reviewed; no silent fallback."""
    import yfinance as yf
    all_rows = []
    for sym in symbols:
        ticker = f"{sym}.NS"
        raw = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False,
                          multi_level_index=False, threads=False)
        if raw is None or raw.empty:
            raise RuntimeError(f"No data returned for {ticker}; try a narrower period or another provider")
        x = raw.reset_index()
        x["Symbol"] = sym
        all_rows.append(x[["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"]])
    return validate_ohlcv(pd.concat(all_rows, ignore_index=True))


def load_configured_market():
    """Shared source selection for MCP reads; cached dataset only for NSEPython."""
    from pathlib import Path
    import os,json
    root=Path(os.getenv('AEGIS_DATA_DIR','data'))
    settings=root/'market_config.json'
    config=json.loads(settings.read_text()) if settings.exists() else {}
    source=config.get('source',os.getenv('AEGIS_DATA_SOURCE','synthetic'))
    if source=='synthetic':return synthetic_market()
    if source=='nsepython':
        from .nse_data import load_dataset
        configured=config.get('dataset_dir')
        folder=Path(configured) if configured else Path(os.getenv('AEGIS_NSE_DATASET_DIR',str(root/'nse_nifty20')))
        if configured and not folder.is_absolute():folder=root/folder
        return load_dataset(folder)[0]
    if source=='yfinance':return download_nse_history()
    raise ValueError('Unknown market source; no silent synthetic fallback')
