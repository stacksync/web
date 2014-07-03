"""
Django settings for web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4g4h1g859zavzyh3r5=rchkl%w9+%_cl%_v03=y9_ml218$2ox'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stacksync'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'web.urls'

WSGI_APPLICATION = 'web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,'mytemplates'),
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR,'static'),
)

MEDIA_ROOT = (
    os.path.join(BASE_DIR,'media'),
)

#url to conect
URL_STACKSYNC_OLD = 'https://cloudspaces.urv.cat:8080/v1/AUTH_e685194ffd724f55bd7f6ad14dc5bec7/stacksync'
URL_STACKSYNC = 'http://api.stacksync.com:8080/v1'
STACKSYNC_CONSUMER_KEY = "b3af4e669daf880fb16563e6f36051b105188d413"
STACKSYNC_CONSUMER_SECRET = "c168e65c18d75b35d8999b534a3776cf"
STACKSYNC_REQUEST_TOKEN_ENDPOINT = "http://api.stacksync.com:8080/oauth/request_token"
STACKSYNC_ACCESS_TOKEN_ENDPOINT = "http://api.stacksync.com:8080/oauth/access_token"
STACKSYNC_AUTHORIZE_ENDPOINT = "http://api.stacksync.com:8080/oauth/authorize"
