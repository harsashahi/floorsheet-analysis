import pandas as pd
import matplotlib.pyplot as plt

# 1. Load CSV
df = pd.read_csv("floorsheet_floorsheetdata_cleaned.csv")

# 2. Convert numeric columns (remove commas, convert to float)
numeric_cols = ["quantity", "amount", "rate", "transaction_no", "id"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

# 3. Correlation matrix for all numeric columns
corr = df.corr(numeric_only=True)
print("\n===== Correlation Matrix =====\n")
print(corr)

# 4. Correlation between quantity and amount
if "quantity" in df.columns and "amount" in df.columns:
    print("\nCorrelation between quantity and amount:\n")
    print(df[["quantity", "amount"]].corr())

# 5. Heatmap (optional)
plt.figure(figsize=(8,6))
plt.imshow(corr, cmap='coolwarm', interpolation='nearest')
plt.colorbar()
plt.title("Correlation Heatmap")
plt.xticks(range(len(corr)), corr.columns, rotation=90)
plt.yticks(range(len(corr)), corr.columns)
plt.tight_layout()
plt.show()

