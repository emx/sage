import os

class Config:
    SECRET_KEY = os.urandom(24)
    DATABASE_PATH = '/tmp/verdant_analytics.db'