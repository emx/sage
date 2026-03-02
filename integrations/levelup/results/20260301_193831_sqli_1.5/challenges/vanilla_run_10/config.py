import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
    DATABASE = '/tmp/voyant.db'