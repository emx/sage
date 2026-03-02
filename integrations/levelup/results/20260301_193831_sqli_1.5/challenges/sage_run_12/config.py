import os
class Config:
    SECRET_KEY = '55d8e7b9231f4e8ea312b9195679c45a'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/vexillum.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False