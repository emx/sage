import os

class Config:
    SECRET_KEY = os.urandom(32)
    DEBUG = False
    DATABASE = '/tmp/vortex.db'