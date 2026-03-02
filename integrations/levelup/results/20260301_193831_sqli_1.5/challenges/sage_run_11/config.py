import os
class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE = '/tmp/orbit_logistics.db'
    DEBUG = False