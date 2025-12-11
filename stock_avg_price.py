import pandas as pd

# Load cleaned data if available, otherwise minimally clean raw file
try:
    df = pd.read_csv('floorsheet_floorsheetdata_cleaned.csv', parse_dates=['date'])
except FileNotFoundError:
    df = pd.read_csv('floorsheet_floorsheetdata.csv')
    df['quantity'] = pd.to_numeric(df['quantity'].astype(str).str.replace(',', ''), errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',', ''), errors='coerce')
    df['rate'] = pd.to_numeric(df['rate'].astype(str).str.replace(',', ''), errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Remove rows with missing symbol or rate
df = df.dropna(subset=['symbol', 'rate', 'quantity'])

# Compute simple average price (mean of `rate`) and VWAP per symbol
agg = df.groupby('symbol').apply(lambda g: pd.Series({
    'trade_count': len(g),
    'total_quantity': g['quantity'].sum(),
    'total_value': (g['rate'] * g['quantity']).sum(),
    'avg_rate': g['rate'].mean(),
    'vwap': (g['rate'] * g['quantity']).sum() / g['quantity'].sum()
})).reset_index()

# Sort by vwap or total_quantity as needed
agg_sorted_vwap = agg.sort_values('vwap', ascending=False)
agg_sorted_volume = agg.sort_values('total_quantity', ascending=False)

# Print top 20 by VWAP and by Volume
top_n = 20
print(f"Top {top_n} stocks by VWAP:\n")
print(agg_sorted_vwap.head(top_n).to_string(index=False))

print(f"\nTop {top_n} stocks by Total Quantity (volume):\n")
print(agg_sorted_volume.head(top_n).to_string(index=False))

# Save to CSV
agg.to_csv('stock_avg_and_vwap.csv', index=False)
print('\nSaved CSV: stock_avg_and_vwap.csv')
