from app import create_app
import sqlalchemy as sa
from sqlalchemy import text
app = create_app()
with app.app_context():
    engine = app.extensions['migrate'].db.get_engine()
    conn = engine.connect()
    try:
        # Create alembic_version if missing
        conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"))
        # Check current
        res = conn.execute(text("SELECT version_num FROM alembic_version"))
        rows = res.fetchall()
        if rows:
            print('Existing alembic_version rows:', rows)
        else:
            print('No alembic_version row found, inserting our head')
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:v)"), {'v': '0001_initial'})
            print('Inserted revision 0001_initial')
    except Exception as e:
        print('Error stamping alembic_version:', e)
    finally:
        conn.close()
