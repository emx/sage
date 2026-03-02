import os

class Config:
    DATABASE = '/tmp/velostratus.db'
    SECRET_KEY = os.urandom(24)