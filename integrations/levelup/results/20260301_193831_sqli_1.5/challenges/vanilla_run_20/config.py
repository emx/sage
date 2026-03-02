import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'v3lo_5tr34m_sup3r_53cur3_k3y_9912'
    DATABASE = '/tmp/velostream.db'