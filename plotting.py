import pandas as pd
import matplotlib.pyplot as plt
import os


# 1. Load CSV

df = pd.read_csv("floorsheet_floorsheetdata.csv")

# 2. Clean numeric columns
numeric_cols = ["quantity", "amount", "rate"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')


# 3. Convert date column

df['date'] = pd.to_datetime(df['date'])


# 4. Create report folder

report_folder = "report"
os.makedirs(report_folder, exist_ok=True)


# 5. Stock-wise total traded amount (Bar Plot)

stock_summary = df.groupby("symbol")["amount"].sum().sort_values(ascending=False)
plt.figure(figsize=(10,6))
stock_summary.plot(kind='bar', color='steelblue', title='Total Traded Amount per Stock')
plt.xlabel("Stock Symbol")
plt.ylabel("Amount")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(f"{report_folder}/stock_traded_amount.png")
plt.close()

# 6. Daily turnover (Line Plot)
daily_turnover = df.groupby(df['date'].dt.date)["amount"].sum()
plt.figure(figsize=(10,5))
daily_turnover.plot(kind='line', marker='o', title='Daily Market Turnover')
plt.xlabel("Date")
plt.ylabel("Total Amount")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{report_folder}/daily_turnover.png")
plt.close()


# 7. Top 10 traders by amount (Horizontal Bar Plot)

top_traders = df.groupby("buyer")["amount"].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(10,6))
top_traders.plot(kind='barh', color='coral', title='Top 10 Buyers by Amount')
plt.xlabel("Total Amount")
plt.ylabel("Trader")
plt.tight_layout()
plt.savefig(f"{report_folder}/top10_traders.png")
plt.close()


# 8. Quantity vs Amount (Scatter Plot)

plt.figure(figsize=(8,6))
df.plot(kind='scatter', x='quantity', y='amount', alpha=0.5, title='Quantity vs Amount')
plt.tight_layout()
plt.savefig(f"{report_folder}/quantity_vs_amount.png")
plt.close()


# 9. Rate Distribution (Histogram)
plt.figure(figsize=(8,6))
df['rate'].plot(kind='hist', bins=30, color='green', title='Rate Distribution')
plt.xlabel("Rate")
plt.tight_layout()
plt.savefig(f"{report_folder}/rate_distribution.png")
plt.close()

print(f"All plots saved in folder '{report_folder}'")
