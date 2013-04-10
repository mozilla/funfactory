# Django settings file for a project based on the playdoh template.
# import * into your settings_local.py
import logging
import os
import socket

from django.utils.functional import lazy

from .manage import ROOT, path


# For backwards compatability, (projects built based on cloning playdoh)
# we still have to have a ROOT_URLCONF.
# For new-style playdoh projects this will be overridden automatically
# by the new installer
ROOT_URLCONF = '%s.urls' % os.path.basename(ROOT)

# Is this a dev instance?
DEV = False

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {}  # See settings_local.

SLAVE_DATABASES = []

DATABASE_ROUTERS = ('multidb.PinningMasterSlaveRouter',)

# Site ID is used by Django's Sites framework.
SITE_ID = 1

## Logging
LOG_LEVEL = logging.INFO
HAS_SYSLOG = True
SYSLOG_TAG = "http_app_playdoh"  # Change this after you fork.
LOGGING_CONFIG = None
LOGGING = {}

# CEF Logging
CEF_PRODUCT = 'Playdoh'
CEF_VENDOR = 'Mozilla'
CEF_VERSION = '0'
CEF_DEVICE_VERSION = '0'


## Internationalization.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Gettext text domain
TEXT_DOMAIN = 'messages'
STANDALONE_DOMAINS = [TEXT_DOMAIN, 'javascript']
TOWER_KEYWORDS = {'_lazy': None}
TOWER_ADD_HEADERS = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

## Accepted locales

# Tells the product_details module where to find our local JSON files.
# This ultimately controls how LANGUAGES are constructed.
PROD_DETAILS_DIR = path('lib/product_details_json')

# On dev instances, the list of accepted locales defaults to the contents of
# the `locale` directory within a project module or, for older Playdoh apps,
# the root locale directory.  A localizer can add their locale in the l10n
# repository (copy of which is checked out into `locale`) in order to start
# testing the localization on the dev server.
import glob
import itertools
DEV_LANGUAGES = None
try:
    DEV_LANGUAGES = [
        os.path.basename(loc).replace('_', '-')
        for loc in itertools.chain(glob.iglob(ROOT + '/locale/*'),  # old style
                                   glob.iglob(ROOT + '/*/locale/*'))
        if (os.path.isdir(loc) and os.path.basename(loc) != 'templates')
    ]
except OSError:
    pass

# If the locale/ directory isn't there or it's empty, we make sure that
# we always have at least 'en-US'.
if not DEV_LANGUAGES:
    DEV_LANGUAGES = ('en-US',)

# On stage/prod, the list of accepted locales is manually maintained.  Only
# locales whose localizers have signed off on their work should be listed here.
PROD_LANGUAGES = (
    'en-US',
)


def lazy_lang_url_map():
    from django.conf import settings
    langs = settings.DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(i.lower(), i) for i in langs])

LANGUAGE_URL_MAP = lazy(lazy_lang_url_map, dict)()


# Override Django's built-in with our native names
def lazy_langs():
    from django.conf import settings
    from product_details import product_details
    langs = DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(lang.lower(), product_details.languages[lang]['native'])
                 for lang in langs if lang in product_details.languages])

