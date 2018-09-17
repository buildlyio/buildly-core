import warnings
from .base import *

# CORS to allow external apps auth through OAuth 2
# https://github.com/ottoyiu/django-cors-headers

INSTALLED_APPS += (
    'corsheaders',
)

MIDDLEWARE_CORS = [
    'corsheaders.middleware.CorsMiddleware',
]

MIDDLEWARE = MIDDLEWARE_CORS + MIDDLEWARE

CORS_ORIGIN_WHITELIST = os.environ['CORS_ORIGIN_WHITELIST'].split(',')


# Security
# https://docs.djangoproject.com/en/1.11/ref/settings/#allowed-hosts

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

# https://docs.djangoproject.com/en/1.11/ref/settings/#secure-proxy-ssl-header

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/#deployment

STATIC_ROOT = '/static/'


# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/#configuring-logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'class': 'logging.FileHandler',
            'filename': '/var/log/bifrost_api.log',
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

# Email settings
# https://docs.djangoproject.com/en/1.11/topics/email/

if os.getenv('EMAIL_BACKEND') == 'SMTP':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', True)
    EMAIL_SUBJECT_PREFIX = os.getenv('EMAIL_SUBJECT_PREFIX', '')
else:
    warnings.warn('No SMTP email backend provider. Falling back to dummy '
                  'backend')
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
DEFAULT_REPLY_TO = os.environ['DEFAULT_REPLY_TO']
SALES_TEAM_EMAIL = os.getenv('SALES_TEAM_EMAIL', '')
