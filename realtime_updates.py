import sqlite3
import json
import os
import datetime
import time
import threading
import requests
import random

# Function to update stock prices with simulated real-time data
def update_stock_prices():
    conn = sqlite3.connect('/home/ubuntu/tariff_project/database/tariff_tracker.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all stocks
    stocks = cursor.execute('SELECT id, symbol FROM stocks').fetchall()
    
    for stock in stocks:
        stock_id = stock['id']
        symbol = stock['symbol']
        
        # Get the latest price for this stock
        latest_price = cursor.execute(
            'SELECT close_price FROM stock_prices WHERE stock_id = ? ORDER BY price_date DESC LIMIT 1',
            (stock_id,)
        ).fetchone()
        
        # If no price exists, generate a random starting price
        if latest_price is None:
            base_price = random.uniform(50, 500)
        else:
            base_price = latest_price['close_price']
        
        # Generate a small random price change (-2% to +1%)
        # More likely to be negative due to tariff impact
        change_pct = random.uniform(-2.0, 1.0)
        new_price = base_price * (1 + change_pct / 100)
        
        # Insert the new price
        today = datetime.date.today().isoformat()
        cursor.execute(
            'INSERT INTO stock_prices (stock_id, price_date, close_price) VALUES (?, ?, ?)',
            (stock_id, today, new_price)
        )
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Updated stock prices at {datetime.datetime.now()}")

# Function to update country responses with simulated new responses
def update_country_responses():
    conn = sqlite3.connect('/home/ubuntu/tariff_project/database/tariff_tracker.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get countries that don't have responses yet
    countries_without_responses = cursor.execute('''
        SELECT c.id, c.name 
        FROM countries c
        LEFT JOIN country_responses cr ON c.id = cr.country_id
        WHERE cr.id IS NULL
        LIMIT 3
    ''').fetchall()
    
    # Possible response types
    response_types = ['tariff', 'statement', 'negotiation', 'restriction', 'sanction']
    
    # Add random responses for some countries
    for country in countries_without_responses:
        if random.random() < 0.3:  # 30% chance to add a response
            country_id = country['id']
            country_name = country['name']
            response_type = random.choice(response_types)
            
            # Generate response description based on type
            if response_type == 'tariff':
                rate = random.randint(10, 30)
                description = f"{country_name} announced a {rate}% retaliatory tariff on selected US goods"
                response_rate = float(rate)
            elif response_type == 'statement':
                description = f"{country_name}'s trade minister expressed concern over US tariffs and called for negotiations"
                response_rate = None
            elif response_type == 'negotiation':
                description = f"{country_name} has initiated trade talks with the US to discuss tariff reductions"
                response_rate = None
            elif response_type == 'restriction':
                description = f"{country_name} announced new restrictions on US imports in response to tariffs"
                response_rate = None
            else:  # sanction
                description = f"{country_name} imposed sanctions on specific US companies in response to tariffs"
                response_rate = None
            
            # Generate dates
            announcement_date = datetime.date.today().isoformat()
            implementation_date = (datetime.date.today() + datetime.timedelta(days=random.randint(5, 30))).isoformat()
            
            # Insert the new response
            cursor.execute('''
                INSERT INTO country_responses 
                (country_id, response_type, response_description, response_rate, announcement_date, implementation_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (country_id, response_type, description, response_rate, announcement_date, implementation_date))
            
            print(f"Added new response for {country_name}")
    
    # Commit changes
    conn.commit()
    conn.close()

# Function to update tariff impacts based on new stock prices
def update_tariff_impacts():
    conn = sqlite3.connect('/home/ubuntu/tariff_project/database/tariff_tracker.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all stocks
    stocks = cursor.execute('SELECT id, symbol FROM stocks').fetchall()
    
    for stock in stocks:
        stock_id = stock['id']
        
        # Get the oldest and newest prices for this stock
        prices = cursor.execute('''
            SELECT close_price, price_date
            FROM stock_prices 
            WHERE stock_id = ? 
            ORDER BY price_date ASC
        ''', (stock_id,)).fetchall()
        
        if len(prices) >= 2:
            oldest_price = prices[0]['close_price']
            newest_price = prices[-1]['close_price']
            
            # Calculate price change percentage
            price_change_pct = ((newest_price - oldest_price) / oldest_price) * 100
            
            # Determine impact level
            if abs(price_change_pct) > 15:
                impact_level = "High"
            elif abs(price_change_pct) > 5:
                impact_level = "Medium"
            else:
                impact_level = "Low"
            
            # Update the tariff impact
            cursor.execute('''
                UPDATE tariff_impacts
                SET impact_level = ?, price_change_pct = ?, analysis_date = ?
                WHERE stock_id = ?
            ''', (impact_level, round(price_change_pct, 2), datetime.date.today().isoformat(), stock_id))
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Updated tariff impacts at {datetime.datetime.now()}")

# Function to simulate news articles about tariffs
def generate_news():
    conn = sqlite3.connect('/home/ubuntu/tariff_project/database/tariff_tracker.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get random country and stock
    country = cursor.execute('SELECT id, name FROM countries ORDER BY RANDOM() LIMIT 1').fetchone()
    stock = cursor.execute('SELECT id, symbol, company_name FROM stocks ORDER BY RANDOM() LIMIT 1').fetchone()
    
    if country and stock and random.random() < 0.5:  # 50% chance to generate news
        news_types = [
            f"{stock['company_name']} warns of profit impact from US-{country['name']} tariff dispute",
            f"Analysts downgrade {stock['symbol']} citing tariff concerns",
            f"{country['name']} consumers boycott {stock['company_name']} products amid trade tensions",
            f"{stock['company_name']} considers relocating production from {country['name']} due to tariffs",
            f"Trade group warns tariffs could cost {country['name']} economy billions",
            f"{stock['company_name']} CEO meets with {country['name']} officials to discuss tariff mitigation"
        ]
        
        title = random.choice(news_types)
        content = f"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        source = random.choice(["Reuters", "Bloomberg", "CNBC", "Financial Times", "Wall Street Journal"])
        publication_date = datetime.date.today().isoformat()
        
        # Insert the news
        cursor.execute('''
            INSERT INTO news 
            (title, content, source, publication_date, country_id, stock_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, source, publication_date, country['id'], stock['id']))
        
        print(f"Generated news: {title}")
    
    # Commit changes
    conn.commit()
    conn.close()

# Main update function to be run in a separate thread
def update_data_periodically():
    while True:
        try:
            # Update stock prices
            update_stock_prices()
            
            # Update country responses (less frequently)
            if random.random() < 0.3:  # 30% chance each cycle
                update_country_responses()
            
            # Update tariff impacts
            update_tariff_impacts()
            
            # Generate news
            generate_news()
            
            print("Data update complete")
            
            # Wait for next update cycle (between 30-60 seconds for demo purposes)
            time.sleep(random.randint(30, 60))
            
        except Exception as e:
            print(f"Error in update thread: {e}")
            time.sleep(60)  # Wait a minute before trying again

# Start the update thread when the module is imported
update_thread = threading.Thread(target=update_data_periodically, daemon=True)
update_thread.start()

print("Real-time update functionality initialized")
