import pandas as pd

# Load cleaned data
df = pd.read_csv("floorsheet_floorsheetdata_cleaned.csv")
df['date'] = pd.to_datetime(df['date'])

#  Daily aggregation per symbol
daily = (
    df.groupby(['symbol', 'date'])
    .agg(
        today_avg_rate=('rate', 'mean'),
        today_volume=('quantity', 'sum')
    )
    .reset_index()
    .sort_values(['symbol', 'date'])
)
#  Last 5-day rolling calculations
daily['avg_rate_5d'] = (
    daily.groupby('symbol')['today_avg_rate']
    .rolling(5)
    .mean()
    .reset_index(level=0, drop=True)
)

daily['avg_volume_5d'] = (
    daily.groupby('symbol')['today_volume']
    .rolling(5)
    .mean()
    .reset_index(level=0, drop=True)
)

# 4Change & spike metrics
daily['rate_change_pct'] = (
    (daily['today_avg_rate'] - daily['avg_rate_5d']) / daily['avg_rate_5d'] * 100
)

daily['volume_multiplier'] = (
    daily['today_volume'] / daily['avg_volume_5d']
)

# Flags
daily['volume_spike'] = daily['volume_multiplier'] >= 2
daily['rate_change_lt_5pct'] = daily['rate_change_pct'].abs() < 5

#  Final clean table
final_table = daily[[
    'symbol',
    'date',
    'today_avg_rate',
    'avg_rate_5d',
    'rate_change_pct',
    'today_volume',
    'avg_volume_5d',
    'volume_multiplier',
    'volume_spike',
    'rate_change_lt_5pct'
]].dropna()

# Round for readability
final_table = final_table.round({
    'today_avg_rate': 2,
    'avg_rate_5d': 2,
    'rate_change_pct': 2,
    'avg_volume_5d': 0,
    'volume_multiplier': 2
})

#  Retrieve different cases
# a) All volume spikes
volume_spikes = final_table[final_table['volume_spike'] == True]

# b) Low rate change (<5%)
low_change = final_table[final_table['rate_change_lt_5pct'] == True]

# c) Low rate change + volume spike
low_change_spike = final_table[
    (final_table['rate_change_lt_5pct'] == True) &
    (final_table['volume_spike'] == True)
]

#  Save CSVs
final_table.to_csv("rolling_window_analysis.csv", index=False)
volume_spikes.to_csv("volume_spike_only.csv", index=False)
low_change.to_csv("rate_change_less_than_5pct.csv", index=False)
low_change_spike.to_csv("low_change_high_volume_spike.csv", index=False)

# Print tables

print("\n📊 FULL ROLLING WINDOW TABLE\n")
print(final_table.to_string(index=False))

print("\n🚨 VOLUME SPIKES\n")
print(volume_spikes.to_string(index=False))

print("\n📉 RATE CHANGE < 5%\n")
print(low_change.to_string(index=False))

print("\n⚡ LOW PRICE CHANGE + HIGH VOLUME SPIKE\n")
print(low_change_spike.to_string(index=False))
