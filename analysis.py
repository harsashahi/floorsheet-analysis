import pandas as pd

# Load the dataset
df = pd.read_csv('floorsheet_floorsheetdata.csv')

print("=" * 80)
print("1. FIRST 5 ROWS OF DATA")
print("=" * 80)
print(df.head())

print("\n" + "=" * 80)
print("2. DATASET SHAPE AND INFO")
print("=" * 80)
print(f"Total Rows: {df.shape[0]}")
print(f"Total Columns: {df.shape[1]}")
print(f"\nColumn Names and Data Types:")
print(df.dtypes)

print("\n" + "=" * 80)
print("3. MISSING VALUES CHECK")
print("=" * 80)
print(df.isnull().sum())

print("\n" + "=" * 80)
print("4. STATISTICAL SUMMARY")
print("=" * 80)
print(df.describe())

print("\n" + "=" * 80)
print("5. UNIQUE VALUES COUNT")
print("=" * 80)
print(f"Unique Stocks: {df['symbol'].nunique()}")
print(f"Unique Buyers: {df['buyer'].nunique()}")
print(f"Unique Sellers: {df['seller'].nunique()}")
print(f"Unique Dates: {df['date'].nunique()}")

print("\n" + "=" * 80)
print("6. SAMPLE OF DIFFERENT STOCKS")
print("=" * 80)
print(f"First 10 Stock Symbols: {df['symbol'].unique()[:10]}")
