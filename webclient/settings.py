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

ALLOWED_HOSTS = ['*']

ALLOWED_INCLUDE_ROOTS = ('/index.html', '/log_in.html')

DEFAULT_CHARSET = 'utf-8'


# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stacksync',
    'easywebdav'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'webclient.urls'
WSGI_APPLICATION = 'webclient.wsgi.application'

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

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
  ('es', 'Spanish'),
  ('en', 'English'),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'conf', 'locale'),
)


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

#Mail settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = "mailer@gmail.com"
EMAIL_HOST_PASSWORD = "password"

#Database manager
MANAGER_HOST = '123.123.123.123'
MANAGER_USER = 'stacksync_user'
MANAGER_PASS = 'stacksync'
MANAGER_PORT = '5432'
MANAGER_DATABASE = 'stacksync'

URL_STACKSYNC = 'https://123.123.123.123:8080/v1'
STACKSYNC_CONSUMER_KEY = "b3af4e669daf880fb16563e6f36051b105188d413"
STACKSYNC_CONSUMER_SECRET = "c168e65c18d75b35d8999b534a3776cf"
STACKSYNC_REQUEST_TOKEN_ENDPOINT = "https://123.123.123.123:8080/oauth/request_token"
STACKSYNC_ACCESS_TOKEN_ENDPOINT = "https://123.123.123.123:8080/oauth/access_token"
STACKSYNC_AUTHORIZE_ENDPOINT = "https://123.123.123.123:8080/oauth/authorize"

KEYSTONE_ADMIN_USER = "stacksync_admin"
KEYSTONE_ADMIN_PASSWORD = "secret"
KEYSTONE_TENANT = "stacksync"
KEYSTONE_AUTH_URL = "https://123.123.123.123:5000/v2.0"
KEYSTONE_USR_URL = "https://123.123.123.123:35357/v2.0"
LOCAL_URL = "http://127.0.0.1:8000"
#KEYSTONE_AUTH_URL = "https://10.128.146.230:5000/v3"

# NUEVO CAMPO ADMINS = Recibiran los emails en caso de error en el servidor
ADMINS = (('Equipo de desarrollo', 'mailer@gmail.com'), ('Nombre', 'email@server.com'))

#LOGGER
# https://docs.djangoproject.com/en/1.7/topics/logging/
