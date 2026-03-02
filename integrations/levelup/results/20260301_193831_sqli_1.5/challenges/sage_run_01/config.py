import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'v3r1d1an_shhh_s3cr3t')
    DATABASE = '/tmp/veridian.db'