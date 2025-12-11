# Save this as dashboard.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# -----------------------------
# 1. Load CSV
# -----------------------------
df = pd.read_csv("floorsheet_floorsheetdata.csv")

# -----------------------------
# 2. Convert numeric columns
# -----------------------------
numeric_cols = ["quantity", "amount", "rate", "transaction_no"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

# -----------------------------
# 3. Convert date column
# -----------------------------
df['date'] = pd.to_datetime(df['date'])

# -----------------------------
# 4. Create report folder
# -----------------------------
report_folder = "static_report"
os.makedirs(report_folder, exist_ok=True)

# -----------------------------
# 5. Stock-wise total traded amount
# -----------------------------
stock_summary = df.groupby("symbol")["amount"].sum().sort_values(ascending=False)
plt.figure(figsize=(10,6))
sns.barplot(x=stock_summary.index, y=stock_summary.values, color="steelblue")
plt.xticks(rotation=90)
plt.title("Total Traded Amount per Stock")
plt.ylabel("Amount")
plt.xlabel("Stock Symbol")
plt.tight_layout()
plt.savefig(f"{report_folder}/stock_traded_amount.png")
plt.close()

# -----------------------------
# 6. Daily turnover
# -----------------------------
daily_turnover = df.groupby(df['date'].dt.date)["amount"].sum()
plt.figure(figsize=(10,5))
sns.lineplot(x=daily_turnover.index, y=daily_turnover.values, marker="o")
plt.xticks(rotation=45)
plt.title("Daily Market Turnover")
plt.ylabel("Total Amount")
plt.xlabel("Date")
plt.tight_layout()
plt.savefig(f"{report_folder}/daily_turnover.png")
plt.close()

# -----------------------------
# 7. Top 10 traders by amount
# -----------------------------
trader_summary = df.groupby("buyer")["amount"].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(10,5))
sns.barplot(x=trader_summary.index, y=trader_summary.values, color="coral")
plt.xticks(rotation=45)
plt.title("Top 10 Buyers by Amount")
plt.ylabel("Total Amount")
plt.xlabel("Trader")
plt.tight_layout()
plt.savefig(f"{report_folder}/top10_traders.png")
plt.close()

# -----------------------------
# 8. Correlation heatmap
# -----------------------------
plt.figure(figsize=(6,5))
corr = df[numeric_cols].corr(numeric_only=True)
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Matrix")
plt.tight_layout()
plt.savefig(f"{report_folder}/correlation_matrix.png")
plt.close()

# -----------------------------
# 9. Save summary CSVs
# -----------------------------
stock_summary.to_csv(f"{report_folder}/stock_summary.csv")
daily_turnover.to_csv(f"{report_folder}/daily_turnover.csv")
trader_summary.to_csv(f"{report_folder}/top10_traders.csv")

print(f"Static report generated in folder '{report_folder}'")
print("Charts and CSVs saved successfully.")
