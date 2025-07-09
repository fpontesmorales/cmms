import os
from .settings import *

# =================================================
# CONFIGURAÇÕES ESPECÍFICAS PARA O AMBIENTE ONLINE
# =================================================

# SEGURANÇA
DEBUG = False
# ATENÇÃO: Cole sua SECRET_KEY real aqui, dentro das aspas
SECRET_KEY = 'django-insecure-_2a7r)ix4wllaq3fmhtzz#f6ia%-o0ov7%n#8vn%81o5zxr@qa'
ALLOWED_HOSTS = ['fpontesmorales.pythonanywhere.com']
CSRF_TRUSTED_ORIGINS = ['https://fpontesmorales.pythonanywhere.com']

# E-MAIL: Configuração real do SendGrid
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'infra.caucaia@ifce.edu.br'