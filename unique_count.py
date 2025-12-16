import pandas as pd

# Load floorsheet data
df = pd.read_csv("floorsheet_floorsheetdata_largenew.csv")

# Ensure date column is datetime
df['date'] = pd.to_datetime(df['date'])

# Calculate unique counts
unique_symbols = df['symbol'].nunique()
unique_dates = df['date'].dt.date.nunique()
unique_brokers = pd.concat([df['buyer'], df['seller']]).nunique()

# Display results
print("📊 Floorsheet Summary")
print("---------------------")
print(f"Unique Symbols  : {unique_symbols}")
print(f"Unique Dates    : {unique_dates}")
print(f"Unique Brokers  : {unique_brokers}")
