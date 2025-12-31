import pandas as pd

# Load data

df = pd.read_csv("floorsheet_cleaned.csv", dtype=str)

# Sort by serial number (execution order)
df = df.sort_values("sn").reset_index(drop=True)

# Detect new serial transaction
# df["new_serial"] = (
#     (df["symbol"] != df["symbol"].shift()) |
#     (df["buyer"]  != df["buyer"].shift()) |
#     (df["seller"] != df["seller"].shift())
# )

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
          seller=("seller", "first")
      )
      .reset_index()
)

# Keep only serials with trades >= 5
serial_5plus = serial_summary[serial_summary["trades"] >= 5]

# Keep only the detailed rows belonging to these serials
df_5plus = df.merge(
    serial_5plus[["symbol", "symbol_txn_no"]],
    on=["symbol", "symbol_txn_no"],
    how="inner"
)

# Save outputs
df_5plus.to_csv("floorsheet_serial_5plus3.csv", index=False)
serial_5plus.to_csv("serial_transactions_5plus2.csv", index=False)

print("✅ Serial transactions with trades >=5 processed successfully.")
