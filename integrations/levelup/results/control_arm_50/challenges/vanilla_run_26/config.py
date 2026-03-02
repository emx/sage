import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_12345')
    DATABASE = '/tmp/verdant.db'
    DEBUG = False