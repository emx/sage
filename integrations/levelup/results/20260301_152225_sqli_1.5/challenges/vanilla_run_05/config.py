import os
DATABASE = '/tmp/auraflow.db'
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_77889911')