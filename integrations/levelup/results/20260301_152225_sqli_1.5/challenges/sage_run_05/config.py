import os

class Config:
    SECRET_KEY = os.urandom(32)
    # SQLite must be in /tmp for read-only filesystem compatibility
    DATABASE_PATH = '/tmp/vanguard_logistics.db'