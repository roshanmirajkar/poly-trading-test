# poly-trading-test

A lightweight sports arbitrage trading bot for Polymarket using the Gamma Markets API.

## Features
- Fetches active Polymarket sports markets from the Gamma API.
- Groups markets by event and finds pricing gaps where outcome prices sum to less than 1.0.
- Generates a suggested bundle of orders for each detected arbitrage opportunity.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py --category sports --min-edge 0.02 --stake 200
```

## Web UI

Run the dashboard to scan markets and visualize opportunities:

```bash
python src/web_app.py
```

Then open http://localhost:8000 to launch the UI.
The dashboard loads demo opportunities by default so the layout is visible even before a live scan.

### Example output
```
Event: nba-finals-2025
Total cost: 0.9750
Edge: 0.0250
Orders:
  - Outcome: Team A | Limit: 0.48 | Size: 416.67
  - Outcome: Team B | Limit: 0.495 | Size: 404.04
----------------------------------------
```

## Notes
- This bot only scans markets and prints suggested orders. Executing trades requires integration with the Polymarket CLOB API.
- Market grouping uses event metadata when available, falling back to the market question.
