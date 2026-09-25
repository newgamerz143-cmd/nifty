# Nifty 15-min Data Pipeline

Automatically fetches Nifty 50 (`^NSEI`) 15-minute OHLC data via `yfinance`
and appends new rows to `data/nifty_15min.csv` — no human interaction
required once set up.

## How it works
- `fetch_nifty.py` pulls the last few days of 15-min candles, dedupes
  against what's already saved, and appends only new rows.
- `.github/workflows/fetch_nifty.yml` runs this script automatically via
  GitHub Actions every 15 minutes during NSE market hours
  (9:15 AM–3:30 PM IST, Mon–Fri), and commits the updated CSV back to
  the repo.

## Setup (5 minutes)

1. **Create a new GitHub repo** and push these files to it:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Nifty data pipeline"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. **Enable Actions** (usually on by default): go to your repo →
   **Settings → Actions → General → Workflow permissions** → select
   **"Read and write permissions"**. This lets the workflow commit the
   updated CSV back to the repo.

3. That's it. The workflow will now run automatically every 15 minutes
   during market hours. You can also trigger it manually anytime from
   the **Actions** tab → "Fetch Nifty 15-min Data" → **Run workflow**.

## Notes & limitations
- `yfinance` only serves 15-min intraday data for roughly the last
  60 days — fine for continuous collection (each run just adds the
  newest candles), but you can't backfill years of 15-min history
  this way.
- GitHub Actions' free tier includes 2,000 minutes/month for private
  repos (unlimited for public repos) — this job runs in well under a
  minute per execution, so you're comfortably within free limits even
  at ~25 runs/day.
- Scheduled GitHub Actions can be delayed by a few minutes during
  high load on GitHub's infra — it's not millisecond-precise, but
  reliable enough for 15-min bar collection.
- If you need tick-level precision or guaranteed on-time execution,
  a broker API (Zerodha Kite, Upstox) with a proper server/cron setup
  is more robust than yfinance + GitHub Actions.
- Data will land in `data/nifty_15min.csv`, growing over time as the
  workflow keeps appending new rows.

## Running locally (optional, for testing)
```bash
pip install -r requirements.txt
python fetch_nifty.py
```
