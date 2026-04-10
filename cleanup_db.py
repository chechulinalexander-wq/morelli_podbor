import sqlite3

conn = sqlite3.connect('handles_server.db')
cursor = conn.cursor()

# Check total before
cursor.execute('SELECT COUNT(*) FROM handles')
total_before = cursor.fetchone()[0]
print(f'Total records before: {total_before}')

# Delete rows with empty embeddings
cursor.execute('''
    DELETE FROM handles
    WHERE image_embedding IS NULL OR image_embedding = ''
''')

deleted = cursor.rowcount
print(f'Deleted rows with empty embeddings: {deleted}')

# Check total after
cursor.execute('SELECT COUNT(*) FROM handles')
total_after = cursor.fetchone()[0]
print(f'Total records after: {total_after}')

conn.commit()
conn.close()
