import os

class Config:
    SECRET_KEY = "your_secret_key"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:user@localhost/tollsync"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
