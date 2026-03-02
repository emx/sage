import os

class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE = '/tmp/velosync.db'
    DEBUG = False