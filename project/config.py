import os
import re

# Если вы используете SQLAlchemy
database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/app.db')

# Render отдаёт URL, начинающийся с postgres://, но SQLAlchemy требует postgresql://
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
