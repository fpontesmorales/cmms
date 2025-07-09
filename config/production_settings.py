import os
from .settings import *

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = ['fpontesmorales.pythonanywhere.com']
CSRF_TRUSTED_ORIGINS = ['https://fpontesmorales.pythonanywhere.com']

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'infra.caucaia@ifce.edu.br'