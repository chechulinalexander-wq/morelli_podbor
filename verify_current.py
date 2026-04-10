import sqlite3

conn = sqlite3.connect("handles.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM handles")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM handles WHERE image_embedding IS NOT NULL AND image_embedding != \"\"")
emb = cursor.fetchone()[0]

cursor.execute("SELECT product_id, name FROM handles LIMIT 3")
samples = cursor.fetchall()

print(f"Total records: {total}")
print(f"With embeddings: {emb}")
print(f"\nSample records:")
for pid, name in samples:
    print(f"  {pid}: {name[:60]}")

conn.close()
