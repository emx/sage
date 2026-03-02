import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'v3rdant_pals3_s3cr3t_2024'
    DATABASE = '/tmp/verdant.db'
    DEBUG = False