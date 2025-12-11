import pandas as pd

# 1. Load CSV
df = pd.read_csv("floorsheet_floorsheetdata.csv")

# 2. Convert numeric columns (remove commas and convert to float)
numeric_cols = ["quantity", "amount", "rate"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

# 3. Group by stock symbol
stock_analysis = df.groupby("symbol").agg({
    "quantity": "sum",
    "amount": "sum",
    "rate": "mean",
    "transaction_no": "count"
}).reset_index()

stock_analysis.columns = ["symbol", "total_quantity", "total_amount", "avg_rate", "num_trades"]

# 4. Sort by total_amount descending (optional)
stock_analysis = stock_analysis.sort_values("total_amount", ascending=False)

# 5. Print stock-wise trading activity
print("\n===== Stock-wise Trading Activity =====\n")
print(stock_analysis)

# 6. Save to CSV
stock_analysis.to_csv("stock_trading_activity.csv", index=False)
print("\nStock-wise trading activity saved to 'stock_trading_activity.csv'")
