import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '06d0937a85810076db3642398687b12d')
    DEBUG = False