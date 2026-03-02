import os

class Config:
    SECRET_KEY = os.urandom(32)
    # Database must be in /tmp for read-only filesystem compatibility
    DATABASE_PATH = '/tmp/aetherflow.db'