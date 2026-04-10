import sqlite3

conn = sqlite3.connect('handles_server.db')

with open('handles_dump.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(f'{line}\n')

conn.close()
print("SQL dump created: handles_dump.sql")
