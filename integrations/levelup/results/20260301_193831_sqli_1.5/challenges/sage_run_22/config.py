import os

class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE_PATH = '/tmp/nebula_logistics.db'
    DEBUG = False