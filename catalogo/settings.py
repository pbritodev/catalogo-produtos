import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuração de DEBUG - True para desenvolvimento
DEBUG = True if os.getenv('DJANGO_DEBUG', 'True') == 'True' else False

# Configuração do banco de dados
# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configuração de arquivos de mídia
# SQLite não suporta S3, mas já preparamos o caminho
if DEBUG:
    # Armazenamento local para desenvolvimento
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    # Configuração preparada para S3 (será ativada depois)
    USE_S3 = os.getenv('USE_S3', 'False') == 'True'
    if USE_S3:
        # Configurações S3 serão ativadas posteriormente
        pass
    else:
        MEDIA_URL = '/media/'
        MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Hosts permitidos (importante para Elastic Beanstalk)
ALLOWED_HOSTS = os.getenv(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1,.elasticbeanstalk.com'
).split(',')

# Arquivos estáticos para deploy
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'