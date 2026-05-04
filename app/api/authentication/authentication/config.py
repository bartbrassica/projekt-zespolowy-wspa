from os import getenv


class Config:
    def __init__(self):
        self.CLIENT_SECRET = getenv('CLIENT_SECRET')
        self.DEBUG = getenv('DEBUG')
        self.JWT_ALG = getenv('JWT_ALG')
        self.DB_NAME = getenv('DB_NAME')
        self.DB_USER = getenv('DB_USER')
        self.DB_PASSWORD = getenv('DB_PASSWORD')
        self.DB_HOST = getenv('DB_HOST')
        self.DB_PORT = getenv('DB_PORT')


config = Config()
