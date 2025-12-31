import pandas as pd

# Load data
df = pd.read_csv("floorsheet_12_28_2025.csv", dtype=str)

# Sort by serial number
df = df.sort_values("sn").reset_index(drop=True)

# Detect new serial transaction
df["new_serial"] = (
    (df["symbol"] != df["symbol"].shift()) |
    (df["buyer"]  != df["buyer"].shift()) |
    (df["seller"] != df["seller"].shift())
)

# Serial transaction numbers
df["symbol_txn_no"] = df.groupby("symbol")["new_serial"].cumsum()
df["global_txn_no"] = df["new_serial"].cumsum()

# Convert numeric columns
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["rate"] = pd.to_numeric(df["rate"], errors="coerce")

# Remove date & time columns
df = df.drop(columns=["date", "time"], errors="ignore")

# Aggregate serial transactions
serial_summary = (
    df.groupby(["symbol", "symbol_txn_no"])
      .agg(
          start_sn=("sn", "min"),
          end_sn=("sn", "max"),
          trades=("sn", "count"),
          total_qty=("quantity", "sum"),
          total_amount=("amount", "sum"),
          avg_rate=("rate", "mean"),
          buyer=("buyer", "first"),
          seller=("seller", "first"),
      )
      .reset_index()
)

# Save outputs
df.to_csv("floorsheet_with_serial_txn.csv", index=False)
serial_summary.to_csv("serial_transaction_summary.csv", index=False)

print("✅ Date & time removed. Serial transaction files created.")
