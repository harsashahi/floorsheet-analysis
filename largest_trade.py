import pandas as pd
import numpy as np

# Load cleaned data if available, otherwise minimally clean raw file
try:
    df = pd.read_csv('floorsheet_floorsheetdata_cleaned.csv', parse_dates=['date'])
except FileNotFoundError:
    df = pd.read_csv('floorsheet_floorsheetdata.csv')
    df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',', ''), errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'].astype(str).str.replace(',', ''), errors='coerce')
    df['rate'] = pd.to_numeric(df['rate'].astype(str).str.replace(',', ''), errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Drop rows without amount
df = df.dropna(subset=['amount'])

# Ensure numeric type
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# Largest trades by amount
top_n = 50
largest_trades = df.sort_values('amount', ascending=False).head(top_n)
print(f"Top {top_n} largest trades by amount:\n")
print(largest_trades[['id','transaction_no','symbol','buyer','seller','quantity','rate','amount','date']].to_string(index=False))

# Save largest trades
largest_trades.to_csv('largest_trades.csv', index=False)

# Flag extreme outliers: trades with amount > mean + 3*std
mean_amt = df['amount'].mean()
std_amt = df['amount'].std()
threshold = mean_amt + 3 * std_amt
outliers = df[df['amount'] > threshold].sort_values('amount', ascending=False)
print(f"\nThreshold for outliers (mean + 3*std): {threshold:.2f}")
print(f"Found {len(outliers)} outlier trades.\n")

# Save outliers
outliers.to_csv('largest_trade_outliers.csv', index=False)
print('Saved CSVs: largest_trades.csv, largest_trade_outliers.csv')
