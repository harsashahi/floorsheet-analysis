import pandas as pd
import networkx as nx
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np

# LOAD CLEANED CSV
df = pd.read_csv("floorsheet_rolling_analysis.csv")
df['date'] = pd.to_datetime(df['date'])

# BROKER DOMINANCE
# Buy side
buy_df = df.groupby(['symbol', 'date', 'buyer'], as_index=False).agg(
    buy_qty=('quantity', 'sum'),
    buy_amount=('amount', 'sum')
).rename(columns={'buyer': 'broker'})

# Sell side
sell_df = df.groupby(['symbol', 'date', 'seller'], as_index=False).agg(
    sell_qty=('quantity', 'sum'),
    sell_amount=('amount', 'sum')
).rename(columns={'seller': 'broker'})

# Merge buy & sell
broker_df = pd.merge(buy_df, sell_df, on=['symbol','date','broker'], how='outer').fillna(0)
broker_df['net_amount'] = broker_df['buy_amount'] - broker_df['sell_amount']

# Total turnover per symbol-date
turnover = df.groupby(['symbol','date'])['amount'].sum().reset_index(name='total_turnover')
broker_df = broker_df.merge(turnover, on=['symbol','date'], how='left')
broker_df['dominance_ratio'] = broker_df['net_amount'] / broker_df['total_turnover']
broker_df['dominant_flag'] = broker_df['dominance_ratio'].abs() > 0.25

#  MARKET PHASE
symbol_daily = df.groupby(['symbol','date'], as_index=False).agg(
    avg_price=('rate','mean'),
    total_qty=('quantity','sum'),
    total_amount=('amount','sum')
)
symbol_daily['price_change'] = symbol_daily.groupby('symbol')['avg_price'].diff()
symbol_daily['volume_change'] = symbol_daily.groupby('symbol')['total_qty'].diff()

WINDOW = 5
symbol_daily['avg_volume'] = symbol_daily.groupby('symbol')['total_qty']\
    .rolling(WINDOW, min_periods=1).mean().reset_index(level=0, drop=True)
symbol_daily['price_volatility'] = symbol_daily.groupby('symbol')['price_change']\
    .rolling(WINDOW, min_periods=1).std().reset_index(level=0, drop=True)

def classify_phase(row):
    high_volume = row['total_qty'] > row['avg_volume'] * 1.3
    flat_price = abs(row['price_change']) < (row['price_volatility'] if row['price_volatility']>0 else 0.0001)
    rising_price = row['price_change'] > 0
    falling_price = row['price_change'] < 0

    if high_volume and flat_price:
        return 'Accumulation'
    elif high_volume and rising_price:
        return 'Markup'
    elif high_volume and falling_price:
        return 'Distribution'
    elif falling_price:
        return 'Markdown'
    else:
        return 'Neutral'
symbol_daily['market_phase'] = symbol_daily.apply(classify_phase, axis=1)

# COMBINE BROKER DOMINANCE + PHASE
combined_df = broker_df.merge(
    symbol_daily[['symbol','date','market_phase']],
    on=['symbol','date'],
    how='left'
)
combined_df['strong_accumulation'] = (combined_df['dominant_flag']) & (combined_df['market_phase'] == 'Accumulation')

#  CIRCULAR TRADING FLAG
# Initialize flag
combined_df['circular_flag'] = False

for (symbol, date), day_df in df.groupby(['symbol','date']):
    G = nx.DiGraph()
    for _, row in day_df.iterrows():
        buyer = row['buyer']
        seller = row['seller']
        G.add_edge(buyer, seller)
    cycles = list(nx.simple_cycles(G))
    if cycles:
        brokers_in_cycles = set([b for cycle in cycles for b in cycle])
        mask = (combined_df['symbol']==symbol) & (combined_df['date']==date) & (combined_df['broker'].isin(brokers_in_cycles))
        combined_df.loc[mask, 'circular_flag'] = True

# TRADE CLUSTER FLAG (DBSCAN)
combined_df['cluster_flag'] = False

for symbol, symbol_df in df.groupby('symbol'):
    if len(symbol_df) < 2:
        continue
    X = symbol_df[['quantity','rate']].to_numpy()
    X_scaled = StandardScaler().fit_transform(X)
    db = DBSCAN(eps=0.5, min_samples=2).fit(X_scaled)
    symbol_df['cluster'] = db.labels_
    clustered_brokers = symbol_df[symbol_df['cluster']!=-1]['buyer'].unique()
    mask = (combined_df['symbol']==symbol) & (combined_df['broker'].isin(clustered_brokers))
    combined_df.loc[mask,'cluster_flag'] = True

#  SAVE FINAL MASTER CSV
combined_df.to_csv("master_floorsheet_analysis_all_flags.csv", index=False)
print("✅ Master floorsheet analysis with all flags saved as 'master_floorsheet_analysis_all_flags.csv'")
