# SPY Options Flow & Volatility Analysis

A quantitative options analysis pipeline for SPY (S&P 500 ETF) that detects unusual options activity by comparing Implied Volatility (IV) to Realized Volatility (RV), and identifies statistically significant volume and open interest spikes.

> **Data pulled:** April 7, 2026 | **Expiry analyzed:** April 7, 2026 (nearest expiry) | **RV (21-day):** 18.41%

---

## What This Does

This project automates the following workflow:

```
Pull historical prices → Compute Realized Volatility (RV)
       ↓
Pull options chain (calls + puts)
       ↓
Calculate IV-RV spread per contract
       ↓
Flag unusual activity (volume & OI spikes > μ + 2σ)
       ↓
Visualize: heatmaps, volume bars, RV trend
```

The core insight is that **IV - RV spread** reveals how much the market is paying for optionality above what recent price movement justifies. Large positive spreads indicate fear or informed positioning; negative spreads suggest complacency or mispricing.

---

## Project Structure

```
spy_options_analysis/
│
├── data_pull.py                  # Main pipeline script
│
├── data/
│   ├── spy_historical_prices.csv # 6-month daily OHLCV
│   ├── spy_calls.csv             # Full call chain (nearest expiry)
│   ├── spy_puts.csv              # Full put chain (nearest expiry)
│   ├── spy_unusual_calls.csv     # Flagged unusual calls
│   └── spy_unusual_puts.csv      # Flagged unusual puts
│
├── charts/
│   ├── RV.png                    # Realized volatility (6-month)
│   ├── Figure_1.png              # RV vs IV-RV scatter
│   ├── Call_Heatmap.png          # Calls IV-RV spread by strike/date
│   ├── Puts_Heatmap.png          # Puts IV-RV spread by strike/date
│   └── OpsVolume_byStrike.png    # Volume by strike (calls vs puts)
│
└── FINDINGS.md                   # Full market analysis & interpretation
```

---

## Setup & Usage

### Requirements

```bash
pip install yfinance pandas numpy matplotlib seaborn
```

### Run

```bash
python data_pull.py
```

This will:
1. Download 6 months of SPY daily price history
2. Pull the nearest-expiry options chain (calls + puts)
3. Compute 21-day rolling realized volatility
4. Calculate IV-RV spreads and flag unusual contracts
5. Save CSVs and display all 5 charts

---

## Methodology

### Realized Volatility (RV)
21-day rolling standard deviation of daily log returns, annualized by multiplying by √252. This captures recent actual price movement as a volatility benchmark.

```python
hist["RV"] = hist['returns'].rolling(21).std() * np.sqrt(252)
```

### IV-RV Spread
For each contract, the spread is:
```
IV_RV_spread = impliedVolatility - latest_RV
```
Positive → options are expensive relative to recent realized vol  
Negative → options are cheap relative to recent realized vol

### Unusual Activity Detection
A contract is flagged as unusual if **either** condition is met:
- Volume > mean + 2σ (volume spike)
- Open Interest > mean + 2σ (OI spike)

This is a 2-standard-deviation filter, catching roughly the top ~2.3% of contracts by activity level.

---

## Key Charts

| Chart | What It Shows |
|-------|--------------|
| `RV.png` | 6-month realized volatility trend with latest RV reference line |
| `Figure_1.png` | RV time series overlaid with IV-RV spread dots (calls=red, puts=green) |
| `Call_Heatmap.png` | IV-RV spread intensity by strike and last trade date for calls |
| `Puts_Heatmap.png` | IV-RV spread intensity by strike and last trade date for puts |
| `OpsVolume_byStrike.png` | Raw volume concentration by strike |

---

## Key Findings (April 7, 2026)

See [FINDINGS.md](FINDINGS.md) for the full analysis.

**TL;DR:**
- RV spiked to **18.41%** — its highest level in 6 months, up from a ~8% floor in January
- Put IV-RV spreads at deep OTM strikes (500–545) reached **+14% to +30%** above RV — extreme fear premium
- Massive volume concentration at **640–660 strikes**, dominated by **put flow (~3.5:1 put/call ratio)**
- Unusual calls at **653 and 654 strikes** show high ATM activity consistent with day-trading or short-term directional plays
- The 500-strike call carried the highest IV-RV spread among calls (**~2.5x RV**), suggesting someone buying extreme upside as a convex hedge or reversal bet

---

## Limitations & Next Steps

- **Single expiry only** — extending to full term structure would reveal vol surface shape
- **Blunt unusual filter** — volume/OI relative to strike-level peers would be more precise
- **No delta adjustment** — OI/volume in delta-equivalent terms would better reflect actual market exposure
- **No put/call ratio per strike** — adding this would sharpen directional reads
- **No Greeks** — adding delta, gamma, vega per contract would enable more advanced analysis

---

## Disclaimer

This project is for educational and research purposes only. Nothing here constitutes financial advice or a trading recommendation.
