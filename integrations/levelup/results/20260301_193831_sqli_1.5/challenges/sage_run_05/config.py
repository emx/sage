import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vql-super-secret-key-12345'
    DATABASE_PATH = '/tmp/logistics.db'