import os

class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE_PATH = '/tmp/velopath.db'
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '/tmp/flask_sessions'