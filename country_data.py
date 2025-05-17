import requests
import sqlite3


url = "https://restcountries.com/v3.1/all"
response = requests.get(url)

if response.status_code != 200:
    print(f"API ERROR (HTTP {response.status_code})")
    exit(1)

try:
    countries = response.json()
except Exception as e:
    print("Wrong JSON format:", e)
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


c.execute("DELETE FROM countries")


for country in countries:
    name = country.get("name", {}).get("common", "Unknown")
    population = country.get("population", 0)
    area = country.get("area", 0.0)
    region = country.get("region", "Unknown")

    c.execute('''
        INSERT INTO countries (name, population, area, region)
        VALUES (?, ?, ?, ?)
    ''', (name, population, area, region))

conn.commit()


print("\n COUNTRY DATA REPORT")
print("=" * 60)


c.execute("SELECT COUNT(*) FROM countries")
total = c.fetchone()[0]
print(f"\n Total Countries: {total}\n")


print(" Average Population by Region:")
for row in c.execute('''
    SELECT region, COUNT(*) as count, ROUND(AVG(population)) AS avg_pop
    FROM countries
    WHERE region != ''
    GROUP BY region
    ORDER BY avg_pop DESC
'''):
    region, count, avg_pop = row
    percent = (count / total) * 100
    print(f"- {region:<12} | {count} countries ({percent:.1f}%) | Avg Pop: {avg_pop:,}")


row = c.execute('''
    SELECT region, COUNT(*) as count
    FROM countries
    WHERE region != ''
    GROUP BY region
    ORDER BY count DESC
    LIMIT 1
''').fetchone()
print(f"\n Region with Most Countries: {row[0]} ({row[1]} countries)")


print("\n Top 10 Countries by Area:")
for i, row in enumerate(c.execute('''
    SELECT name, population, area
    FROM countries
    WHERE area > 0
    ORDER BY area DESC
    LIMIT 10
'''), 1):
    print(f"{i:02d}. {row[0]:<30} | Area: {row[2]:,.0f} km² | Pop: {row[1]:,}")


print("\n Top 5 Most Densely Populated Countries (People/km²):")
for i, row in enumerate(c.execute('''
    SELECT name, population, area, ROUND(population / area, 2) AS density
    FROM countries
    WHERE area > 0
    ORDER BY density DESC
    LIMIT 5
'''), 1):
    print(f"{i:02d}. {row[0]:<30} | Density: {row[3]:,.2f} people/km²")


print("\n Largest Country by Area in Each Region:")
for row in c.execute('''
    SELECT region, name, MAX(area)
    FROM countries
    WHERE region != ''
    GROUP BY region
'''):
    print(f"- {row[0]:<12} | {row[1]:<30} | Area: {row[2]:,.0f} km²")


conn.close()
