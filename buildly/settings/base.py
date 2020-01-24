import os

# Base dir path
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False if os.getenv('DEBUG') == 'False' else True

ALLOWED_HOSTS = []


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

MIDDLEWARE_THIRD_PARTIES = [
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

MIDDLEWARE_CSRF = [
    'core.middleware.DisableCsrfCheck',
]

EXCEPTION_MIDDLEWARE = [
    'core.middleware.ExceptionMiddleware'
]

MIDDLEWARE = MIDDLEWARE_DJANGO + MIDDLEWARE_THIRD_PARTIES + MIDDLEWARE_CSRF +\
             EXCEPTION_MIDDLEWARE

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

# Authentication backends
# https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-AUTHENTICATION_BACKENDS

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.microsoft.MicrosoftOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'oauth2_provider.backends.OAuth2Backend',
)


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
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # TODO check if disable, and also delete CSRF
        'rest_framework.authentication.TokenAuthentication',
        'oauth2_provider_jwt.authentication.JWTAuthentication',
    ),
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

PASSWORD_RESET_TIMEOUT_DAYS = 1

INVITATION_EXPIRE_HOURS = 24

# Auth Application
OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID', None)
OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET', None)

# JWT Authentication settings
JWT_PAYLOAD_ENRICHER = 'core.jwt_utils.payload_enricher'
JWT_ISSUER = os.getenv('JWT_ISSUER', '')
JWT_ALLOWED_ISSUER = os.getenv('JWT_ISSUER', '')
JWT_AUTH_DISABLED = False
JWT_PRIVATE_KEY_RSA_BUILDLY = os.getenv('JWT_PRIVATE_KEY_RSA_BUILDLY')
JWT_PUBLIC_KEY_RSA_BUILDLY = os.getenv('JWT_PUBLIC_KEY_RSA_BUILDLY')


# Password Validators
AUTH_PASSWORD_VALIDATORS = []

AUTH_PASSWORD_VALIDATORS_MAP = {
    'USE_PASSWORD_USER_ATTRIBUTE_SIMILARITY_VALIDATOR':
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
    'USE_PASSWORD_MINIMUM_LENGTH_VALIDATOR':
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': int(os.getenv('PASSWORD_MINIMUM_LENGTH', 6)),
            }
        },
    'USE_PASSWORD_COMMON_VALIDATOR':
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
    'USE_PASSWORD_NUMERIC_VALIDATOR':
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
}

for password_validator_env_var, password_validator in AUTH_PASSWORD_VALIDATORS_MAP.items():
    if os.getenv(password_validator_env_var, 'True') == 'True':
        AUTH_PASSWORD_VALIDATORS.append(password_validator)


# Social Auth
LOGIN_URL = os.getenv('LOGIN_URL', FRONTEND_URL)
LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_URL_NAMESPACE = 'social'

SOCIAL_AUTH_REDIRECT_IS_HTTPS = True if os.getenv('SOCIAL_AUTH_REDIRECT_IS_HTTPS') == 'True' else False
SOCIAL_AUTH_LOGIN_REDIRECT_URLS = {
    'github': os.getenv('SOCIAL_AUTH_GITHUB_REDIRECT_URL', None),
    'google-oauth2': os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URL', None),
    'microsoft-graph': os.getenv('SOCIAL_AUTH_MICROSOFT_GRAPH_REDIRECT_URL', None)
}

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.create_user',
    'core.auth_pipeline.create_organization',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# Github social auth
SOCIAL_AUTH_GITHUB_KEY = os.getenv('SOCIAL_AUTH_GITHUB_KEY', '')
SOCIAL_AUTH_GITHUB_SECRET = os.getenv('SOCIAL_AUTH_GITHUB_SECRET', '')

# Google social auth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')

# Microsoft social auth
SOCIAL_AUTH_MICROSOFT_GRAPH_KEY = os.getenv('SOCIAL_AUTH_MICROSOFT_GRAPH_KEY', '')
SOCIAL_AUTH_MICROSOFT_GRAPH_SECRET = os.getenv('SOCIAL_AUTH_MICROSOFT_GRAPH_SECRET', '')


# Whitelist of domains allowed to login via social auths
# i.e. ['example.com', 'buildly.io','treeaid.org']
if os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS'):
    SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS').split(',')
if os.getenv('SOCIAL_AUTH_MICROSOFT_WHITELISTED_DOMAINS'):
    SOCIAL_AUTH_GOOGLE_MICROSOFT_DOMAINS = os.getenv('SOCIAL_AUTH_MICROSOFT_WHITELISTED_DOMAINS').split(',')

# oauth2 settings
OAUTH2_PROVIDER = {
    "ACCESS_TOKEN_EXPIRE_SECONDS": int(os.getenv('ACCESS_TOKEN_EXPIRE_SECONDS', 36000)),
}

DEFAULT_OAUTH_DOMAINS = os.getenv('DEFAULT_OAUTH_DOMAINS', '')
CREATE_DEFAULT_PROGRAM = True if os.getenv('CREATE_DEFAULT_PROGRAM') == 'True' else False

# graphene schema
GRAPHENE = {
    'SCHEMA': 'workflow.graph-schema.schema' # Where your Graphene schema lives
}

CORS_ORIGIN_ALLOW_ALL = True

CORE_WEBSITE = "https://buildly.io"

# User and Organization configuration
SUPER_USER_PASSWORD = os.getenv('SUPER_USER_PASSWORD')
DEFAULT_ORG = os.getenv('DEFAULT_ORG')

# Swagger settings - for generate_swagger management command

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'gateway.urls.swagger_info',
}
