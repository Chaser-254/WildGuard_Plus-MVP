from app import create_app
app = create_app()
with app.app_context():
    m = app.extensions.get('migrate')
    print('migrate extension present:', bool(m))
    if m:
        print('migrate.configure_args:', m.configure_args)
        try:
            db = m.db
            print('migrate.db present:', db is not None)
            print('db metadata tables:', getattr(db, 'metadatas', 'no metadatas'))
            print('db.metadata.tables:', list(db.metadata.tables.keys()))
        except Exception as e:
            print('Error inspecting migrate.db:', e)
