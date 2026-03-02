import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'v3lo_l1nk_secret_2024_key_!'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/velolink.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False