import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vanguard-maritime-logistics-system-key-2024'
    DATABASE = '/tmp/vanguard.db'