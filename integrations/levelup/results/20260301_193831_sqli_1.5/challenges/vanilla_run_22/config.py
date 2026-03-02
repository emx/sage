import os

class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = False