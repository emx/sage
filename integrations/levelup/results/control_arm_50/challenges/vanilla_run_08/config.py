import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'v3rdant_pul5e_super_secr3t_k3y_9912'
    DATABASE = '/tmp/verdant_pulse.db'