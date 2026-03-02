import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'v3loc3-str3am-v3ry-s3cr3t-k3y-2024'
    DATABASE = '/tmp/logistics.db'