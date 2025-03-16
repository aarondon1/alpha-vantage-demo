import requests
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries
from statsmodels.tsa.ar_model import AutoReg
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variables
api_key = os.getenv("API_KEY")

# # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
# url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=5min&apikey={api_key}'
# r = requests.get(url)
# data = r.json()
# print(data)

# Using the Alpha Vantage API to get the historical data for SPY
ts = TimeSeries(key=api_key, output_format='pandas')
# Using 'full' to get the entire historical set. 'compact' would only get the last 100 data points.
spy_data, meta_data = ts.get_daily(symbol='SPY', outputsize='full')


# 'spy_data' is a pandas dataframe with columns
# [1. open', '2. high', '3. low', '4. close', '5. volume']
# since the data is in descending orfder we use sort_index to sort it in ascending order
spy_data = spy_data.sort_index()

st.title("S&P 500 (SPY) Analysis using Alpha Vantage")
st.title("")
st.title("")
st.write("This simple app fetches SPY historical data from the Alpha Vantage API, allows you to \
         select a date range, and shows both a Moving Average and an AutoRegressive (AR) model.")


#-----------------------------------------------------------------------------------
# Select date range (slider)
#-----------------------------------------------------------------------------------
# Convert index to a DatetimeIndex for easier filtering
spy_data.index = pd.to_datetime(spy_data.index)

# extract year range for the slider
min_year = spy_data.index.year.min()
max_year = spy_data.index.year.max()

# Slider for selecting the start and end year
start_year, end_year = st.slider(
    "Select the start and end year:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter the DataFrame by the selected years
filtered_data = spy_data.loc[
    (spy_data.index.year >= start_year) &
    (spy_data.index.year <= end_year)
]

# Just to confirm how many data points we have now:
st.write(f"Data points in selected date range: {len(filtered_data)}")

#-----------------------------------------------------------------------------------
# Display the raw data or a quick preview
#-----------------------------------------------------------------------------------
st.subheader("Preview of Selected Data")
st.write(filtered_data.head())  # Show first few rows

#-----------------------------------------------------------------------------------
# Plot the closing price of SPY within the selected date range
#-----------------------------------------------------------------------------------
st.subheader("SPY Closing Prices Over Selected Date Range")

fig, ax = plt.subplots()
ax.plot(filtered_data.index, filtered_data['4. close'], label='Close Price')
ax.set_xlabel("Date")
ax.set_ylabel("Price (USD)")
ax.set_title("SPY Closing Price")
ax.legend()

# Display the plot using Streamlit 
st.pyplot(fig)

#-----------------------------------------------------------------------------------
# Moving Average Calculation & Visualization
#-----------------------------------------------------------------------------------
st.subheader("Moving Average of Closing Prices")

# slider to select window size for the Moving Average
window_size = st.slider("Select the Moving Average window size (days):", 5, 100, 20)

# Calculate Moving Average on the '4. close' column
filtered_data['MA'] = filtered_data['4. close'].rolling(window=window_size).mean()

fig2, ax2 = plt.subplots()
ax2.plot(filtered_data.index, filtered_data['4. close'], label='Close Price')
ax2.plot(filtered_data.index, filtered_data['MA'], label=f'{window_size}-day MA')
ax2.set_xlabel("Date")
ax2.set_ylabel("Price (USD)")
ax2.set_title(f"SPY Closing Price with {window_size}-day Moving Average")
ax2.legend()

st.pyplot(fig2)

#-----------------------------------------------------------------------------------
# AutoRegressive (AR) Model Fitting & Visualization
#-----------------------------------------------------------------------------------
st.subheader("AutoRegressive (AR) Model on SPY Closing Prices")

# We'll do a simple AR model to forecast the next N days
# For demonstration, let's pick how many lags we want:
lag = st.slider("Select the number of lags for AR model:", 1, 30, 5)
forecast_days = st.slider("Select how many days to forecast:", 1, 30, 5)

# Make sure we drop NaNs (from the MA step if it was included)
ar_data = filtered_data['4. close'].dropna()

# Fit the AR model on the closing price
model = AutoReg(ar_data, lags=lag, old_names=False)
model_fit = model.fit()

# Forecast the next 'forecast_days'
predictions = model_fit.predict(start=len(ar_data), end=len(ar_data) + forecast_days - 1)

# Create a combined series with actual + forecast
all_dates = pd.date_range(start=ar_data.index[-1], periods=forecast_days+1, freq='D')[1:]
# 'ar_data.index[-1]' is the last date in the training set
# the next day after that is all_dates[0], etc.

forecast_series = pd.Series(predictions.values, index=all_dates)

# Plot the actual data and the forecast
fig3, ax3 = plt.subplots()
ax3.plot(ar_data.index, ar_data, label='Historical Close')
ax3.plot(forecast_series.index, forecast_series, label='AR Forecast')
ax3.set_xlabel("Date")
ax3.set_ylabel("Price (USD)")
ax3.set_title("AR Model Forecast")
ax3.legend()

st.pyplot(fig3)


# Explanation of Each Step
st.markdown("""
### Explanation of each section of the code:

1. **Load Environment Variables**  
   We use `load_dotenv()` to read in our `.env` file and retrieve our Alpha Vantage `API_KEY`.

2. **Alpha Vantage API Setup**  
   We use the Python wrapper `alpha_vantage.timeseries.TimeSeries` to query daily stock data for SPY.

3. **Data Sorting and Filtering**  
   The returned DataFrame is sorted in descending order by default. We sort it in ascending order for convenience.
   Then we convert the index to actual DateTime objects, which makes filtering and plotting simpler and easier.

4. **Streamlit Layout**  
   - We set the page title(s) with `st.title()`.
   - We show a brief description with `st.write()` or `st.markdown()`.

5. **Date Range Slider**  
   We extract the min and max year from our data and create a slider to let the user choose a start and end year. We then filter the DataFrame to only those years.

6. **Data Preview**  
   We show a small preview of the filtered DataFrame using `st.write(filtered_data.head())`.

7. **Initial Plot**  
   We use `matplotlib.pyplot` to plot the closing prices (`4. close`) over the filtered date range, and display it with `st.pyplot()`.

8. **Moving Average**  
   We add a user-selected window size slider and compute a rolling mean (`rolling(window=...).mean()`). We plot both the original closing price and the moving average on the same figure.

9. **AutoRegressive Model**  
   - We allow the user to choose the number of lags (`lag`) and the number of days to forecast. 
   - We fit an AR model on our filtered data with `AutoReg`.
   - We generate predictions for the next few days and plot them alongside the historical data.

10. **Final Visualization**  
    Each figure is displayed with a separate `plt.subplots()` and `st.pyplot()` call. Streamlit automatically renders the figure.

""")







