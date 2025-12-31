import pandas as pd

# Load CSV
df = pd.read_csv("floorsheet_serial_sn.csv", dtype=str)

# Drop unnecessary columns
for col in ["date", "time", "start_sn", "end_sn", "symbol_txn_no"]:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

# Convert numeric columns
for col in ["quantity", "rate", "amount"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Sort by sn to preserve order
df = df.sort_values(["symbol", "sn"]).reset_index(drop=True)

# Assign serial_sn per transaction block (all consecutive rows of same symbol share same serial)
df["serial_sn"] = (df["symbol"] != df["symbol"].shift(1)).cumsum()

# Save CSV
df.to_csv("floorsheet_serial_sn_only.csv", index=False)

print("✅ Done. Only serial_sn column kept for transaction blocks per symbol.")
print(df.head(20))
