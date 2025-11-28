import sqlite3
import os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wildguard.db')
print('DB path:', DB)
if not os.path.exists(DB):
    print('Database not found')
else:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM alembic_version")
        rows = cur.fetchall()
        if not rows:
            print('alembic_version table empty')
        else:
            print('alembic_version rows:')
            for r in rows:
                print(r)
    except Exception as e:
        print('Error querying alembic_version:', e)
    conn.close()
