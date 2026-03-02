import os
class Config:
    SECRET_KEY = os.urandom(32)
    JSON_SORT_KEYS = False