import pandas as pd


#  Load your CSV file
df = pd.read_csv("floorsheet_floorsheetdata.csv")


# If your date is in format 2024-01-01 or similar
try:
    df["date"] = pd.to_datetime(df["date"])
except:
    pass   

# Sort by amount (highest first)
sorted_df = df.sort_values("amount", ascending=False)


# Sort by symbol (A → Z)
sorted_df = df.sort_values("symbol", ascending=True)

#  Print sorted output
print("\n===== Sorted Data =====\n")
print(sorted_df)


# Save to new CSV
sorted_df.to_csv("sorted_output.csv", index=False)

print("\nSorting complete! Saved as sorted_output.csv")
