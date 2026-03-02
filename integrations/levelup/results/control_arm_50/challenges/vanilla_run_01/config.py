import os
class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE = '/tmp/velovista.db'
    DEBUG = False