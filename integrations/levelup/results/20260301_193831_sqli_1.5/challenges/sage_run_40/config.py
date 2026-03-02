import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-logistics-key-9988'
    DATABASE = '/tmp/aetherbound.db'