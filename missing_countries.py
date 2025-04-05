import sqlite3
import os

# List of countries from The Guardian article that need to be added
new_countries = [
    # Country name, reciprocal_tariff_rate
    ("Brazil", 10),
    ("Chile", 10),
    ("Australia", 10),
    ("Turkey", 10),
    ("Costa Rica", 10),
    ("Dominican Republic", 10),
    ("United Arab Emirates", 10),
    ("New Zealand", 10),
    ("Argentina", 10),
    ("Ecuador", 10),
    ("Guatemala", 10),
    ("Honduras", 10),
    ("Myanmar", 44),
    ("Egypt", 10),
    ("Saudi Arabia", 10),
    ("El Salvador", 10),
    ("Morocco", 10),
    ("Oman", 10),
    ("Uruguay", 10),
    ("Bahamas", 10),
    ("Ukraine", 10),
    ("Bahrain", 10),
    ("Qatar", 10),
    ("Iceland", 10),
    ("Kenya", 10),
    ("Haiti", 10),
    ("Ethiopia", 10),
    ("Ghana", 10),
    ("Jamaica", 10),
    ("Mozambique", 16),
    ("Paraguay", 10),
    ("Lebanon", 10),
    ("Tanzania", 10),
    ("Georgia", 10),
    ("Senegal", 10),
    ("Azerbaijan", 10),
    ("Uganda", 10),
    ("Panama", 10),
    ("Kuwait", 10),
    ("Peru", 10),
    ("Colombia", 10),
    ("Bolivia", 10),
    ("Belarus", 10),
    ("Cyprus", 10),
    ("Malta", 10),
    ("Luxembourg", 10),
    ("Slovenia", 10),
    ("Croatia", 10),
    ("Estonia", 10),
    ("Latvia", 10),
    ("Lithuania", 10),
    ("Slovakia", 10),
    ("Czech Republic", 10),
    ("Hungary", 10),
    ("Bulgaria", 10),
    ("Romania", 10),
    ("Greece", 10),
    ("Portugal", 10),
    ("Ireland", 10),
    ("Finland", 10),
    ("Denmark", 10),
    ("Sweden", 10),
    ("Austria", 10),
    ("Belgium", 10),
    ("Netherlands", 10),
    ("Spain", 10),
    ("Italy", 10),
    ("France", 10),
    ("Germany", 10),
    ("Mexico", 10),
    ("Canada", 10)
]

# Connect to the database
conn = sqlite3.connect('/home/ubuntu/tariff_project/database/tariff_tracker.db')
cursor = conn.cursor()

# Get existing countries to avoid duplicates
cursor.execute("SELECT name FROM countries")
existing_countries = [row[0] for row in cursor.fetchall()]
print(f"Found {len(existing_countries)} existing countries in the database")

# Add new countries that don't already exist
countries_added = 0
for country_name, tariff_rate in new_countries:
    if country_name not in existing_countries:
        # Calculate base_tariff_rate (always 10%)
        base_tariff_rate = 10.0
        
        # Insert the new country
        cursor.execute('''
            INSERT INTO countries (name, base_tariff_rate, reciprocal_tariff_rate, total_tariff_rate)
            VALUES (?, ?, ?, ?)
        ''', (country_name, base_tariff_rate, float(tariff_rate), base_tariff_rate + float(tariff_rate)))
        
        countries_added += 1
        print(f"Added {country_name} with tariff rate {tariff_rate}%")

# Commit changes
conn.commit()

# Verify the total count
cursor.execute("SELECT COUNT(*) FROM countries")
total_countries = cursor.fetchone()[0]

print(f"Added {countries_added} new countries to the database")
print(f"Total countries in database: {total_countries}")

# Close the connection
conn.close()
