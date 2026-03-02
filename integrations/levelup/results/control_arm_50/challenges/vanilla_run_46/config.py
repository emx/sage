import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '592e3d36b76174a72d73318991a0c83a'
    DATABASE = '/tmp/aetherflow.db'
    DEBUG = False