import os

class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE_PATH = '/tmp/aetheris_logistics.db'