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

# Total number of countries
c.execute("SELECT COUNT(*) FROM countries")
total = c.fetchone()[0]
print(f"\n Total Countries: {total}\n")

# Average Population by Region
print(" Average Population by Region:")
print(f"{'Region':<15} {'Countries':<10} {'% of Total':<12} {'Avg Population':<15}")
print("-" * 60)
for row in c.execute('''
    SELECT region, COUNT(*) as count, ROUND(AVG(population)) AS avg_pop
    FROM countries
    WHERE region != ''
    GROUP BY region
    ORDER BY avg_pop DESC
'''):
    region, count, avg_pop = row
    percent = (count / total) * 100
    print(f"{region:<15} {count:<10} {percent:>10.1f}% {avg_pop:>15,}")

# Region with most countries
row = c.execute('''
    SELECT region, COUNT(*) as count
    FROM countries
    WHERE region != ''
    GROUP BY region
    ORDER BY count DESC
    LIMIT 1
''').fetchone()
print(f"\n Region with Most Countries: {row[0]} ({row[1]} countries)")

# Top 10 Countries by Area
print("\n Top 10 Countries by Area:")
print(f"{'No.':<5} {'Country':<30} {'Area (km²)':>15} {'Population':>15}")
print("-" * 70)
for i, row in enumerate(c.execute('''
    SELECT name, population, area
    FROM countries
    WHERE area > 0
    ORDER BY area DESC
    LIMIT 10
'''), 1):
    print(f"{i:02d}. {row[0]:<30} {row[2]:>15,.0f} {row[1]:>15,}")

# Most densely populated countries
print("\n Top 5 Most Densely Populated Countries:")
print(f"{'No.':<5} {'Country':<30} {'Density (people/km²)':>25}")
print("-" * 65)
for i, row in enumerate(c.execute('''
    SELECT name, population, area, ROUND(population / area, 2) AS density
    FROM countries
    WHERE area > 0
    ORDER BY density DESC
    LIMIT 5
'''), 1):
    print(f"{i:02d}. {row[0]:<30} {row[3]:>25,.2f}")

# Largest country by area in each region
print("\n Largest Country by Area in Each Region:")
print(f"{'Region':<15} {'Country':<30} {'Area (km²)':>15}")
print("-" * 65)
for row in c.execute('''
    SELECT region, name, MAX(area)
    FROM countries
    WHERE region != ''
    GROUP BY region
'''):
    print(f"{row[0]:<15} {row[1]:<30} {row[2]:>15,.0f}")
