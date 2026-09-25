"""
Fetches Nifty 50 (^NSEI) 15-minute OHLC data via yfinance and appends
only new rows to a CSV file, so it can be run repeatedly (e.g. every
15 min via cron / GitHub Actions) without creating duplicates.
"""

import os
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

TICKER = "^NSEI"          # Nifty 50 index
INTERVAL = "15m"
DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "nifty_15min.csv")

# yfinance only serves 15m data for the last ~60 days, so a short
# lookback window is enough — we dedupe against what's already saved.
LOOKBACK_DAYS = 5


def fetch_latest(ticker: str, interval: str, lookback_days: int) -> pd.DataFrame:
    end = datetime.utcnow()
    start = end - timedelta(days=lookback_days)
    df = yf.download(
        tickers=ticker,
        start=start,
        end=end,
        interval=interval,
        progress=False,
        auto_adjust=False,
    )
    if df.empty:
        return df

    # yfinance sometimes returns a MultiIndex column header even for
    # a single ticker — flatten it if so.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()
    # Column is named "Datetime" for intraday intervals
    df.rename(columns={"Datetime": "datetime", "Date": "datetime"}, inplace=True)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df[["datetime", "Open", "High", "Low", "Close", "Volume"]]


def load_existing(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=["datetime", "Open", "High", "Low", "Close", "Volume"])
    df = pd.read_csv(csv_path, parse_dates=["datetime"])
    return df


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    new_data = fetch_latest(TICKER, INTERVAL, LOOKBACK_DAYS)
    if new_data.empty:
        print("No data returned (market may be closed). Exiting.")
        return

    existing = load_existing(CSV_PATH)

    combined = pd.concat([existing, new_data], ignore_index=True)
    combined.drop_duplicates(subset="datetime", keep="last", inplace=True)
    combined.sort_values("datetime", inplace=True)

    combined.to_csv(CSV_PATH, index=False)

    added = len(combined) - len(existing)
    print(f"Fetched {len(new_data)} rows from source. "
          f"{added} new rows added. Total rows now: {len(combined)}.")


if __name__ == "__main__":
    main()
