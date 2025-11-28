"""
Utility to fix Alembic's recorded revision in the local SQLite DB.

This script will:
- back up the SQLite file specified (default: `instance/wildguard.db`)
- create or update the `alembic_version` table to contain the provided revision (default: `0001_initial`)

Usage:
    python scripts/fix_alembic_version.py [path/to/wildguard.db] [revision]

Example:
    python scripts/fix_alembic_version.py instance/wildguard.db 0001_initial

Note: This performs a direct DB write. Make sure you have a backup or
are comfortable overwriting the alembic version state for local/dev data.
"""
import sys
import os
import shutil
import sqlite3


def backup_db(db_path):
    if not os.path.exists(db_path):
        print(f"DB file not found: {db_path}")
        return False
    bak_path = db_path + '.bak'
    shutil.copy2(db_path, bak_path)
    print(f"Backed up DB to: {bak_path}")
    return True


def ensure_alembic_version(db_path, revision='0001_initial'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alembic_version (
            version_num VARCHAR(32) NOT NULL
        );
    """)

    # Check if a row exists
    cur.execute("SELECT count(*) FROM alembic_version;")
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute("INSERT INTO alembic_version (version_num) VALUES (?);", (revision,))
        print(f"Inserted alembic_version = {revision}")
    else:
        cur.execute("UPDATE alembic_version SET version_num = ?;", (revision,))
        print(f"Updated alembic_version -> {revision}")

    conn.commit()
    conn.close()


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join('instance', 'wildguard.db')
    revision = sys.argv[2] if len(sys.argv) > 2 else '0001_initial'

    print(f"Target DB: {db_path}")
    print(f"Target alembic revision: {revision}")

    if not os.path.exists(db_path):
        print("Error: DB file does not exist. Aborting.")
        return 1

    if not backup_db(db_path):
        print("Failed to back up DB. Aborting.")
        return 2

    try:
        ensure_alembic_version(db_path, revision)
        print("Done. You can now run: flask db migrate")
        return 0
    except Exception as e:
        print(f"Error while updating alembic_version: {e}")
        return 3


if __name__ == '__main__':
    sys.exit(main())
