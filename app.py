from flask import Flask, render_template, jsonify
import sqlite3
import datetime
import os
import threading
import time

# Import the real-time update functionality
import realtime_updates

app = Flask(__name__)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('/home/ubuntu/tariff_project/database/tariff_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/countries')
def get_countries():
    conn = get_db_connection()
    countries = conn.execute('SELECT * FROM countries ORDER BY total_tariff_rate DESC').fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in countries])

@app.route('/api/country_responses')
def get_country_responses():
    conn = get_db_connection()
    responses = conn.execute('''
        SELECT cr.*, c.name as country_name 
        FROM country_responses cr
        JOIN countries c ON cr.country_id = c.id
        ORDER BY cr.implementation_date DESC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in responses])

@app.route('/api/affected_stocks')
def get_affected_stocks():
    conn = get_db_connection()
    stocks = conn.execute('''
        SELECT s.*, ti.impact_level, ti.price_change_pct, c.name as country_name
        FROM stocks s
        LEFT JOIN countries c ON s.country_id = c.id
        JOIN tariff_impacts ti ON s.id = ti.stock_id
        ORDER BY ti.price_change_pct ASC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in stocks])

@app.route('/api/us_stocks')
def get_us_stocks():
    conn = get_db_connection()
    stocks = conn.execute('''
        SELECT s.*, ti.impact_level, ti.price_change_pct
        FROM stocks s
        JOIN tariff_impacts ti ON s.id = ti.stock_id
        WHERE s.stock_type = 'US'
        ORDER BY ti.price_change_pct ASC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in stocks])

@app.route('/api/foreign_stocks')
def get_foreign_stocks():
    conn = get_db_connection()
    stocks = conn.execute('''
        SELECT s.*, ti.impact_level, ti.price_change_pct, c.name as country_name
        FROM stocks s
        LEFT JOIN countries c ON s.country_id = c.id
        JOIN tariff_impacts ti ON s.id = ti.stock_id
        WHERE s.stock_type = 'Foreign'
        ORDER BY ti.price_change_pct ASC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in stocks])

@app.route('/api/tariff_summary')
def get_tariff_summary():
    conn = get_db_connection()
    
    # Get summary statistics
    summary = {}
    
    # Count of countries with tariffs
    country_count = conn.execute('SELECT COUNT(*) as count FROM countries').fetchone()['count']
    summary['country_count'] = country_count
    
    # Average tariff rate
    avg_tariff = conn.execute('SELECT AVG(total_tariff_rate) as avg FROM countries').fetchone()['avg']
    summary['average_tariff_rate'] = round(avg_tariff, 2)
    
    # Count of country responses
    response_count = conn.execute('SELECT COUNT(*) as count FROM country_responses').fetchone()['count']
    summary['response_count'] = response_count
    
    # Count of affected stocks
    stock_count = conn.execute('SELECT COUNT(*) as count FROM stocks').fetchone()['count']
    summary['affected_stock_count'] = stock_count
    
    # Average stock price change
    avg_price_change = conn.execute('SELECT AVG(price_change_pct) as avg FROM tariff_impacts').fetchone()['avg']
    summary['average_price_change'] = round(avg_price_change, 2)
    
    # Latest news
    latest_news = conn.execute('''
        SELECT n.title, n.source, n.publication_date, c.name as country_name, s.symbol
        FROM news n
        LEFT JOIN countries c ON n.country_id = c.id
        LEFT JOIN stocks s ON n.stock_id = s.id
        ORDER BY n.publication_date DESC
        LIMIT 5
    ''').fetchall()
    
    if latest_news:
        summary['latest_news'] = [dict(news) for news in latest_news]
    else:
        summary['latest_news'] = []
    
    conn.close()
    
    return jsonify(summary)

@app.route('/api/news')
def get_news():
    conn = get_db_connection()
    news = conn.execute('''
        SELECT n.*, c.name as country_name, s.symbol, s.company_name
        FROM news n
        LEFT JOIN countries c ON n.country_id = c.id
        LEFT JOIN stocks s ON n.stock_id = s.id
        ORDER BY n.publication_date DESC
        LIMIT 20
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(item) for item in news])

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Start the real-time update thread
    print("Starting real-time update thread...")
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
