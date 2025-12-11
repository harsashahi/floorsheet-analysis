import pandas as pd


# 1. Load CSV file

df = pd.read_csv("floorsheet_floorsheetdata.csv")


# 2. Convert date column to datetime

df['date'] = pd.to_datetime(df['date'])

# 3. Calculate daily turnover
daily_turnover = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
daily_turnover.columns = ['date', 'daily_turnover']


# 4. Print daily turnover

print("\n===== Daily Turnover =====\n")
print(daily_turnover)

# 5. Save to CSV


daily_turnover.to_csv("daily_turnover.csv", index=False)
print("\nDaily turnover saved to 'daily_turnover.csv'")
