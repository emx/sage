import os

class Config:
    SECRET_KEY = os.urandom(32)
    # Database MUST be in /tmp/ for read-only filesystem compatibility
    DATABASE_PATH = '/tmp/veridiant_logistics.db'