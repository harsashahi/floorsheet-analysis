import pandas as pd
import numpy as np
from datetime import timedelta

# Load cleaned data if available
try:
    df = pd.read_csv('floorsheet_floorsheetdata_cleaned.csv', parse_dates=['date'])
except FileNotFoundError:
    df = pd.read_csv('floorsheet_floorsheetdata.csv')
    df['quantity'] = pd.to_numeric(df['quantity'].astype(str).str.replace(',', ''), errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',', ''), errors='coerce')
    df['rate'] = pd.to_numeric(df['rate'].astype(str).str.replace(',', ''), errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Aggregate daily totals
daily = df.groupby('date').agg(total_quantity=('quantity', 'sum'), total_amount=('amount', 'sum')).reset_index()
if daily.empty:
    raise SystemExit('No daily data available to forecast')

daily = daily.sort_values('date')

print('Historical daily data:')
print(daily.to_string(index=False))

# Forecast horizon
horizon = 7

# Helper: simple forecasts
results = []

# If we have less than 2 days, only return last value
if len(daily) < 2:
    last_q = daily['total_quantity'].iloc[-1]
    last_a = daily['total_amount'].iloc[-1]
    print('\nToo few days for trend-based forecasting. Using last-value forecast.')
    for i in range(1, horizon+1):
        results.append({'date': daily['date'].iloc[-1] + timedelta(days=i), 'forecast_quantity': last_q, 'forecast_amount': last_a, 'method': 'last_value'})
else:
    # Dates to numeric (day index)
    x = np.arange(len(daily))
    q = daily['total_quantity'].values
    a = daily['total_amount'].values

    # Linear regression (degree 1)
    coef_q = np.polyfit(x, q, 1)
    coef_a = np.polyfit(x, a, 1)

    # Moving average (window=3)
    ma_q = daily['total_quantity'].rolling(window=3, min_periods=1).mean().iloc[-1]
    ma_a = daily['total_amount'].rolling(window=3, min_periods=1).mean().iloc[-1]

    last_date = daily['date'].iloc[-1]
    for i in range(1, horizon+1):
        xi = len(daily) - 1 + i
        # Linear forecast
        lin_q = np.polyval(coef_q, xi)
        lin_a = np.polyval(coef_a, xi)
        # Combine: average of linear and moving average (simple ensemble)
        forecast_q = float((lin_q + ma_q) / 2)
        forecast_a = float((lin_a + ma_a) / 2)
        results.append({'date': last_date + timedelta(days=i), 'forecast_quantity': max(0, round(forecast_q)), 'forecast_amount': max(0.0, round(forecast_a, 2)), 'method': 'linear+ma'})

# Save forecast results
fc_df = pd.DataFrame(results)
fc_df.to_csv('daily_volume_forecast.csv', index=False)
print('\nForecast for next', horizon, 'days:')
print(fc_df.to_string(index=False))
print('\nSaved CSV: daily_volume_forecast.csv')

# Save combined historical + forecast for convenience
hist = daily.rename(columns={'total_quantity':'historical_quantity','total_amount':'historical_amount'})
combined = pd.concat([hist[['date','historical_quantity','historical_amount']], fc_df.rename(columns={'forecast_quantity':'historical_quantity','forecast_amount':'historical_amount'})], ignore_index=True)
combined.to_csv('daily_volume_history_and_forecast.csv', index=False)
print('Saved CSV: daily_volume_history_and_forecast.csv')
