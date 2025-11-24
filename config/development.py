from config.default import Config

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries
    
    # Allow longer request timeouts for development
    REQUEST_TIMEOUT = 30