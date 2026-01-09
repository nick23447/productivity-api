import os
from typing import Optional

class Config:
    SECRET_KEY: Optional[str] = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI: Optional[str] = os.environ.get('SQLALCHEMY_DATABASE_URI')

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  
    WTF_CSRF_ENABLED = False  
    SECRET_KEY = 'test-secret-key'  

