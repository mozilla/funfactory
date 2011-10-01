import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from mock import Mock, patch
from nose.tools import raises

from funfactory.manage import validate_settings


def setup():
    warnings.filterwarnings('error')


def teardown():
    warnings.resetwarnings()


@raises(UserWarning)
@patch.object(settings, 'DEBUG', True)
@patch.object(settings, 'SECRET_KEY', '')
def test_empty_secret_key_for_dev():
    validate_settings(settings)


@raises(ImproperlyConfigured)
@patch.object(settings, 'DEBUG', False)
@patch.object(settings, 'SECRET_KEY', '')
def test_empty_secret_key_for_prod():
    validate_settings(settings)


@patch.object(settings, 'DEBUG', False)
@patch.object(settings, 'SECRET_KEY', 'any random value')
def test_secret_key_ok():
    validate_settings(settings)
