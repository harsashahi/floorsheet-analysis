import pandas as pd

# Load your floorsheet
df = pd.read_csv("floorsheet_serial_5plus.csv", dtype=str)

# Convert numeric columns
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["rate"] = pd.to_numeric(df["rate"], errors="coerce")

# Remove date & time if present
df = df.drop(columns=["date", "time"], errors="ignore")

# Aggregate all trades per symbol
symbol_summary = (
    df.groupby("symbol")
      .agg(
          start_sn=("sn", "min"),
          end_sn=("sn", "max"),
          total_trades=("sn", "count"),
          total_qty=("quantity", "sum"),
          total_amount=("amount", "sum"),
          avg_rate=("rate", "mean")
      )
      .reset_index()
)

# Save result
symbol_summary.to_csv("symbol_summary.csv", index=False)

print("✅ Symbol-level aggregation completed successfully.")
