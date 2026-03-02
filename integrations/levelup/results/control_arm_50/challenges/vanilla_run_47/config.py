import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'v3rdant_4xle_dynam1cs_s3cr3t'
    DATABASE = '/tmp/verdant_logistics.db'