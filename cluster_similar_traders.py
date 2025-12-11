import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# 1. Load CSV
df = pd.read_csv("floorsheet_floorsheetdata.csv")

# 2. Convert columns to numeric
numeric_cols = ["quantity", "amount", "rate", "transaction_no"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

# 3. Create buyer features
buyer_stats = df.groupby("buyer").agg({
    "quantity": "sum",
    "amount": "sum",
    "rate": "mean",
    "transaction_no": "count"
}).reset_index()
buyer_stats.columns = ["trader", "buy_qty", "buy_amount", "avg_buy_rate", "buy_trades"]

# 4. Create seller features
seller_stats = df.groupby("seller").agg({
    "quantity": "sum",
    "amount": "sum",
    "rate": "mean",
    "transaction_no": "count"
}).reset_index()
seller_stats.columns = ["trader", "sell_qty", "sell_amount", "avg_sell_rate", "sell_trades"]

# 5. Merge buyer + seller
trader_data = pd.merge(buyer_stats, seller_stats, on="trader", how="outer").fillna(0)

# 6. Select features
features = trader_data[[
    "buy_qty", "sell_qty",
    "buy_amount", "sell_amount",
    "avg_buy_rate", "avg_sell_rate",
    "buy_trades", "sell_trades"
]]

# 7. Normalize
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# 8. K-Means clustering
k = 3
kmeans = KMeans(n_clusters=k, random_state=42)
trader_data['cluster'] = kmeans.fit_predict(scaled_features)

# 9. Show results
print("\n===== Trader Clusters =====\n")
print(trader_data[['trader', 'cluster']])

# 10. Save to CSV
trader_data.to_csv("clustered_traders.csv", index=False)
print("\nClustered traders saved to 'clustered_traders.csv'")
