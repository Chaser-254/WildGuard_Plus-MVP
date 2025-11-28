from app import create_app
from sqlalchemy import text
app = create_app()
with app.app_context():
    engine = app.extensions['migrate'].db.get_engine()
    conn = engine.connect()
    try:
        res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [r[0] for r in res]
        print('Tables in DB:', tables)
        if 'alembic_version' in tables:
            v = conn.execute(text('SELECT * FROM alembic_version')).fetchall()
            print('alembic_version rows:', v)
        else:
            print('no alembic_version table')
    finally:
        conn.close()
