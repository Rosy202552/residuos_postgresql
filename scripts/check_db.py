import os
import sqlite3

p = os.path.join('instance', 'app.db')
print('DB path:', p)
print('Exists:', os.path.exists(p))
if not os.path.exists(p):
    raise SystemExit('DB file not found')

conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print('Tables:', tables)

if any(t[0] == 'denuncia' for t in tables):
    cur.execute("PRAGMA table_info('denuncia')")
    schema = cur.fetchall()
    print('denuncia schema:')
    for row in schema:
        print(row)
else:
    print('Table `denuncia` not found')

conn.close()
