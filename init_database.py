import sqlite3
import json
import os
import datetime

# Create database connection
conn = sqlite3.connect('/home/ubuntu/tariff_project/database/tariff_tracker.db')
cursor = conn.cursor()

# Execute schema SQL to create tables
with open('/home/ubuntu/tariff_project/database/schema.sql', 'r') as f:
    schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()

print("Database tables created successfully")

# Load tariff data
with open('/home/ubuntu/tariff_project/us_tariffs_data.md', 'r') as f:
    tariff_data = f.read()

# Load country responses data
with open('/home/ubuntu/tariff_project/country_responses.md', 'r') as f:
    country_responses_data = f.read()

# Load stock analysis data
with open('/home/ubuntu/tariff_project/stock_analysis/affected_stocks_analysis.json', 'r') as f:
    stock_analysis = json.load(f)

# Parse and insert country data
print("Inserting country data...")
countries = {}

# Extract country data from tariff_data markdown
import re
country_pattern = r'\| ([^|]+) \| (\d+)% \|'
country_matches = re.findall(country_pattern, tariff_data)

for country_name, tariff_rate in country_matches:
    country_name = country_name.strip()
    tariff_rate = float(tariff_rate)
    base_tariff = 10.0  # Base tariff rate is 10%
    total_tariff = base_tariff + tariff_rate
    
    cursor.execute('''
        INSERT INTO countries (name, base_tariff_rate, reciprocal_tariff_rate, total_tariff_rate)
        VALUES (?, ?, ?, ?)
    ''', (country_name, base_tariff, tariff_rate, total_tariff))
    
    # Store country ID for later reference
    country_id = cursor.lastrowid
    countries[country_name] = country_id

conn.commit()
print(f"Inserted {len(countries)} countries")

# Parse and insert country responses
print("Inserting country responses...")
response_count = 0

# China's response
if 'China' in countries:
    cursor.execute('''
        INSERT INTO country_responses 
        (country_id, response_type, response_description, response_rate, announcement_date, implementation_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        countries['China'], 
        'tariff', 
        'China announced a 34% retaliatory tariff on all US goods', 
        34.0, 
        '2025-04-04', 
        '2025-04-10'
    ))
    response_count += 1

# EU's response
if 'European Union' in countries:
    cursor.execute('''
        INSERT INTO country_responses 
        (country_id, response_type, response_description, announcement_date)
        VALUES (?, ?, ?, ?)
    ''', (
        countries['European Union'], 
        'negotiation', 
        'EU trade chief Maros Sefcovic stated the EU would act in "a calm, carefully phased, unified way" and allow time for talks', 
        '2025-04-04'
    ))
    response_count += 1

# Vietnam's response
if 'Vietnam' in countries:
    cursor.execute('''
        INSERT INTO country_responses 
        (country_id, response_type, response_description, announcement_date)
        VALUES (?, ?, ?, ?)
    ''', (
        countries['Vietnam'], 
        'statement', 
        'Vietnam\'s top trade official called Trump\'s new 46% tariff "unfair"', 
        '2025-04-04'
    ))
    response_count += 1

conn.commit()
print(f"Inserted {response_count} country responses")

# Insert stock data
print("Inserting stock data...")
stock_count = 0

# Process US stocks
for stock in stock_analysis['us_stocks']:
    symbol = stock['symbol']
    company_name = stock['company_name']
    sector = stock['sector']
    stock_type = stock['stock_type']
    
    cursor.execute('''
        INSERT INTO stocks (symbol, company_name, sector, stock_type)
        VALUES (?, ?, ?, ?)
    ''', (symbol, company_name, sector, stock_type))
    
    stock_id = cursor.lastrowid
    stock_count += 1
    
    # Insert tariff impact
    cursor.execute('''
        INSERT INTO tariff_impacts 
        (stock_id, impact_level, price_change_pct, analysis_date)
        VALUES (?, ?, ?, ?)
    ''', (
        stock_id, 
        stock['tariff_impact'], 
        stock['recent_price_change_pct'], 
        datetime.date.today().isoformat()
    ))

# Process foreign stocks
for stock in stock_analysis['foreign_stocks']:
    symbol = stock['symbol']
    company_name = stock['company_name']
    sector = stock['sector']
    stock_type = stock['stock_type']
    
    # Try to determine country for foreign stocks
    country_id = None
    if 'BABA' in symbol or 'JD' in symbol:
        country_id = countries.get('China')
    elif 'TM' in symbol or 'HMC' in symbol:
        country_id = countries.get('Japan')
    elif 'TSM' in symbol:
        country_id = countries.get('Taiwan')
    
    cursor.execute('''
        INSERT INTO stocks (symbol, company_name, sector, stock_type, country_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (symbol, company_name, sector, stock_type, country_id))
    
    stock_id = cursor.lastrowid
    stock_count += 1
    
    # Insert tariff impact
    cursor.execute('''
        INSERT INTO tariff_impacts 
        (stock_id, impact_level, price_change_pct, analysis_date)
        VALUES (?, ?, ?, ?)
    ''', (
        stock_id, 
        stock['tariff_impact'], 
        stock['recent_price_change_pct'], 
        datetime.date.today().isoformat()
    ))

conn.commit()
print(f"Inserted {stock_count} stocks with tariff impact data")

# Close the database connection
conn.close()
print("Database initialization complete")
