import requests
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variables
api_key = os.getenv("API_KEY")

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey={api_key}'
r = requests.get(url)
data = r.json()

#print(data)
 
# Extracting data for IBM
ts = TimeSeries(key=api_key, output_format="pandas")

# Fetch intraday data for IBM
data, meta_data = ts.get_intraday(symbol="IBM", interval="5min", outputsize="full")

# Print the data
print(data.head())
