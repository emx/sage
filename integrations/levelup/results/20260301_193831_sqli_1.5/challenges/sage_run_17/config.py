import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'v3loce_str3am_logistics_2024_secret'
    DATABASE = '/tmp/logistics.db'