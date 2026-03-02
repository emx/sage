import os

class Config:
    SECRET_KEY = os.urandom(32)
    # The DB path used by the application at runtime (must be writable)
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/vantage.db'
    DEBUG = False