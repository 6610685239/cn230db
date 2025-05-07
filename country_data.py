import requests
import sqlite3


url = "https://restcountries.com/v3.1/all"
response = requests.get(url)

if response.status_code != 200:
    print(f"ไม่สามารถเรียก API ได้ (HTTP {response.status_code})")
    exit(1)

try:
    countries = response.json()
except Exception as e:
    print("❌ JSON ไม่ถูกต้อง:", e)
    print(response.text)
    exit(1)


conn = sqlite3.connect("countries.db")
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS countries (
        name TEXT,
        population INTEGER,
        area REAL,
        region TEXT
    )
''')


for country in countries:
    name = country.get("name", {}).get("common", "Unknown")
    population = country.get("population", 0)
    area = country.get("area", 0)
    region = country.get("region", "Unknown")

    c.execute('''
        INSERT INTO countries (name, population, area, region)
        VALUES (?, ?, ?, ?)
    ''', (name, population, area, region))

conn.commit()


print("Average population By Region:")
for row in c.execute('''
    SELECT region, ROUND(AVG(population)) AS avg_population
    FROM countries
    GROUP BY region
    ORDER BY avg_population DESC
'''):
    print(f"- {row[0]}: {row[1]:,} คน")
print("")
print("5 Countries with most area:")
for row in c.execute('''
    SELECT name, area
    FROM countries
    ORDER BY area DESC
    LIMIT 5
'''):
    print(f"- {row[0]}: {row[1]:,.0f} ตร.กม.")

conn.close()
