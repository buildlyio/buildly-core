import os
from datetime import timedelta

# Base dir path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEBUG = False if os.getenv('DEBUG') == 'False' else True

ALLOWED_HOSTS = ["http://localhost:8000", "http://127.0.0.1:8000"]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
# Application definition

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/#deployment

STATIC_ROOT = '/static/'

STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

INSTALLED_APPS_DJANGO = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS_THIRD_PARTIES = [
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    # swagger
    'drf_yasg',
    # health check
    'health_check',  # required
    'health_check.db',  # stock Django health checkers
]

INSTALLED_APPS_LOCAL = ['buildly', 'gateway', 'core', 'datamesh']

INSTALLED_APPS = (
        INSTALLED_APPS_DJANGO + INSTALLED_APPS_THIRD_PARTIES + INSTALLED_APPS_LOCAL
)

MIDDLEWARE_DJANGO = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE_CSRF = ['core.middleware.DisableCsrfCheck']

EXCEPTION_MIDDLEWARE = ['core.middleware.AsyncSessionAuthBlockMiddleware', 'core.middleware.ExceptionMiddleware']

MIDDLEWARE = MIDDLEWARE_DJANGO + MIDDLEWARE_CSRF + EXCEPTION_MIDDLEWARE

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [  # TODO to delete?
                'django.templatetags.static'
            ],
        },
    }
]

WSGI_APPLICATION = 'buildly.wsgi.application'

AUTH_USER_MODEL = 'core.CoreUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default backend
    # Add custom backends here if applicable
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = False

USE_L10N = False

USE_TZ = True

# Sites
# https://docs.djangoproject.com/en/1.11/ref/contrib/sites/

SITE_ID = 1

# https://docs.djangoproject.com/en/1.11/ref/settings/#secure-proxy-ssl-header

if os.getenv('USE_HTTPS') == 'True':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['core.permissions.IsSuperUserBrowseableAPI'],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',
}

# Front-end application URL
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://www.example.com/')
REGISTRATION_URL_PATH = os.getenv('REGISTRATION_URL_PATH', 'register/')
RESETPASS_CONFIRM_URL_PATH = os.getenv(
    'RESETPASS_CONFIRM_URL_PATH', 'reset_password_confirm/'
)
VERIFY_EMAIL_URL_PATH = os.getenv('VERIFY_EMAIL_URL_PATH', 'verify-email/')
PASSWORD_RESET_TIMEOUT_DAYS = 1

INVITATION_EXPIRE_HOURS = 24

CORE_WEBSITE = "https://buildly.io"

# User and Organization configuration
SUPER_USER_PASSWORD = os.getenv('SUPER_USER_PASSWORD')
DEFAULT_ORG = os.getenv('DEFAULT_ORG').lower() if os.getenv('DEFAULT_ORG') else None
AUTO_APPROVE_USER = False if os.getenv('AUTO_APPROVE_USER') == 'False' else True
FREE_COUPON_CODE = os.getenv('FREE_COUPON_CODE', '')
STRIPE_SECRET = os.getenv('STRIPE_SECRET', '')

EMAIL_VERIFICATION_EXPIRATION = 24  # Expiration time in hours

# Swagger settings - for generate_swagger management command

SWAGGER_SETTINGS = {'DEFAULT_INFO': 'gateway.urls.swagger_info'}

ORGANIZATION_TYPES = ['Developer', 'Product']

EMAIL_VERIFICATION_EXPIRATION = int(os.getenv('EMAIL_VERIFICATION_EXPIRATION', 12))

HUBSPOT_API_KEY = ''

ORGANIZATION_TYPES = ['Developer', 'Product']

SIMPLE_JWT = {
    "ALGORITHM": "HS256",  # Or "RS256" if you want asymmetric keys
    "SIGNING_KEY": os.getenv('SECRET_KEY', ''),  # Or your RS256 private key
    "VERIFYING_KEY": "",  # Only needed for RS256
    "ISSUER": "Buildly",
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    # Add other options as needed
}
