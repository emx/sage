import os

class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE_PATH = '/tmp/vanguard_logistics.db'