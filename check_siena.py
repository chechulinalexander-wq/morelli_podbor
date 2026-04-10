import sqlite3

conn = sqlite3.connect('handles_server.db')
cursor = conn.cursor()

# Find SIENA-2 handle
cursor.execute("""
    SELECT product_id, name, url, image_path, finish_color, style, color_group, series,
    CASE WHEN image_embedding IS NULL OR image_embedding = '' THEN 'EMPTY' ELSE 'EXISTS' END as embedding_status
    FROM handles
    WHERE name LIKE '%SIENA-2%' AND name LIKE '%матовое золото%'
""")

result = cursor.fetchone()
if result:
    print("Product ID:", result[0])
    print("Name:", result[1])
    print("URL:", result[2])
    print("Image Path:", result[3])
    print("Finish Color:", result[4])
    print("Style:", result[5])
    print("Color Group:", result[6])
    print("Series:", result[7])
    print("Embedding Status:", result[8])
else:
    print("Handle not found")

conn.close()
