# SPY Options Flow & Volatility Analysis

A quantitative options analysis pipeline for SPY (S&P 500 ETF) that detects unusual options activity by comparing Implied Volatility (IV) to Realized Volatility (RV), and identifies statistically significant volume and open interest spikes.

> **Data pulled:** April 7, 2026 | **Expiry analyzed:** April 7, 2026 (nearest expiry) | **RV (21-day):** 18.41%

---

## What This Does

This project automates the following workflow:

Pull historical prices → Compute Realized Volatility (RV)

Pull options chain (calls + puts)

↓

Calculate IV-RV spread per contract

↓

Flag unusual activity (volume & OI spikes > μ + 2σ)

↓

Visualizations: heatmaps, volume bars, RV trend

The core insight is **IV - RV spread** that reveals how much the market is paying for optionality above what recent price movement justifies. Large positive spreads indicate fear or informed positioning; negative spreads suggest complacency or mispricing.

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
IV_RV_spread = impliedVolatility - latest_RV
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

- RV spiked to **18.41%** - its highest level in 6 months, up from a ~8% floor in January
- Put IV-RV spreads at deep OTM strikes (500–545) reached **+14% to +30%** above RV - extreme fear premium
- Massive volume concentration at **640–660 strikes**, dominated by **put flow (~3.5:1 put/call ratio)**
- Unusual calls at **653 and 654 strikes** show high ATM activity consistent with day-trading or short-term directional plays
- The 500-strike call carried the highest IV-RV spread among calls (**~2.5x RV**), suggesting someone buying extreme upside as a convex hedge or reversal bet

---

## Next Steps

- Extend to full term structure to reveal vol surface shape
- Refine unusual activity filter using volume/OI relative to strike-level peers
- Add delta-adjusted OI/volume to better reflect actual market exposure
- Add put/call ratio per strike to sharpen directional reads
- Add Greeks (delta, gamma, vega) per contract for more advanced analysis

---
