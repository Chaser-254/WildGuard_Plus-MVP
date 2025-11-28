from app import create_app
from flask import current_app
import sqlalchemy as sa
app = create_app()
with app.app_context():
    m = app.extensions.get('migrate')
    engine = m.db.get_engine()
    print('Engine URL:', getattr(engine, 'url', None))
    conn = engine.connect()
    try:
        res = conn.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [r[0] for r in res]
        print('Tables in DB:', tables)
        if 'alembic_version' in tables:
            v = conn.execute(sa.text('SELECT * FROM alembic_version')).fetchall()
            print('alembic_version rows:', v)
    except Exception as e:
        print('Error querying DB:', e)
    finally:
        conn.close()
