import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-dev-key-123'
    DATABASE = '/tmp/orbitstream.db'
    DEBUG = False