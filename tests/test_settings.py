from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from mock import Mock, patch
from nose.tools import eq_, raises

from funfactory.manage import validate_settings
from funfactory.settings_base import (get_apps, get_middleware,
    get_template_context_processors)


@patch.object(settings, 'DEBUG', True)
@patch.object(settings, 'HMAC_KEYS', {'2012-06-06': 'secret'})
@patch.object(settings, 'SECRET_KEY', 'any random value')
@patch.object(settings, 'SESSION_COOKIE_SECURE', False)
def test_insecure_session_cookie_for_dev():
    validate_settings(settings)


@raises(ImproperlyConfigured)
@patch.object(settings, 'DEBUG', False)
@patch.object(settings, 'HMAC_KEYS', {'2012-06-06': 'secret'})
@patch.object(settings, 'SECRET_KEY', '')
@patch.object(settings, 'SESSION_COOKIE_SECURE', True)
def test_empty_secret_key_for_prod():
    validate_settings(settings)


@patch.object(settings, 'DEBUG', False)
@patch.object(settings, 'HMAC_KEYS', {'2012-06-06': 'secret'})
@patch.object(settings, 'SECRET_KEY', 'any random value')
@patch.object(settings, 'SESSION_COOKIE_SECURE', True)
def test_secret_key_ok():
    """Validate required security-related settings.

    Don't raise exceptions when required settings are set properly."""
    validate_settings(settings)


@raises(ImproperlyConfigured)
@patch.object(settings, 'DEBUG', False)
@patch.object(settings, 'HMAC_KEYS', {'2012-06-06': 'secret'})
@patch.object(settings, 'SECRET_KEY', 'any random value')
@patch.object(settings, 'SESSION_COOKIE_SECURE', None)
def test_session_cookie_ok():
    """Raise an exception if session cookies aren't secure in production."""
    validate_settings(settings)


@patch.object(settings, 'DEBUG', True)
@patch.object(settings, 'HMAC_KEYS', {})
@patch.object(settings, 'SESSION_COOKIE_SECURE', False)
def test_empty_hmac_in_dev():
    # Should not raise an exception.
    validate_settings(settings)


@raises(ImproperlyConfigured)
@patch.object(settings, 'DEBUG', False)
@patch.object(settings, 'HMAC_KEYS', {})
@patch.object(settings, 'SESSION_COOKIE_SECURE', False)
def test_empty_hmac_in_prod():
    validate_settings(settings)


def test_get_apps():
    eq_(get_apps(exclude=('chico',),
        current={'apps': ('groucho', 'harpo', 'chico')}),
        ('groucho', 'harpo'))
    eq_(get_apps(append=('zeppo',),
        current={'apps': ('groucho', 'harpo', 'chico')}),
        ('groucho', 'harpo', 'chico', 'zeppo'))
    eq_(get_apps(exclude=('harpo', 'zeppo'), append=('chico',),
        current={'apps': ('groucho', 'harpo', 'zeppo')}),
        ('groucho', 'chico'))
    eq_(get_apps(exclude=('funfactory'), append=('gummo',)), get_apps())


def test_get_middleware():
    eq_(get_middleware(exclude=['larry', 'moe'],
        current={'middleware': ('larry', 'curly', 'moe')}),
        ('curly',))
    eq_(get_middleware(append=('shemp', 'moe'),
        current={'middleware': ('larry', 'curly')}),
        ('larry', 'curly', 'shemp', 'moe'))
    eq_(get_middleware(exclude=('curly'), append=['moe'],
        current={'middleware': ('shemp', 'curly', 'larry')}),
        ('shemp', 'larry', 'moe'))
    eq_(get_middleware(append=['emil']), get_middleware())


def test_get_processors():
    eq_(get_template_context_processors(exclude=('aramis'),
        current={'processors': ('athos', 'porthos', 'aramis')}),
        ('athos', 'porthos'))
    eq_(get_template_context_processors(append=("d'artagnan",),
        current={'processors': ('athos', 'porthos')}),
        ('athos', 'porthos', "d'artagnan"))
    eq_(get_template_context_processors(exclude=['athos'], append=['aramis'],
        current={'processors': ('athos', 'porthos', "d'artagnan")}),
        ('porthos', "d'artagnan", 'aramis'))
    eq_(get_template_context_processors(append=['richelieu']),
        get_template_context_processors())
