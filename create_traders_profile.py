import pandas as pd

# 1. Load CSV
df = pd.read_csv("floorsheet_floorsheetdata.csv")

# 2. Convert numeric columns
for col in ["quantity", "amount", "rate", "transaction_no"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

# 3. Buyer profiles
buyer_stats = df.groupby("buyer").agg({
    "quantity": "sum",
    "amount": "sum",
    "rate": "mean",
    "transaction_no": "count"
}).reset_index()
buyer_stats.columns = ["trader", "total_buy_qty", "total_buy_amount", "avg_buy_rate", "buy_trades"]

# 4. Seller profiles
seller_stats = df.groupby("seller").agg({
    "quantity": "sum",
    "amount": "sum",
    "rate": "mean",
    "transaction_no": "count"
}).reset_index()
seller_stats.columns = ["trader", "total_sell_qty", "total_sell_amount", "avg_sell_rate", "sell_trades"]

# 5. Merge buyer and seller stats
trader_profiles = pd.merge(buyer_stats, seller_stats, on="trader", how="outer").fillna(0)

# 6. Activity level (example classification)
conditions = [
    (trader_profiles["total_buy_amount"] + trader_profiles["total_sell_amount"] > 1_000_000),
    (trader_profiles["total_buy_amount"] + trader_profiles["total_sell_amount"] > 500_000)
]
choices = ["High", "Medium"]
trader_profiles["activity_level"] = pd.Series(pd.cut(
    trader_profiles["total_buy_amount"] + trader_profiles["total_sell_amount"],
    bins=[-1, 500_000, 1_000_000, float('inf')],
    labels=["Low", "Medium", "High"]
))

# 7. Most traded symbols per trader (optional)
most_traded = df.melt(id_vars=["transaction_no", "date"], value_vars=["buyer", "seller"], var_name="type", value_name="trader")
most_traded_symbols = df.groupby("buyer")["symbol"].apply(lambda x: x.mode()[0] if not x.mode().empty else "").reset_index()
most_traded_symbols.columns = ["trader", "most_traded_symbol"]

# Merge symbols
trader_profiles = pd.merge(trader_profiles, most_traded_symbols, on="trader", how="left")

# 8. Print sample profiles
print("\n===== Trader Profiles =====\n")
print(trader_profiles.head())

# 9. Save to CSV
trader_profiles.to_csv("trader_profiles.csv", index=False)
print("\nTrader profiles saved to 'trader_profiles.csv'")
