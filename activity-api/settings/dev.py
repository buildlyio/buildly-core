from .base import *

# Email settings
# https://docs.djangoproject.com/en/1.11/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/tola-messages'
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
DEFAULT_REPLY_TO = os.environ['DEFAULT_REPLY_TO']
EMAIL_SUBJECT_PREFIX = os.getenv('EMAIL_SUBJECT_PREFIX', '')
SALES_TEAM_EMAIL = 'sales@example.com'

# CORS to allow external apps auth through OAuth 2
# https://github.com/ottoyiu/django-cors-headers

INSTALLED_APPS += (
    'corsheaders',
)

MIDDLEWARE_CORS = [
    'corsheaders.middleware.CorsMiddleware',
]

MIDDLEWARE = MIDDLEWARE_CORS + MIDDLEWARE

CORS_ORIGIN_WHITELIST = "*"