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

# --- DROP THE OLD TABLE ---
# We delete the old table so we can build the new one with the District column
cursor.execute('DROP TABLE IF EXISTS construction_sites')

# 3. Create the Table (Now with 'district')
cursor.execute('''
CREATE TABLE construction_sites (
    id TEXT PRIMARY KEY,
    subtype TEXT,
    severity TEXT,
    direction TEXT,
    street TEXT,
    district TEXT,  -- <-- NEW COLUMN ADDED HERE
    section TEXT,
    content TEXT,
    validity_from TEXT,
    validity_to TEXT,
    longitude REAL,
    latitude REAL
)
''')

# 4. Insert the data
inserted_count = 0

for feature in features:
    props = feature.get('properties', {})
    geom = feature.get('geometry', {})
    
    # --- DATA CLEANING: EXTRACT THE DISTRICT ---
    raw_street = props.get('street', '')
    district_name = None
    clean_street = raw_street
    
    # If there are brackets in the street name...
    if raw_street and '(' in raw_street and ')' in raw_street:
        # Split by '(' and grab the second half, then split by ')' and grab the first half
        # e.g. "Wolfensteindamm (Steglitz)" -> "Steglitz"
        district_name = raw_street.split('(')[1].split(')')[0].strip()
        
        # We also clean up the street name so it just says "Wolfensteindamm"
        clean_street = raw_street.split('(')[0].strip()

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
                break 

    # The SQL INSERT command
    cursor.execute('''
    INSERT INTO construction_sites 
    (id, subtype, severity, direction, street, district, section, content, validity_from, validity_to, longitude, latitude)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        props.get('id'),
        props.get('subtype'),
        props.get('severity'),
        props.get('direction'),
        clean_street,
        district_name, # <-- INJECTING THE DISTRICT
        props.get('section'),
        props.get('content'),
        validity_from,
        validity_to,
        lon,
        lat
    ))
    inserted_count += 1

# 5. Save and close
conn.commit()
conn.close()

print(f"Successfully rebuilt the database with {inserted_count} records and a dedicated District column!")