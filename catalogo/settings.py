import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de um arquivo .env, se python-dotenv estiver instalado.
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-9xk@4f1z!2kq8v#3r9v$0l1m2n3p4q5r6s7t8u9v0w'  # fallback p/ dev
)

DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'storages',
    'produtos',
    'pedidos',
    'loja',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ── Banco de dados ──────────────────────────────────────────────
# Se DB_HOST estiver definido no ambiente, usa PostgreSQL (ex.: Amazon RDS).
# Caso contrário, cai no SQLite local — não precisa configurar nada para testar.
if os.getenv('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME':     os.getenv('DB_NAME', 'voltstore'),
            'USER':     os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST':     os.getenv('DB_HOST'),
            'PORT':     os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '60')),
            'OPTIONS': {
                # exige SSL por padrão (recomendado no RDS); use DB_SSLMODE=disable p/ desligar
                'sslmode': os.getenv('DB_SSLMODE', 'require'),
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# ── Arquivos de mídia (imagens dos produtos) ────────────────────
# Com USE_S3=True, as imagens vão para um bucket no AWS S3.
# Caso contrário, ficam no disco local (pasta media/).
USE_S3 = os.getenv('USE_S3', 'False').lower() in ('true', '1', 'yes')

if USE_S3:
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    # Credenciais: se rodar em EC2/Elastic Beanstalk com IAM Role,
    # pode deixar em branco que o boto3 usa as credenciais da instância.
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    AWS_S3_CUSTOM_DOMAIN = os.getenv(
        'AWS_S3_CUSTOM_DOMAIN',
        f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    )
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_DEFAULT_ACL = None          # respeita a policy do bucket
    AWS_QUERYSTRING_AUTH = False    # URLs limpas (objetos públicos para leitura)
    AWS_S3_FILE_OVERWRITE = True    # sobrescreve em vez de chamar HeadObject (evita 403 quando objeto não existe)

    STORAGES = {
        'default': {  # uploads de mídia → S3
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {'location': 'media'},
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ALLOWED_HOSTS = os.getenv(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1,.elasticbeanstalk.com'
).split(',')

# CSRF: aceita os mesmos hosts via HTTPS (e HTTP enquanto TLS não está ativo).
# Quando configurar HTTPS no EB, dá para tirar a parte http://.
CSRF_TRUSTED_ORIGINS = []
for h in ALLOWED_HOSTS:
    h = h.strip()
    if not h or h in ('localhost', '127.0.0.1'):
        continue
    # ".elasticbeanstalk.com" -> "https://*.elasticbeanstalk.com" + http
    if h.startswith('.'):
        CSRF_TRUSTED_ORIGINS.append(f'https://*{h}')
        CSRF_TRUSTED_ORIGINS.append(f'http://*{h}')
    else:
        CSRF_TRUSTED_ORIGINS.append(f'https://{h}')
        CSRF_TRUSTED_ORIGINS.append(f'http://{h}')

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise: serve estáticos comprimidos (admin, DRF browsable) em produção
# CompressedStaticFilesStorage (sem Manifest) é tolerante a arquivos faltando;
# se trocar para CompressedManifestStaticFilesStorage no futuro, garantir que
# collectstatic rode com sucesso em todo deploy ANTES do app aceitar requests.
if not DEBUG:
    STORAGES_STATICFILES = 'whitenoise.storage.CompressedStaticFilesStorage'
else:
    STORAGES_STATICFILES = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Se ainda não há STORAGES (modo local sem S3), define para incluir staticfiles
if 'STORAGES' not in dir():
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': STORAGES_STATICFILES},
    }
else:
    STORAGES['staticfiles'] = {'BACKEND': STORAGES_STATICFILES}

# Segurança HTTPS — ativadas em produção (DJANGO_DEBUG=False)
# DJANGO_SECURE_COOKIES=False permite logar em HTTP enquanto o EB ainda não tem TLS.
# Em produção real, configure HTTPS no EB (ACM + Listener 443) e remova essa variável.
_secure_cookies = os.getenv('DJANGO_SECURE_COOKIES', 'True').lower() == 'true'
if not DEBUG:
    SESSION_COOKIE_SECURE = _secure_cookies
    CSRF_COOKIE_SECURE = _secure_cookies
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # EB faz TLS no LB
    if _secure_cookies:
        SECURE_HSTS_SECONDS = 3600           # comece curto; aumente quando confiante
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_SSL_REDIRECT = True         # ative depois de configurar HTTPS no EB

ROOT_URLCONF = 'catalogo.urls'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework — Browsable API + JSON habilitados
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}


# ── Logging: registra erros Python em /var/log/django-error.log ───
# (Facilita debug em produção sem precisar de ssh)
import logging.handlers
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'botocore': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'boto3': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
