import pandas as pd

# LOAD DATA
FILE_PATH = "floorsheet_floorsheetdata_cleaned.csv"  
df = pd.read_csv(FILE_PATH)
print("Initial Columns:")
print(df.columns)

# Sort by symbol and date (VERY IMPORTANT for rolling)
df = df.sort_values(by=['symbol', 'date'])
print("\nData after cleaning:")
print(df.head())

# Rolling window size
WINDOW = 5
df['rolling_qty'] = (
    df.groupby('symbol')['quantity']
    .rolling(window=WINDOW, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)
df['rolling_rate'] = (
    df.groupby('symbol')['rate']
    .rolling(window=WINDOW, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)
df['rolling_amount'] = (
    df.groupby('symbol')['amount']
    .rolling(window=WINDOW, min_periods=1)
    .sum()
    .reset_index(level=0, drop=True)
)
# BROKER LEVEL ROLLING ANALYSIS
# Buyer rolling quantity
df['buyer_rolling_qty'] = (
    df.groupby(['symbol', 'buyer'])['quantity']
    .rolling(window=WINDOW, min_periods=1)
    .sum()
    .reset_index(level=[0, 1], drop=True)
)
# Seller rolling quantity
df['seller_rolling_qty'] = (
    df.groupby(['symbol', 'seller'])['quantity']
    .rolling(window=WINDOW, min_periods=1)
    .sum()
    .reset_index(level=[0, 1], drop=True)
)
# MARKET INTENSITY SIGNALS
df['price_change'] = df.groupby('symbol')['rate'].diff()
df['high_volume_flag'] = df['quantity'] > df['rolling_qty'] * 1.5
df['price_spike_flag'] = df['price_change'] > df['rate'].rolling(WINDOW).std()

# FINAL OUTPUT
OUTPUT_FILE = "floorsheet_rolling_analysis.csv"
df.to_csv(OUTPUT_FILE, index=False)
print("\nAnalysis completed!")
print(f"Output saved as: {OUTPUT_FILE}")
