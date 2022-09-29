import os

# Base dir path
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False if os.getenv('DEBUG') == 'False' else True

ALLOWED_HOSTS = ['*']


# Application definition

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/#deployment

STATIC_ROOT = '/static/'

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


INSTALLED_APPS_DJANGO = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.staticfiles',
]

INSTALLED_APPS_THIRD_PARTIES = [
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',

    # Social auth
    'social_django',

    # OAuth2
    'oauth2_provider',
    'oauth2_provider_jwt',

    # swagger
    'drf_yasg',

    # health check
    'health_check',                             # required
    'health_check.db',                          # stock Django health checkers
]

INSTALLED_APPS_LOCAL = [
    'buildly',
    'gateway',
    'core',
    'workflow',
    'datamesh',
]

INSTALLED_APPS = INSTALLED_APPS_DJANGO + INSTALLED_APPS_THIRD_PARTIES + INSTALLED_APPS_LOCAL

MIDDLEWARE_DJANGO = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE_CSRF = [
    'core.middleware.DisableCsrfCheck',
]

EXCEPTION_MIDDLEWARE = [
    'core.middleware.ExceptionMiddleware'
]

MIDDLEWARE = MIDDLEWARE_DJANGO + MIDDLEWARE_CSRF + EXCEPTION_MIDDLEWARE

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
            'builtins': [  # TODO to delete?
                'django.contrib.staticfiles.templatetags.staticfiles',
            ],
        },
    },
]

WSGI_APPLICATION = 'buildly.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{}'.format(os.environ['DATABASE_ENGINE']),
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.environ['DATABASE_PORT'],
    }
}


AUTH_USER_MODEL = 'core.CoreUser'

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


# NGINX and HTTPS
# https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-USE_X_FORWARDED_HOST

USE_X_FORWARDED_HOST = True if os.getenv('USE_X_FORWARDED_HOST') == 'True' else False

# https://docs.djangoproject.com/en/1.11/ref/settings/#secure-proxy-ssl-header

if os.getenv('USE_HTTPS') == 'True':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Rest Framework
REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',  # TODO check if disable, and also delete CSRF
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'core.permissions.IsSuperUserBrowseableAPI',
    )
    # ToDo: Think about `DEFAULT_PAGINATION_CLASS as env variable and
    #       customizable values with reasonable defaults
}

# Front-end application URL
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://www.example.com/')
REGISTRATION_URL_PATH = os.getenv('REGISTRATION_URL_PATH', 'register/')
RESETPASS_CONFIRM_URL_PATH = os.getenv('RESETPASS_CONFIRM_URL_PATH', 'reset_password_confirm/')
VERIFY_EMAIL_URL_PATH = os.getenv('VERIFY_EMAIL_URL_PATH', 'verify-email/')

PASSWORD_RESET_TIMEOUT_DAYS = 1

INVITATION_EXPIRE_HOURS = 24

CORE_WEBSITE = "https://buildly.io"

# User and Organization configuration
SUPER_USER_PASSWORD = os.getenv('SUPER_USER_PASSWORD')
DEFAULT_ORG = os.getenv('DEFAULT_ORG').lower() if os.getenv('DEFAULT_ORG') else None
AUTO_APPROVE_USER = False if os.getenv('AUTO_APPROVE_USER') == 'False' else True

# Swagger settings - for generate_swagger management command

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'gateway.urls.swagger_info',
}
