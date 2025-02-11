import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    MYSQL_HOST = os.getenv('HOST')
    MYSQL_PORT = int(os.getenv('PORT', 3306))
    MYSQL_USER = os.getenv('USER')
    MYSQL_PASSWORD = os.getenv('PASSWORD')
    MYSQL_DB = os.getenv('SRIP_P')