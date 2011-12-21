from django.conf import settings

from mock import patch
from nose.tools import eq_
from django.test import TestCase

from funfactory.utils import absolutify


@patch.object(settings, 'DOMAIN', 'test.mo.com')
class AbsolutifyTests(TestCase):
    ABS_PATH = '/some/absolute/path'

    def test_basic(self):
        url = absolutify(AbsolutifyTests.ABS_PATH)
        eq_('http://test.mo.com/some/absolute/path', url)

    @patch.object(settings, 'PROTOCOL', 'https://')
    @patch.object(settings, 'PORT', 443)
    def test_https(self):
        url = absolutify(AbsolutifyTests.ABS_PATH)
        eq_('https://test.mo.com/some/absolute/path', url)

    @patch.object(settings, 'PORT', 8000)
    def test_with_port(self):
        url = absolutify(AbsolutifyTests.ABS_PATH)
        eq_('http://test.mo.com:8000/some/absolute/path', url)
