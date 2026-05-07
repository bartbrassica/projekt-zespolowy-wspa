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
        
        # Email configuration
        self.EMAIL_BACKEND = getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
        self.EMAIL_HOST = getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.EMAIL_PORT = int(getenv('EMAIL_PORT', '587'))
        self.EMAIL_USE_TLS = getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
        self.EMAIL_HOST_USER = getenv('EMAIL_HOST_USER')
        self.EMAIL_HOST_PASSWORD = getenv('EMAIL_HOST_PASSWORD')
        self.DEFAULT_FROM_EMAIL = getenv('DEFAULT_FROM_EMAIL', self.EMAIL_HOST_USER)
        self.FRONTEND_URL = getenv('FRONTEND_URL', 'http://localhost:3000')


config = Config()
