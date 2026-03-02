import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '0rb1t_Str3am_D3fau1t_K3y_2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/orbitstream.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False