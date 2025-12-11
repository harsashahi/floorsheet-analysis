import pandas as pd

# 1. Load CSV
df = pd.read_csv("floorsheet_floorsheetdata.csv")

# 2. Convert numeric columns
for col in ["quantity", "amount", "rate"]:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

# 3. Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# 4. Aggregate daily stock-wise stats
stock_daily = df.groupby(['symbol', df['date'].dt.date]).agg({
    'quantity': 'sum',
    'amount': 'sum',
    'rate': ['mean', 'max', 'min'],
    'buyer': 'nunique',
    'seller': 'nunique'
}).reset_index()

# Flatten multi-level columns
stock_daily.columns = ['symbol', 'date', 'total_quantity', 'total_amount', 'avg_rate', 'max_rate', 'min_rate', 'unique_buyers', 'unique_sellers']

# 5. Detect potential pump: sudden volume spike or large price increase
# For simplicity, flag if quantity > 2x daily average or rate > 10% increase from previous day
stock_daily['prev_avg_quantity'] = stock_daily.groupby('symbol')['total_quantity'].shift(1)
stock_daily['prev_avg_rate'] = stock_daily.groupby('symbol')['avg_rate'].shift(1)

# Conditions
stock_daily['volume_spike'] = stock_daily['total_quantity'] > 2 * stock_daily['prev_avg_quantity']
stock_daily['price_jump'] = stock_daily['avg_rate'] > 1.1 * stock_daily['prev_avg_rate']

# Flag potential pump-and-dump days
stock_daily['potential_pump_dump'] = stock_daily['volume_spike'] & stock_daily['price_jump']

# 6. Show flagged rows
flagged = stock_daily[stock_daily['potential_pump_dump'] == True]
print("\n===== Potential Pump-and-Dump Cases =====\n")
print(flagged[['symbol', 'date', 'total_quantity', 'avg_rate', 'volume_spike', 'price_jump']])

# 7. Save to CSV
flagged.to_csv("potential_pump_and_dump.csv", index=False)
print("\nFlagged potential pump-and-dump cases saved to 'potential_pump_and_dump.csv'")
