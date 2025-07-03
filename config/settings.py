import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# A chave secreta será lida de uma "Variável de Ambiente" no servidor.
# Se não encontrar, usa uma chave insegura (apenas para o seu PC local).
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-local-e-insegura-para-testes')

# O modo DEBUG será 'False' no servidor e 'True' no seu PC local.
DEBUG = os.environ.get('DJANGO_DEBUG', '') != 'False'

ALLOWED_HOSTS = ['127.0.0.1', '10.10.2.88']

# Adiciona o seu futuro endereço do PythonAnywhere à lista de permissões
if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    ALLOWED_HOSTS.append(os.environ['PYTHONANYWHERE_DOMAIN'])


# Application definition
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

# Database
# A configuração do banco de dados agora usará SQLite, que é um arquivo.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
# Caminho onde o comando 'collectstatic' vai juntar todos os arquivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Jazzmin Theme Settings
JAZZMIN_SETTINGS = {
    "site_title": "CMMS INFRA",
    "site_header": "CMMS IFCE",
    "site_brand": "INFRA-IFCE",
    "theme": "flatly",
    "order_with_respect_to": ["auth", "chamados", "inventario", "cadastros"],
    "apps": {
        "chamados": {"label": "Gestão de Chamados", "icon": "fas fa-bullhorn"},
        "inventario": {"label": "Inventário", "icon": "fas fa-box-open"},
        "cadastros": {"label": "Cadastros de Suporte", "icon": "fas fa-cogs"},
    },
    "icons": {
        "auth": "fas fa-users-cog", "auth.user": "fas fa-user", "auth.Group": "fas fa-users",
        "chamados.Chamado": "fas fa-bullhorn", "chamados.Interacao": "fas fa-comments",
        "cadastros.Bloco": "fas fa-building", "cadastros.Sala": "fas fa-door-open",
        "cadastros.TipoServico": "fas fa-tools", "cadastros.TipoPiso": "fas fa-layer-group",
        "cadastros.TipoForro": "fas fa-layer-group", "cadastros.TipoPintura": "fas fa-layer-group",
        "cadastros.TipoPorta": "fas fa-layer-group",
        "inventario.TipoAtivo": "fas fa-tags", "inventario.Ativo": "fas fa-box"
    }
}

# Auth Settings
LOGIN_REDIRECT_URL = '/painel/'
LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/'

# Email Settings (Modo de Desenvolvimento)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'