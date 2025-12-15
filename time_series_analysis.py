import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA

# 1. LOAD CSV
df = pd.read_csv("floorsheet_floorsheetdata_cleaned.csv")

# Show columns
print("\nColumns in your dataset:\n")
print(df.columns.tolist())

# 2. COLUMN MAPPING
DATE_COL      = "date"       # lowercase as in your CSV
SYMBOL_COL    = "symbol"
RATE_COL      = "rate"
QUANTITY_COL  = "quantity"
AMOUNT_COL    = "amount"


# Convert date column
df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors='coerce')

# Drop rows with invalid dates
df = df.dropna(subset=[DATE_COL])

# Set date as index
df = df.sort_values(DATE_COL)
df.set_index(DATE_COL, inplace=True)

print("\nCleaned sample data:\n")
print(df.head())

#  DAILY AGGREGATION

daily_volume = df[QUANTITY_COL].resample('D').sum()
daily_turnover = df[AMOUNT_COL].resample('D').sum()
daily_vwap = (df[RATE_COL] * df[QUANTITY_COL]).resample('D').sum() / df[QUANTITY_COL].resample('D').sum()

#  BROKER-LEVEL ANALYSIS

# Total buy quantity per broker
buy_volume = df.groupby('buyer')[QUANTITY_COL].sum().sort_values(ascending=False)
print("\nTop Brokers by Buy Quantity:\n")
print(buy_volume.head(10))

# Total sell quantity per broker
sell_volume = df.groupby('seller')[QUANTITY_COL].sum().sort_values(ascending=False)
print("\nTop Brokers by Sell Quantity:\n")
print(sell_volume.head(10))

# Total turnover per broker
buy_turnover = df.groupby('buyer')[AMOUNT_COL].sum().sort_values(ascending=False)
sell_turnover = df.groupby('seller')[AMOUNT_COL].sum().sort_values(ascending=False)

print("\nTop Brokers by Buy Turnover:\n")
print(buy_turnover.head(10))
print("\nTop Brokers by Sell Turnover:\n")
print(sell_turnover.head(10))

# Net position per broker (Buy Quantity - Sell Quantity)
all_brokers = set(df['buyer'].unique()).union(set(df['seller'].unique()))
net_position = {}
for broker in all_brokers:
    buys = buy_volume.get(broker, 0)
    sells = sell_volume.get(broker, 0)
    net_position[broker] = buys - sells

net_position_series = pd.Series(net_position).sort_values(ascending=False)
print("\nTop Brokers by Net Buy Position:\n")
print(net_position_series.head(10))
print("\nTop Brokers by Net Sell Position:\n")
print(net_position_series.tail(10))

# Optional: Plot top 10 brokers by net position
plt.figure(figsize=(12,6))
net_position_series.head(10).plot(kind='bar', color='green', label='Net Buy')
net_position_series.tail(10).plot(kind='bar', color='red', label='Net Sell')
plt.title("Top Brokers by Net Position")
plt.ylabel("Net Quantity")
plt.legend()
plt.show()

#  PLOTS
plt.figure(figsize=(12,5))
daily_volume.plot(title="Daily Traded Volume")
plt.show()
plt.figure(figsize=(12,5))
daily_turnover.plot(title="Daily Turnover")
plt.show()
plt.figure(figsize=(12,5))
daily_vwap.plot(title="Daily VWAP Trend")
plt.show()

#  SYMBOL-WISE ANALYSIS
symbol = "NABIL"  # Change to your symbol
df_symbol = df[df[SYMBOL_COL] == symbol]

if not df_symbol.empty:
    symbol_volume = df_symbol[QUANTITY_COL].resample("D").sum()
    plt.figure(figsize=(12,5))
    symbol_volume.plot(title=f"{symbol} - Daily Volume")
    plt.show()
else:
    print(f"\nSymbol '{symbol}' not found in dataset.\n")

#  MOVING AVERAGES
ma7 = daily_vwap.rolling(7).mean()
ma30 = daily_vwap.rolling(30).mean()
plt.figure(figsize=(12,5))
ma7.plot(label="7-day MA")
ma30.plot(label="30-day MA")
plt.title("VWAP Moving Averages")
plt.legend()
plt.show()

#  DETECT VOLUME SPIKES
threshold = daily_volume.mean() + 3 * daily_volume.std()
spikes = daily_volume[daily_volume > threshold]
print("\nDetected Volume Spikes:\n")
print(spikes)
plt.figure(figsize=(12,5))
daily_volume.plot(label="Daily Volume")
spikes.plot(style="o", label="Spike")
plt.title("Volume Spike Detection")
plt.legend()
plt.show()

#  TREND + SEASONALITY
try:
    decomposition = seasonal_decompose(daily_volume, model="additive")
    decomposition.plot()
    plt.show()
except:
    print("\nNot enough data for seasonal decomposition.\n")

#  ARIMA FORECASTING

try:
    model = ARIMA(daily_volume, order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(7)
    print("\n7-Day Volume Forecast:\n", forecast)
    plt.figure(figsize=(12,5))
    forecast.plot(title="7-Day Volume Forecast")
    plt.show()

except Exception as e:
    print("\nARIMA model failed:", e)
