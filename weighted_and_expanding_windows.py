import pandas as pd
import numpy as np
import networkx as nx
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

#  LOAD CLEANED CSV
df = pd.read_csv("floorsheet_rolling_analysis.csv")
df['date'] = pd.to_datetime(df['date'])

# BROKER DOMINANCE
buy_df = df.groupby(['symbol','date','buyer'], as_index=False).agg(
    buy_qty=('quantity','sum'),
    buy_amount=('amount','sum')
).rename(columns={'buyer':'broker'})

sell_df = df.groupby(['symbol','date','seller'], as_index=False).agg(
    sell_qty=('quantity','sum'),
    sell_amount=('amount','sum')
).rename(columns={'seller':'broker'})

broker_df = pd.merge(buy_df, sell_df, on=['symbol','date','broker'], how='outer').fillna(0)
broker_df['net_amount'] = broker_df['buy_amount'] - broker_df['sell_amount']
turnover = df.groupby(['symbol','date'])['amount'].sum().reset_index(name='total_turnover')
broker_df = broker_df.merge(turnover, on=['symbol','date'], how='left')
broker_df['dominance_ratio'] = broker_df['net_amount'] / broker_df['total_turnover']
broker_df['dominant_flag'] = broker_df['dominance_ratio'].abs() > 0.25

# WEIGHTED ROLLING & EXPANDING PRICES
def rolling_weighted_avg(df_group, window=5):
    rates = df_group['rate'].to_numpy()
    qtys = df_group['quantity'].to_numpy()
    result = []
    for i in range(len(rates)):
        start = max(0, i-window+1)
        wavg = np.average(rates[start:i+1], weights=qtys[start:i+1])
        result.append(wavg)
    return pd.Series(result, index=df_group.index)

def expanding_weighted_avg(df_group):
    rates = df_group['rate'].to_numpy()
    qtys = df_group['quantity'].to_numpy()
    result = []
    for i in range(len(rates)):
        wavg = np.average(rates[:i+1], weights=qtys[:i+1])
        result.append(wavg)
    return pd.Series(result, index=df_group.index)

df['weighted_rolling_price'] = df.groupby('symbol').apply(rolling_weighted_avg).reset_index(level=0, drop=True)
df['weighted_expanding_price'] = df.groupby('symbol').apply(expanding_weighted_avg).reset_index(level=0, drop=True)

# Merge weighted prices into broker_df
weighted_prices = df.groupby(['symbol','date'])[['weighted_rolling_price','weighted_expanding_price']].mean().reset_index()
broker_df = broker_df.merge(weighted_prices, on=['symbol','date'], how='left')

#  MARKET PHASE
symbol_daily = df.groupby(['symbol','date'], as_index=False).agg(
    avg_price=('rate','mean'),
    total_qty=('quantity','sum')
)
symbol_daily['price_change'] = symbol_daily.groupby('symbol')['avg_price'].diff()
WINDOW = 5
symbol_daily['avg_volume'] = symbol_daily.groupby('symbol')['total_qty'].rolling(WINDOW,min_periods=1).mean().reset_index(level=0, drop=True)
symbol_daily['price_volatility'] = symbol_daily.groupby('symbol')['price_change'].rolling(WINDOW,min_periods=1).std().reset_index(level=0, drop=True)

def classify_phase(row):
    high_vol = row['total_qty'] > row['avg_volume'] * 1.3
    flat_price = abs(row['price_change']) < (row['price_volatility'] if row['price_volatility']>0 else 0.0001)
    if high_vol and flat_price:
        return 'Accumulation'
    elif high_vol and row['price_change']>0:
        return 'Markup'
    elif high_vol and row['price_change']<0:
        return 'Distribution'
    elif row['price_change']<0:
        return 'Markdown'
    else:
        return 'Neutral'
symbol_daily['market_phase'] = symbol_daily.apply(classify_phase, axis=1)

# COMBINE BROKER + PHASE
combined_df = broker_df.merge(symbol_daily[['symbol','date','market_phase','avg_price']], on=['symbol','date'], how='left')
combined_df['strong_accumulation'] = (combined_df['dominant_flag']) & (combined_df['market_phase']=='Accumulation')

# CIRCULAR TRADING FLAG
combined_df['circular_flag'] = False
for (symbol,date), day_df in df.groupby(['symbol','date']):
    G = nx.DiGraph()
    for _, row in day_df.iterrows():
        G.add_edge(row['buyer'], row['seller'])
    cycles = list(nx.simple_cycles(G))
    if cycles:
        brokers_in_cycles = set([b for cycle in cycles for b in cycle])
        mask = (combined_df['symbol']==symbol) & (combined_df['date']==date) & (combined_df['broker'].isin(brokers_in_cycles))
        combined_df.loc[mask,'circular_flag'] = True

# TRADE CLUSTER FLAG (DBSCAN)
combined_df['cluster_flag'] = False
for symbol, symbol_df in df.groupby('symbol'):
    if len(symbol_df)<2: continue
    X = symbol_df[['quantity','rate']].to_numpy()
    X_scaled = StandardScaler().fit_transform(X)
    db = DBSCAN(eps=0.5,min_samples=2).fit(X_scaled)
    
    symbol_df = symbol_df.copy()
    symbol_df['cluster'] = db.labels_
    
    clustered_brokers = symbol_df[symbol_df['cluster']!=-1]['buyer'].unique()
    mask = (combined_df['symbol']==symbol) & (combined_df['broker'].isin(clustered_brokers))
    combined_df.loc[mask,'cluster_flag'] = True

# SIGNAL SCORING
def broker_score(row):
    score=0
    if row['strong_accumulation']: score+=3
    if row['circular_flag']: score+=2
    if row['cluster_flag']: score+=2
    if row['dominance_ratio']>0.5: score+=1
    return score
combined_df['broker_score'] = combined_df.apply(broker_score, axis=1)

# Aggregate per symbol per day
daily_score = combined_df.groupby(['symbol','date'], as_index=False).agg(
    total_score=('broker_score','sum'),
    avg_dominance=('dominance_ratio','mean'),
    avg_price=('avg_price','mean'),
    weighted_rolling_price=('weighted_rolling_price','mean'),
    weighted_expanding_price=('weighted_expanding_price','mean')
)
# NEXT-DAY RETURN (BACKTEST)
daily_score['next_day_price'] = daily_score.groupby('symbol')['avg_price'].shift(-1)
daily_score['next_day_return'] = (daily_score['next_day_price'] - daily_score['avg_price']) / daily_score['avg_price']

# SAVE FINAL CSV
daily_score.to_csv("floorsheet_weighted_scoring_fixed.csv", index=False)
print("✅ Weighted rolling + expanding scoring saved as 'floorsheet_weighted_scoring_fixed.csv'")
