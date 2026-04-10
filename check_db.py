import sqlite3

conn = sqlite3.connect("handles_new.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM handles")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM handles WHERE image_embedding IS NOT NULL AND image_embedding != \"\"")
emb = cursor.fetchone()[0]

print(f"Total: {total}")
print(f"With embeddings: {emb}")

conn.close()
