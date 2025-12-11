import pandas as pd 

import pandas as pd

# Load cleaned data if available, otherwise load raw and try minimal cleaning
try:
    df = pd.read_csv('floorsheet_floorsheetdata_cleaned.csv', parse_dates=['date'])
except FileNotFoundError:
    df = pd.read_csv('floorsheet_floorsheetdata.csv')
    df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',', ''), errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'].astype(str).str.replace(',', ''), errors='coerce')
    df['rate'] = pd.to_numeric(df['rate'].astype(str).str.replace(',', ''), errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Ensure buyer/seller numeric
df['buyer'] = pd.to_numeric(df['buyer'], errors='coerce')
df['seller'] = pd.to_numeric(df['seller'], errors='coerce')

# Prepare subsets
buyers = df.dropna(subset=['buyer']).copy()
buyers['buyer'] = buyers['buyer'].astype(int)
sellers = df.dropna(subset=['seller']).copy()
sellers['seller'] = sellers['seller'].astype(int)

# Top buyers
top_buyers_by_amount = buyers.groupby('buyer')['amount'].sum().sort_values(ascending=False).head(20)
top_buyers_by_quantity = buyers.groupby('buyer')['quantity'].sum().sort_values(ascending=False).head(20)
top_buyers_by_trades = buyers['buyer'].value_counts().head(20)

# Top sellers
top_sellers_by_amount = sellers.groupby('seller')['amount'].sum().sort_values(ascending=False).head(20)
top_sellers_by_quantity = sellers.groupby('seller')['quantity'].sum().sort_values(ascending=False).head(20)
top_sellers_by_trades = sellers['seller'].value_counts().head(20)

# Output results
print('\nTop 20 Buyers by Total Amount:')
print(top_buyers_by_amount)
print('\nTop 20 Buyers by Total Quantity:')
print(top_buyers_by_quantity)
print('\nTop 20 Buyers by Number of Trades:')
print(top_buyers_by_trades)

print('\nTop 20 Sellers by Total Amount:')
print(top_sellers_by_amount)
print('\nTop 20 Sellers by Total Quantity:')
print(top_sellers_by_quantity)
print('\nTop 20 Sellers by Number of Trades:')
print(top_sellers_by_trades)

# Save CSV summaries
top_buyers_by_amount.to_csv('top_buyers_by_amount.csv', header=['amount'])
top_buyers_by_quantity.to_csv('top_buyers_by_quantity.csv', header=['quantity'])
top_buyers_by_trades.to_csv('top_buyers_by_trades.csv', header=['trade_count'])

top_sellers_by_amount.to_csv('top_sellers_by_amount.csv', header=['amount'])
top_sellers_by_quantity.to_csv('top_sellers_by_quantity.csv', header=['quantity'])
top_sellers_by_trades.to_csv('top_sellers_by_trades.csv', header=['trade_count'])

print('\nCSV exports saved: top_buyers_*.csv and top_sellers_*.csv')

    