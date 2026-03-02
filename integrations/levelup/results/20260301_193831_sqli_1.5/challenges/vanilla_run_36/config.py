import os
class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE = '/tmp/thalassa.db'
    DEBUG = False