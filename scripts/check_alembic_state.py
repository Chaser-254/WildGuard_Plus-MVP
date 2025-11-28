"""
Check Alembic migration files and the current alembic_version recorded
in the SQLite DB. Helps diagnose 'Target database is not up to date' errors.

Usage:
    python scripts/check_alembic_state.py [path/to/db]

Output:
 - Lists migration files and their revision/down_revision
 - Prints the DB's alembic_version value
"""
import os
import sys
import sqlite3
import re


def list_migration_files(versions_dir):
    files = []
    if not os.path.isdir(versions_dir):
        return files
    for name in sorted(os.listdir(versions_dir)):
        if name.endswith('.py'):
            path = os.path.join(versions_dir, name)
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            rev = re.search(r"revision\s*=\s*['\"]([0-9a-fA-Za-z_]+)['\"]", text)
            down = re.search(r"down_revision\s*=\s*['\"]([0-9a-fA-Za-z_,\s]+)['\"]", text)
            files.append((name, rev.group(1) if rev else None, (down.group(1) if down else None)))
    return files


def read_db_revision(db_path):
    if not os.path.exists(db_path):
        return None, f"DB file not found: {db_path}"
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version';")
        if cur.fetchone() is None:
            conn.close()
            return None, 'alembic_version table not found in DB'
        cur.execute('SELECT version_num FROM alembic_version;')
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0], None
        return None, 'alembic_version table empty'
    except Exception as e:
        return None, str(e)


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    versions_dir = os.path.join(repo_root, 'migrations', 'versions')
    db_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(repo_root, 'instance', 'wildguard.db')

    print('Migration files found in:', versions_dir)
    files = list_migration_files(versions_dir)
    if not files:
        print('  (no migration files found)')
    else:
        for name, rev, down in files:
            print(f'  {name}\n    revision: {rev}\n    down_revision: {down}')

    rev, err = read_db_revision(db_path)
    print('\nDatabase:', db_path)
    if err:
        print('  ERROR reading DB revision:', err)
    else:
        print('  alembic_version in DB =', rev)

    print('\nNext recommended actions:')
    print('  1) Run: flask db current')
    print('  2) Run: flask db heads')
    print('  3) If there are unapplied migrations, run: flask db upgrade')
    print('  4) If Alembic graph still complains, paste the output of steps 1-3 here')


if __name__ == '__main__':
    main()
