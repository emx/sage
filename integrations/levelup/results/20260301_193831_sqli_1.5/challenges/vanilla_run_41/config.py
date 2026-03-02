import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'v3sp3r_g1lt_p4ss_shhh'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/vesper.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False