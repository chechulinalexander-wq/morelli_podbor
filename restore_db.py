import sqlite3

print("Creating new database...")
conn = sqlite3.connect("handles_restored.db")

print("Reading SQL dump...")
with open("handles_dump.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

print("Executing SQL...")
conn.executescript(sql_script)
conn.commit()

print("Verifying...")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM handles")
total = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM handles WHERE image_embedding IS NOT NULL AND image_embedding != \"\"")
emb = cursor.fetchone()[0]

print(f"Total records: {total}")
print(f"With embeddings: {emb}")

conn.close()
print("Done!")