LANGUAGES = lazy(lazy_langs, dict)()

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        # Searching apps dirs only exists for historic playdoh apps.
        # See playdoh's base settings for how message paths are set.
        ('apps/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('apps/**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
        ('templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
    ],
}

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES = ['media', 'static', 'admin']


## Media and templates.

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path('static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
# Set this in your local settings which is not committed to version control.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'funfactory.context_processors.i18n',
    'funfactory.context_processors.globals',
    #'jingo_minify.helpers.build_ids',
)


def get_template_context_processors(exclude=(), append=(),
                        current={'processors': TEMPLATE_CONTEXT_PROCESSORS}):
    """
    Returns TEMPLATE_CONTEXT_PROCESSORS without the processors listed in
    exclude and with the processors listed in append.

    The use of a mutable dict is intentional, in order to preserve the state of
    the TEMPLATE_CONTEXT_PROCESSORS tuple across multiple settings files.
    """

    current['processors'] = tuple(
        [p for p in current['processors'] if p not in exclude]
    ) + tuple(append)

    return current['processors']


TEMPLATE_DIRS = (
    path('templates'),
)

# Storage of static files
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
)
COMPRESS_PRECOMPILERS = (
    #('text/coffeescript', 'coffee --compile --stdio'),
    ('text/less', 'lessc {infile} {outfile}'),
    #('text/x-sass', 'sass {infile} {outfile}'),
    #('text/x-scss', 'sass --scss {infile} {outfile}'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)


def JINJA_CONFIG():
    import jinja2
    from django.conf import settings
#    from caching.base import cache
    config = {'extensions': ['tower.template.i18n', 'jinja2.ext.do',
                             'jinja2.ext.with_', 'jinja2.ext.loopcontrols'],
              'finalize': lambda x: x if x is not None else ''}
#    if 'memcached' in cache.scheme and not settings.DEBUG:
        # We're passing the _cache object directly to jinja because
        # Django can't store binary directly; it enforces unicode on it.
        # Details: http://jinja.pocoo.org/2/documentation/api#bytecode-cache
        # and in the errors you get when you try it the other way.
#        bc = jinja2.MemcachedBytecodeCache(cache._cache,
#                                           "%sj2:" % settings.CACHE_PREFIX)
#        config['cache_size'] = -1 # Never clear the cache
#        config['bytecode_cache'] = bc
    return config


## Middlewares, apps, URL configs.

MIDDLEWARE_CLASSES = (
    'funfactory.middleware.LocaleURLMiddleware',
    'multidb.middleware.PinningRouterMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',  # Must be after auth middleware.
    'django.contrib.messages.middleware.MessageMiddleware',
    'commonware.middleware.FrameOptionsHeader',
    'mobility.middleware.DetectMobileMiddleware',
    'mobility.middleware.XMobileMiddleware',
)


def get_middleware(exclude=(), append=(),
                   current={'middleware': MIDDLEWARE_CLASSES}):
    """
    Returns MIDDLEWARE_CLASSES without the middlewares listed in exclude and
    with the middlewares listed in append.

    The use of a mutable dict is intentional, in order to preserve the state of
    the MIDDLEWARE_CLASSES tuple across multiple settings files.
    """

    current['middleware'] = tuple(
        [m for m in current['middleware'] if m not in exclude]
    ) + tuple(append)
    return current['middleware']


INSTALLED_APPS = (
    # Local apps
    'funfactory',  # Content common to most playdoh-based apps.
    'compressor',

    'tower',  # for ./manage.py extract (L10n)
    'cronjobs',  # for ./manage.py cron * cmd line tasks
    'django_browserid',


    # Django contrib apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    # 'django.contrib.sites',
    # 'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    # Third-party apps, patches, fixes
    'commonware.response.cookies',
    'djcelery',
    'django_nose',
    'session_csrf',

    # L10n
    'product_details',
)


def get_apps(exclude=(), append=(), current={'apps': INSTALLED_APPS}):
    """
    Returns INSTALLED_APPS without the apps listed in exclude and with the apps
    listed in append.

    The use of a mutable dict is intentional, in order to preserve the state of
    the INSTALLED_APPS tuple across multiple settings files.
    """

    current['apps'] = tuple(
        [a for a in current['apps'] if a not in exclude]
    ) + tuple(append)
    return current['apps']

# Path to Java. Used for compress_assets.
JAVA_BIN = '/usr/bin/java'

# Sessions
#
# By default, be at least somewhat secure with our session cookies.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

## Auth
# The first hasher in this list will be used for new passwords.
# Any other hasher in the list can be used for existing passwords.
# Playdoh ships with Bcrypt+HMAC by default because it's the most secure.
# To use bcrypt, fill in a secret HMAC key in your local settings.
BASE_PASSWORD_HASHERS = (
    'django_sha2.hashers.BcryptHMACCombinedPasswordVerifier',
    'django_sha2.hashers.SHA512PasswordHasher',
    'django_sha2.hashers.SHA256PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)
HMAC_KEYS = {  # for bcrypt only
    #'2012-06-06': 'cheesecake',
}

from django_sha2 import get_password_hashers
PASSWORD_HASHERS = get_password_hashers(BASE_PASSWORD_HASHERS, HMAC_KEYS)

## Tests
TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

## Celery

# True says to simulate background tasks without actually using celeryd.
# Good for local development in case celeryd is not running.
CELERY_ALWAYS_EAGER = True

BROKER_CONNECTION_TIMEOUT = 0.1
CELERY_RESULT_BACKEND = 'amqp'
CELERY_IGNORE_RESULT = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Time in seconds before celery.exceptions.SoftTimeLimitExceeded is raised.
# The task can catch that and recover but should exit ASAP.
CELERYD_TASK_SOFT_TIME_LIMIT = 60 * 2

## Arecibo
# when ARECIBO_SERVER_URL is set, it can use celery or the regular wrapper
ARECIBO_USES_CELERY = True

# For absolute urls
try:
    DOMAIN = socket.gethostname()
except socket.error:
    DOMAIN = 'localhost'
PROTOCOL = "http://"
PORT = 80

## django-mobility
MOBILE_COOKIE = 'mobile'
