from app import create_app
app = create_app()
print('SQLALCHEMY_DATABASE_URI =', app.config.get('SQLALCHEMY_DATABASE_URI'))
print('SQLALCHEMY_TRACK_MODIFICATIONS =', app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS'))
print('FLASK_ENV:', app.config.get('ENV'))
