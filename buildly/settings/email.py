from .base import *

# Email configuration

if os.getenv('EMAIL_BACKEND') == 'SMTP':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', True)
    EMAIL_SUBJECT_PREFIX = os.getenv('EMAIL_SUBJECT_PREFIX', '')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
DEFAULT_REPLYTO_EMAIL = os.getenv('DEFAULT_REPLYTO_EMAIL')
RESETPASS_CONFIRM_URL_PATH = os.getenv('RESETPASS_CONFIRM_URL_PATH')
