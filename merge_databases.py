import sqlite3

# Connect to both databases
conn_server = sqlite3.connect('handles_server.db')
conn_new = sqlite3.connect('handles_new.db')

cursor_server = conn_server.cursor()
cursor_new = conn_new.cursor()

# Get existing names from server db
cursor_server.execute('SELECT name FROM handles')
existing_names = set(row[0] for row in cursor_server.fetchall())
print(f'Existing records in server db: {len(existing_names)}')

# Get all records from new db
cursor_new.execute('SELECT product_id, name, type, material, rose_shape, description, url, created_at FROM handles')
new_records = cursor_new.fetchall()
print(f'Total records in new db: {len(new_records)}')

# Filter records that don't exist in server db
records_to_add = [record for record in new_records if record[1] not in existing_names]
print(f'Records to add: {len(records_to_add)}')

# Insert new records
for record in records_to_add:
    cursor_server.execute('''
        INSERT INTO handles (product_id, name, type, material, rose_shape, description, url, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', record)

conn_server.commit()

# Verify
cursor_server.execute('SELECT COUNT(*) FROM handles')
total_after = cursor_server.fetchone()[0]
print(f'Total records after merge: {total_after}')

conn_server.close()
conn_new.close()

print('Merge completed successfully!')
