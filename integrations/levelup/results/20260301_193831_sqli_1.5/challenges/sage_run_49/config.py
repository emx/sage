import os

class Config:
    SECRET_KEY = os.urandom(32)
    # Point to the writable /tmp directory for the database
    DATABASE_PATH = '/tmp/verdant_logix.db'