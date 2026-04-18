import json
import sqlite3

# 1. Load the JSON data
with open('baustellen_sperrungen_viz.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

features = data.get('features', [])
print(f"Found {len(features)} construction records to process.")

# 2. Connect to the database
conn = sqlite3.connect('berlin_infrastructure.db')
cursor = conn.cursor()

# 3. Create the Table (The SQL Schema)
# We use IF NOT EXISTS so we can run this script multiple times safely
cursor.execute('''
CREATE TABLE IF NOT EXISTS construction_sites (
    id TEXT PRIMARY KEY,
    subtype TEXT,
    severity TEXT,
    direction TEXT,
    street TEXT,
    section TEXT,
    content TEXT,
    validity_from TEXT,
    validity_to TEXT,
    longitude REAL,
    latitude REAL
)
''')

# 4. Insert the data
# We loop through every feature, extract the flat values, and insert them
inserted_count = 0

for feature in features:
    props = feature.get('properties', {})
    geom = feature.get('geometry', {})
    
    # Safely extract validity dates
    validity = props.get('validity', {})
    validity_from = validity.get('from')
    validity_to = validity.get('to')
    
    # Safely extract the first Point coordinate for lat/lon
    lon, lat = None, None
    if geom.get('type') == 'GeometryCollection':
        for g in geom.get('geometries', []):
            if g.get('type') == 'Point':
                lon = g['coordinates'][0]
                lat = g['coordinates'][1]
                break # Just grab the first point we find

    # The SQL INSERT command
    # We use INSERT OR REPLACE so if we run the script twice, it updates rather than crashing
    cursor.execute('''
    INSERT OR REPLACE INTO construction_sites 
    (id, subtype, severity, direction, street, section, content, validity_from, validity_to, longitude, latitude)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        props.get('id'),
        props.get('subtype'),
        props.get('severity'),
        props.get('direction'),
        props.get('street'),
        props.get('section'),
        props.get('content'),
        validity_from,
        validity_to,
        lon,
        lat
    ))
    inserted_count += 1

# 5. Save (commit) the changes and close
conn.commit()
conn.close()

print(f"Successfully inserted {inserted_count} records into the SQLite database!")