from os.path import join, dirname
import logging

logging.basicConfig(level=logging.DEBUG)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = join(dirname(__file__), "barcampweb.db")             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

TIME_ZONE = 'Europe/Vienna'

LANGUAGE_CODE = 'de'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = join(dirname(__file__), "media")
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/admin_media/'

SECRET_KEY = '$^ixdng6xe9pw+*2@05!&n)zsqy^7j10-)^@bqt@hworbnn7pj'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'barcampweb_site.middleware.PlatformMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'barcampweb_site.apps.account.middleware.SimpleLoginMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'barcampweb_site.urls'

TEMPLATE_DIRS = (
    join(dirname(__file__), "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin', 
    'south',
    'django_extensions',
    'barcampweb_site.apps.barcamp',
    'barcampweb_site.apps.globaltags',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    'django.contrib.messages.context_processors.messages',
)
EMAIL_PORT = 1025
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'
