from .base import *
from .email import *

# CORS to allow external apps auth through OAuth 2
# https://github.com/ottoyiu/django-cors-headers

INSTALLED_APPS += (
    'corsheaders',
)

MIDDLEWARE_CORS = [
    'corsheaders.middleware.CorsMiddleware',
]

MIDDLEWARE = MIDDLEWARE_CORS + MIDDLEWARE


CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = ['https://127.0.0.1', 'http://127.0.0.1', 'https://localhost','http://localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Security


ALLOWED_HOSTS = ["http://localhost:8000", "http://127.0.0.1:8000"]

# https://docs.djangoproject.com/en/1.11/ref/settings/#secure-proxy-ssl-header

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/#configuring-logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'class': 'logging.FileHandler',
            'filename': os.path.join(
                '/var/log/' if os.access('/var/log/', os.W_OK) else os.getcwd(),
                'buildly.log'
            ),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}

HUBSPOT_API_KEY = ""

SECRET_KEY = "asdfe32fasdf343fasdff32234@##wa45tfgsdfg343"
TOKEN_SECRET_KEY = os.getenv("TOKEN_SECRET_KEY")

try:
    from .local import *
except (ModuleNotFoundError, ImportError):
    pass
