"""
Add `camera_id` column to the detections table if it doesn't exist.

Usage:
    python scripts/add_camera_id_column.py [path/to/wildguard.db]

This is intended as a local/dev quick fix. It will:
- back up the DB to <db>.bak
- check whether `camera_id` exists
- run ALTER TABLE to add the column as TEXT NULLABLE if missing
"""
import sqlite3
import sys
import os
import shutil


def backup_db(db_path):
    bak = db_path + '.pre_add_camera_id.bak'
    shutil.copy2(db_path, bak)
    print(f'Backed up DB to {bak}')


def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table});")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols


def add_column(db_path):
    if not os.path.exists(db_path):
        print(f'Error: DB file not found: {db_path}')
        return 1

    backup_db(db_path)

    conn = sqlite3.connect(db_path)
    try:
        if column_exists(conn, 'detections', 'camera_id'):
            print('camera_id column already exists; no action taken')
            return 0

        print('Adding camera_id column to detections table...')
        conn.execute('ALTER TABLE detections ADD COLUMN camera_id VARCHAR(50);')
        conn.commit()
        print('camera_id column added successfully')
        return 0
    except Exception as e:
        print('Error while adding column:', e)
        return 2
    finally:
        conn.close()


if __name__ == '__main__':
    db = sys.argv[1] if len(sys.argv) > 1 else os.path.join('instance', 'wildguard.db')
    sys.exit(add_column(db))
