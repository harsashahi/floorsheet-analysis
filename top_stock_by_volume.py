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

# Ensure symbol present
if 'symbol' not in df.columns:
    raise SystemExit('No `symbol` column found in dataset')

# Compute total traded volume (quantity) per symbol
volume_by_symbol = df.groupby('symbol', dropna=True)['quantity'].sum().sort_values(ascending=False)

# Show top 20
top_n = 20
print(f"Top {top_n} stocks by traded volume (quantity):")
print(volume_by_symbol.head(top_n))

# Save results
volume_by_symbol.to_csv('top_stocks_by_volume.csv', header=['total_quantity'])
print('\nSaved CSV: top_stocks_by_volume.csv')
