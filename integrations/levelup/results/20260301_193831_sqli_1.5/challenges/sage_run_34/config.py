import os

class Config:
    SECRET_KEY = os.urandom(32)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'