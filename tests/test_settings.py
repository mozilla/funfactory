from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from mock import Mock, patch
from nose.tools import raises

from funfactory.manage import validate_settings


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
