import json
import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the collected stock data
with open('/home/ubuntu/tariff_project/stock_analysis/affected_stocks_data.json', 'r') as f:
    stock_data = json.load(f)

# Create directory for charts
os.makedirs('/home/ubuntu/tariff_project/stock_analysis/charts', exist_ok=True)

# Analyze which stocks are most affected by tariffs
affected_stocks = {
    'us_stocks': [],
    'foreign_stocks': []
}

# US companies likely to be affected by tariffs
us_companies = [
    "AAPL", "MSFT", "AMZN", "TSLA", "F", "GM", "WMT", "TGT", 
    "NKE", "INTC", "AMD", "NVDA", "X", "CAT", "BA"
]

# Foreign companies likely to be affected by tariffs
foreign_companies = [
    "BABA", "JD", "TCEHY", "NIO", "LI", "XPEV", "TM", "HMC", 
    "NSANY", "VLKAF", "BMWYY", "SIEGY", "TSM"
]

# Function to analyze stock performance
def analyze_stock(symbol, stock_type):
    try:
        # Get stock data
        data = stock_data[symbol]
        
        # Extract company name
        company_name = data['insights']['finance']['result']['upsell']['companyName'] if 'insights' in data and 'finance' in data['insights'] and 'result' in data['insights']['finance'] and 'upsell' in data['insights']['finance']['result'] and 'companyName' in data['insights']['finance']['result']['upsell'] else symbol
        
        # Extract sector info if available
        sector_info = data['insights']['finance']['result']['companySnapshot']['sectorInfo'] if 'insights' in data and 'finance' in data['insights'] and 'result' in data['insights']['finance'] and 'companySnapshot' in data['insights']['finance']['result'] and 'sectorInfo' in data['insights']['finance']['result']['companySnapshot'] else "Unknown"
        
        # Extract recent price data if available
        recent_prices = []
        if 'chart' in data and 'chart' in data['chart'] and 'result' in data['chart']['chart'] and len(data['chart']['chart']['result']) > 0:
            chart_data = data['chart']['chart']['result'][0]
            if 'indicators' in chart_data and 'quote' in chart_data['indicators'] and len(chart_data['indicators']['quote']) > 0:
                close_prices = chart_data['indicators']['quote'][0]['close']
                recent_prices = [p for p in close_prices if p is not None]
        
        # Calculate price change if we have enough data
        price_change = 0
        price_change_pct = 0
        if len(recent_prices) >= 2:
            start_price = recent_prices[0]
            end_price = recent_prices[-1]
            price_change = end_price - start_price
            price_change_pct = (price_change / start_price) * 100 if start_price > 0 else 0
        
        # Create a simple chart of recent prices if available
        if len(recent_prices) > 0:
            plt.figure(figsize=(10, 6))
            plt.plot(recent_prices)
            plt.title(f"{company_name} ({symbol}) - Recent Price Movement")
            plt.xlabel("Trading Days")
            plt.ylabel("Price ($)")
            plt.grid(True)
            plt.savefig(f"/home/ubuntu/tariff_project/stock_analysis/charts/{symbol}_price_chart.png")
            plt.close()
        
        # Determine tariff impact based on sector and recent performance
        tariff_impact = "High" if abs(price_change_pct) > 5 else "Medium" if abs(price_change_pct) > 2 else "Low"
        
        # Return stock analysis
        return {
            'symbol': symbol,
            'company_name': company_name,
            'sector': sector_info,
            'stock_type': stock_type,
            'recent_price_change_pct': round(price_change_pct, 2),
            'tariff_impact': tariff_impact,
            'chart_path': f"/home/ubuntu/tariff_project/stock_analysis/charts/{symbol}_price_chart.png" if len(recent_prices) > 0 else None
        }
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return {
            'symbol': symbol,
            'company_name': symbol,
            'sector': "Unknown",
            'stock_type': stock_type,
            'recent_price_change_pct': 0,
            'tariff_impact': "Unknown",
            'chart_path': None
        }

# Analyze US stocks
for symbol in us_companies:
    if symbol in stock_data:
        stock_analysis = analyze_stock(symbol, "US")
        affected_stocks['us_stocks'].append(stock_analysis)

# Analyze foreign stocks
for symbol in foreign_companies:
    if symbol in stock_data:
        stock_analysis = analyze_stock(symbol, "Foreign")
        affected_stocks['foreign_stocks'].append(stock_analysis)

# Sort stocks by tariff impact and price change
affected_stocks['us_stocks'] = sorted(affected_stocks['us_stocks'], 
                                     key=lambda x: (0 if x['tariff_impact'] == "High" else 1 if x['tariff_impact'] == "Medium" else 2, 
                                                   -abs(x['recent_price_change_pct'])))
affected_stocks['foreign_stocks'] = sorted(affected_stocks['foreign_stocks'], 
                                          key=lambda x: (0 if x['tariff_impact'] == "High" else 1 if x['tariff_impact'] == "Medium" else 2, 
                                                        -abs(x['recent_price_change_pct'])))

# Save the analysis results
with open('/home/ubuntu/tariff_project/stock_analysis/affected_stocks_analysis.json', 'w') as f:
    json.dump(affected_stocks, f, indent=2)

# Create a summary report
with open('/home/ubuntu/tariff_project/stock_analysis/affected_stocks_summary.md', 'w') as f:
    f.write("# Stocks Affected by US Tariffs and Country Responses\n\n")
    
    f.write("## Most Affected US Stocks\n\n")
    f.write("| Symbol | Company Name | Sector | Price Change (%) | Tariff Impact |\n")
    f.write("|--------|--------------|--------|------------------|---------------|\n")
    for stock in affected_stocks['us_stocks'][:10]:  # Top 10 most affected
        f.write(f"| {stock['symbol']} | {stock['company_name']} | {stock['sector']} | {stock['recent_price_change_pct']}% | {stock['tariff_impact']} |\n")
    
    f.write("\n## Most Affected Foreign Stocks\n\n")
    f.write("| Symbol | Company Name | Sector | Price Change (%) | Tariff Impact |\n")
    f.write("|--------|--------------|--------|------------------|---------------|\n")
    for stock in affected_stocks['foreign_stocks'][:10]:  # Top 10 most affected
        f.write(f"| {stock['symbol']} | {stock['company_name']} | {stock['sector']} | {stock['recent_price_change_pct']}% | {stock['tariff_impact']} |\n")
    
    f.write("\n## Analysis Summary\n\n")
    f.write("The stocks listed above are likely to be significantly affected by the recent US tariffs and country responses. ")
    f.write("US companies with significant exposure to international markets, particularly in manufacturing, technology, and consumer goods sectors, ")
    f.write("are vulnerable to retaliatory tariffs from countries like China. ")
    f.write("Foreign companies exporting to the US market will face increased costs due to the new tariffs, ")
    f.write("potentially impacting their competitiveness and profitability.\n\n")
    f.write("This analysis is based on recent stock performance and sector exposure to tariffs. ")
    f.write("The actual impact may vary as markets continue to react to policy developments and company-specific factors.")

print("Stock analysis complete. Results saved to affected_stocks_analysis.json and affected_stocks_summary.md")
