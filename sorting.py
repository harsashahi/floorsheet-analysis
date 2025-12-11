import pandas as pd

# -------------------------------
# 1. Load your CSV file
# -------------------------------
df = pd.read_csv("floorsheet_floorsheetdata.csv")

# -------------------------------
# 2. Convert date column (optional)
# -------------------------------
# If your date is in format 2024-01-01 or similar
try:
    df["date"] = pd.to_datetime(df["date"])
except:
    pass   # ignore if date is not clean

# -------------------------------
# 3. Sort the data
# -------------------------------
# Choose ONE option below by uncommenting (remove #)

# Sort by amount (highest first)
sorted_df = df.sort_values("amount", ascending=False)

# Sort by quantity (highest first)
# sorted_df = df.sort_values("quantity", ascending=False)

# Sort by symbol (A → Z)
sorted_df = df.sort_values("symbol", ascending=True)

# Sort by date (oldest first)
# sorted_df = df.sort_values("date", ascending=True)

# Sort by multiple columns: symbol A→Z, quantity high→low
# sorted_df = df.sort_values(["symbol", "quantity"], ascending=[True, False])

# -------------------------------
# 4. Print sorted output
# -------------------------------
print("\n===== Sorted Data =====\n")
print(sorted_df)

# -------------------------------
# 5. Save to new CSV
# -------------------------------
sorted_df.to_csv("sorted_output.csv", index=False)

print("\nSorting complete! Saved as sorted_output.csv")
