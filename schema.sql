-- Database schema for Tariff Tracker application

-- Countries table to store information about affected countries
CREATE TABLE countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    base_tariff_rate REAL NOT NULL,  -- Base 10% tariff
    reciprocal_tariff_rate REAL NOT NULL,  -- Country-specific additional tariff
    total_tariff_rate REAL NOT NULL,  -- Total tariff rate (base + reciprocal)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Country responses table to store information about how countries respond to US tariffs
CREATE TABLE country_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id INTEGER NOT NULL,
    response_type TEXT NOT NULL,  -- 'tariff', 'restriction', 'sanction', 'negotiation', etc.
    response_description TEXT NOT NULL,
    response_rate REAL,  -- Tariff rate if applicable
    announcement_date DATE,
    implementation_date DATE,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- Stocks table to store information about affected stocks
CREATE TABLE stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    company_name TEXT NOT NULL,
    country_id INTEGER,
    sector TEXT,
    industry TEXT,
    stock_type TEXT NOT NULL,  -- 'US' or 'Foreign'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- Stock prices table to store historical and current stock prices
CREATE TABLE stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    price_date DATE NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL NOT NULL,
    volume INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

-- Tariff impacts table to store analysis of tariff impacts on stocks
CREATE TABLE tariff_impacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    impact_level TEXT NOT NULL,  -- 'High', 'Medium', 'Low', 'Unknown'
    price_change_pct REAL,
    impact_description TEXT,
    analysis_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

-- News table to store news articles related to tariffs and their impacts
CREATE TABLE news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    publication_date DATE NOT NULL,
    url TEXT,
    country_id INTEGER,
    stock_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

-- Create indexes for better query performance
CREATE INDEX idx_country_responses_country_id ON country_responses(country_id);
CREATE INDEX idx_stocks_country_id ON stocks(country_id);
CREATE INDEX idx_stock_prices_stock_id ON stock_prices(stock_id);
CREATE INDEX idx_stock_prices_date ON stock_prices(price_date);
CREATE INDEX idx_tariff_impacts_stock_id ON tariff_impacts(stock_id);
CREATE INDEX idx_news_country_id ON news(country_id);
CREATE INDEX idx_news_stock_id ON news(stock_id);
CREATE INDEX idx_news_date ON news(publication_date);
