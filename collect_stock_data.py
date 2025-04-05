import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json

# Initialize API client
client = ApiClient()

# List of sectors and industries likely to be affected by tariffs
affected_sectors = [
    "Automotive", "Technology", "Consumer Goods", "Manufacturing", 
    "Semiconductors", "Retail", "Steel", "Electronics"
]

# List of major US companies likely to be affected by tariffs
us_companies = [
    "AAPL", "MSFT", "AMZN", "TSLA", "F", "GM", "WMT", "TGT", 
    "NKE", "INTC", "AMD", "NVDA", "X", "CAT", "BA"
]

# List of major foreign companies likely to be affected by tariffs
foreign_companies = [
    "BABA", "JD", "TCEHY", "NIO", "LI", "XPEV", "TM", "HMC", 
    "NSANY", "VLKAF", "BMWYY", "SIEGY", "TSM"
]

# Combine all companies
all_companies = us_companies + foreign_companies

# Get stock data for each company
results = {}

for symbol in all_companies:
    try:
        # Get stock insights
        insights = client.call_api('YahooFinance/get_stock_insights', query={'symbol': symbol})
        
        # Get recent stock chart data
        chart = client.call_api('YahooFinance/get_stock_chart', 
                               query={'symbol': symbol, 'interval': '1d', 'range': '1mo'})
        
        # Get insider holdings
        holders = client.call_api('YahooFinance/get_stock_holders', query={'symbol': symbol})
        
        # Store results
        results[symbol] = {
            'insights': insights,
            'chart': chart,
            'holders': holders
        }
        
        print(f"Successfully retrieved data for {symbol}")
    except Exception as e:
        print(f"Error retrieving data for {symbol}: {e}")

# Save results to file
with open('/home/ubuntu/tariff_project/stock_analysis/affected_stocks_data.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Data collection complete. Results saved to affected_stocks_data.json")
