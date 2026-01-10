import os
from .settings import *
from .settings import BASE_DIR
# from urllib.parse import urlparse

hostname = os.environ.get('WEBSITE_HOSTNAME', '')
# domain = urlparse('https://' + hostname).netloc

# if domain:
#     CSRF_TRUSTED_ORIGINS = [f'https://{domain}']
# else:
#     CSRF_TRUSTED_ORIGINS = [
#     'https://tutorking-cjudd8evfkdcyduw.southafricanorth-01.azurewebsites.net'
#     ]

SECRET_KEY = os.environ.get('SECRET')
ALLOWED_HOSTS = [os.environ.get('WEBSITE_HOSTNAME', '')]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ.get('WEBSITE_HOSTNAME', '')]
DEBUG = False


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'authentication.LoginMiddlewareMaxin.LoginCheckMiddleware',

]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR,"staticfiles")
connectin_String = os.environ.get('AZURE_POSTGRESQL_CONNECTIONSTRING')
parameters = {pair.split('='):pair.split('=')[1] for pair in connectin_String.split(' ')}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parameters['dbname'],
        'HOST': parameters['host'],
        'USER':parameters['user'],
        'PASSWORD':parameters['password']
        ,
        'OPTIONS': {
            'timeout': 120,
        }


    }
}

