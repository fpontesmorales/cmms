import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis do arquivo .env (se ele existir)
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Configurações de Segurança ---
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-chave-local-para-desenvolvimento')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '10.10.2.88'] # Ex: '10.10.2.88'
PYTHONANYWHERE_DOMAIN = os.environ.get('PYTHONANYWHERE_DOMAIN')
if PYTHONANYWHERE_DOMAIN:
    ALLOWED_HOSTS.append(PYTHONANYWHERE_DOMAIN)
    CSRF_TRUSTED_ORIGINS = [f'https://{PYTHONANYWHERE_DOMAIN}']

# --- Aplicações Instaladas ---
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chamados.apps.ChamadosConfig',
    'cadastros.apps.CadastrosConfig',
    'inventario.apps.InventarioConfig',
]

# --- Middlewares ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- Banco de Dados ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Validadores de Senha ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internacionalização ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True

# --- Arquivos Estáticos e de Mídia ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Configurações de Terceiros (Jazzmin) ---
JAZZMIN_SETTINGS = {
    "site_title": "CMMS INFRA", "site_header": "CMMS IFCE", "site_brand": "INFRA-IFCE", "theme": "flatly",
    "order_with_respect_to": ["auth", "chamados", "inventario", "cadastros"],
    "apps": {
        "chamados": {"label": "Gestão de Chamados", "icon": "fas fa-bullhorn"},
        "inventario": {"label": "Inventário", "icon": "fas fa-box-open"},
        "cadastros": {"label": "Cadastros de Suporte", "icon": "fas fa-cogs"},
    },
    "icons": {
        "auth": "fas fa-users-cog", "auth.user": "fas fa-user", "auth.Group": "fas fa-users",
        "chamados.Chamado": "fas fa-bullhorn", "chamados.Interacao": "fas fa-comments",
        "cadastros.Bloco": "fas fa-building", "cadastros.Sala": "fas fa-door-open", "cadastros.TipoServico": "fas fa-tools",
        "cadastros.TipoPiso": "fas fa-layer-group", "cadastros.TipoForro": "fas fa-layer-group", "cadastros.TipoPintura": "fas fa-layer-group",
        "cadastros.TipoPorta": "fas fa-layer-group", "cadastros.Funcao": "fas fa-id-badge",
        "inventario.TipoAtivo": "fas fa-tags", "inventario.Ativo": "fas fa-box"
    }
}

# --- Autenticação ---
LOGIN_REDIRECT_URL = '/painel/'
LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/'

# --- Configuração de E-mail ---
DEFAULT_FROM_EMAIL = 'infra.caucaia@ifce.edu.br'

# Lógica para usar o backend correto em cada ambiente
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')