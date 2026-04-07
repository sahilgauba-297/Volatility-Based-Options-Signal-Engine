import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# defining the stock

ticker_symbol = "SPY"
ticker = yf.Ticker(ticker_symbol)

# historical price data (6 months)

hist = ticker.history(period = "6mo", interval = "1d")
hist.to_csv("spy_historical_prices.csv")
print("historical data loaded")

# pulling options expiry date

expiry_date = ticker.options
print("available expiry dates:",  expiry_date)

# pulling options chain with nearest expiry

nearest_expiry = expiry_date[0]

options_chain = ticker.option_chain(nearest_expiry)
calls = options_chain.calls
puts = options_chain.puts

calls.to_csv("spy_calls.csv", index =   False)
puts.to_csv("spy_puts.csv" , index = False)
print("options chains with nearest expiry loaded")



hist = pd.read_csv("spy_historical_prices.csv", parse_dates= ["Date"], index_col= "Date")

# daily returns
hist["returns"] = hist['Close'].pct_change()


# Calculating rolling realized volatility (daily returns to annualized)

window = 21 # 1 month
hist["RV"] = hist['returns'].rolling(window).std() * np.sqrt (252) # annual
# Because variance scales linearly with time, standard deviation scales with the square root of time.

latest_RV = hist["RV"].iloc[-1]
print(f"latest realized volatilty: {latest_RV:.2%}")

# latest RV comes out to be 18.41%

calls = pd.read_csv("spy_calls.csv")
puts = pd.read_csv("spy_puts.csv")

# IV - RV Spreads
calls['IV_RV_spread'] = calls["impliedVolatility"] - latest_RV
puts['IV_RV_spread'] = puts["impliedVolatility"] - latest_RV


# Detecting unusual activity
# Spikes = Volume > mean + 2*std, openInterest > mean + 2*std
def detect_unusual(df):
    df['volume_spike'] = df["volume"] > (df["volume"].mean() + 2*df["volume"].std())
    df["oi_spike"] = df["openInterest"] > (df["openInterest"].mean() + 2*df["openInterest"].std())
    df["unusual"] = df["volume_spike"] | df["oi_spike"]
    return df

calls = detect_unusual(calls)
puts = detect_unusual(puts)


unusual_calls = calls[calls['unusual']].sort_values(by='IV_RV_spread', ascending=False)
unusual_puts = puts[puts['unusual']].sort_values(by='IV_RV_spread', ascending=False)

unusual_calls.to_csv("spy_unsual_calls.csv", index = False)
unusual_puts.to_csv("spy_unsual_puts.csv", index = False)


print("Unusual options with IV-RV spread loaded")
print("Top unusual calls:\n", unusual_calls.head())
print("Top unusual puts:\n", unusual_puts.head())




#Visualizations

# daily returns
hist['returns'] = hist['Close'].pct_change()
window = 21
hist['RV_21d'] = hist['returns'].rolling(window).std() * np.sqrt(252)

plt.figure(figsize=(12,6))
plt.plot(hist.index, hist['RV_21d'], label='Realized Volatility (21d)')
plt.scatter(pd.to_datetime(calls['lastTradeDate']), calls['IV_RV_spread'], 
            color='red', alpha=0.6, label='Calls: IV-RV Spread')
plt.scatter(pd.to_datetime(puts['lastTradeDate']), puts['IV_RV_spread'], 
            color='green', alpha=0.6, label='Puts: IV-RV Spread')
plt.title("SPY Realized Volatility vs Unusual Options IV-RV Spread")
plt.xlabel("Date")
plt.ylabel("Volatility / IV-RV Spread")
plt.legend()
plt.show()

#Heatmaps of unusual activity by strike

# Calls heatmap
calls['lastTradeDate'] = pd.to_datetime(calls['lastTradeDate']).dt.date
puts['lastTradeDate'] = pd.to_datetime(puts['lastTradeDate']).dt.date

plt.figure(figsize=(16,10))
sns.heatmap(calls.pivot_table(index='strike', columns='lastTradeDate', values='IV_RV_spread'),
            cmap='coolwarm', center=0)
plt.title("Calls: IV-RV Spread Heatmap by Strike")
plt.show()

# Puts heatmap
plt.figure(figsize=(16,10))
sns.heatmap(puts.pivot_table(index='strike', columns='lastTradeDate', values='IV_RV_spread'),
            cmap='coolwarm', center=0)
plt.title("Puts: IV-RV Spread Heatmap by Strike")
plt.show()

# Volume spikes by strike 
plt.figure(figsize=(12,6))
plt.bar(calls['strike'], calls['volume'], color='red', alpha=0.6, label='Call Volume')
plt.bar(puts['strike'], puts['volume'], color='green', alpha=0.6, label='Put Volume')
plt.title("Unusual Options Volume by Strike")
plt.xlabel("Strike Price")
plt.ylabel("Volume")
plt.legend()
plt.show()


# IV vs RV Line Chart
plt.figure(figsize=(12,6))
plt.plot(hist.index, hist['RV'], label='Realized Volatility (RV)', color='blue')
plt.axhline(y=latest_RV, color='blue', linestyle='--', alpha=0.5)
plt.title('Realized Volatility Over Last 6 Months')
plt.ylabel('Annualized Volatility')
plt.xlabel('Date')
plt.grid(True)
plt.legend()
plt.show()