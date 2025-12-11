import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('floorsheet_floorsheetdata.csv')

print("=" * 80)
print("BEFORE CLEANING")
print("=" * 80)
print("\nData Types:")
print(df.dtypes)
print("\nSample Data:")
print(df.head(3))

# DATA CLEANING

# 1. Convert quantity to numeric (remove commas if any)
df['quantity'] = pd.to_numeric(df['quantity'].astype(str).str.replace(',', ''), errors='coerce')

# 2. Convert rate to numeric (remove commas if any)
df['rate'] = pd.to_numeric(df['rate'].astype(str).str.replace(',', ''), errors='coerce')

# 3. Convert amount to numeric (remove commas)
df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',', ''), errors='coerce')

# 4. Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# 5. Convert buyer and seller to numeric (they appear to be user IDs)
df['buyer'] = pd.to_numeric(df['buyer'], errors='coerce').astype('Int64')
df['seller'] = pd.to_numeric(df['seller'], errors='coerce').astype('Int64')

print("\n" + "=" * 80)
print("AFTER CLEANING")
print("=" * 80)
print("\nData Types:")
print(df.dtypes)
print("\nSample Data:")
print(df.head(3))


# DATA QUALITY CHECKS


print("\n" + "=" * 80)
print("DATA QUALITY CHECKS")
print("=" * 80)
print(f"\nMissing Values:\n{df.isnull().sum()}")

print("\n" + "=" * 80)
print("NUMERIC STATISTICS")
print("=" * 80)
print(df[['quantity', 'rate', 'amount']].describe())

print("\n" + "=" * 80)
print("DATE RANGE")
print("=" * 80)
print(f"From: {df['date'].min()}")
print(f"To: {df['date'].max()}")
print(f"Trading Days: {df['date'].nunique()}")


# SAVE CLEANED DATA


df.to_csv('floorsheet_floorsheetdata_cleaned.csv', index=False)
print("\n✓ Cleaned data saved to: floorsheet_floorsheetdata_cleaned.csv")
