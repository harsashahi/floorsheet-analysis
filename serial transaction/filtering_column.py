import pandas as pd

# Load CSV
df = pd.read_csv("floorsheet_with_serial_txn.csv", dtype=str)

# Drop the unwanted columns
for col in ["new_serial", "global_txn_no"]:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

# Save the cleaned CSV
df.to_csv("floorsheet_cleaned.csv", index=False)

print("✅ Done. Removed new_serial and global_txn_no.")
print(df.head(20))
