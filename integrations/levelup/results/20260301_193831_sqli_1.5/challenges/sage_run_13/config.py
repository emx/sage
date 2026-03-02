import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'v3rt3x-k3str3l-sh3ll-k3y-2024'
    DATABASE = '/tmp/aerospace.db'
    DEBUG = False