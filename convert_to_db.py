import json
import sqlite3

# Load JSON data
with open('products.json', encoding='utf-8') as f:
    products = json.load(f)

# Connect to SQLite
conn = sqlite3.connect('handles.db')
cursor = conn.cursor()

# Drop existing table if needed
cursor.execute('DROP TABLE IF EXISTS handles')

# Create table
cursor.execute('''
CREATE TABLE handles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT UNIQUE,
    name TEXT,
    type TEXT,
    material TEXT,
    rose_shape TEXT,
    description TEXT,
    url TEXT,
    created_at TEXT
)
''')

# Insert data
for product in products:
    cursor.execute('''
        INSERT INTO handles (product_id, name, type, material, rose_shape, description, url, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        product.get('product_id'),
        product.get('name'),
        product.get('type'),
        product.get('material'),
        product.get('rose_shape'),
        product.get('description'),
        product.get('url'),
        product.get('created_at')
    ))

conn.commit()
conn.close()

print(f'Successfully converted {len(products)} products to handles.db')
