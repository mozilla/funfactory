from django.conf import settings

from mock import patch
from nose.tools import eq_
from django.test import TestCase

import funfactory.utils as utils


@patch.object(settings, 'DOMAIN', 'test.mo.com')
class AbsolutifyTests(TestCase):
    ABS_PATH = '/some/absolute/path'

    def test_basic(self):
        url = utils.absolutify(AbsolutifyTests.ABS_PATH)
        eq_('%s/some/absolute/path' % settings.SITE_URL, url)

    @patch.object(settings, 'PROTOCOL', 'https://')
    @patch.object(settings, 'PORT', 443)
    def test_https(self):
        url = utils.absolutify(AbsolutifyTests.ABS_PATH)
        eq_('%s/some/absolute/path' % settings.SITE_URL, url)

    @patch.object(settings, 'SITE_URL', '')
    @patch.object(settings, 'PORT', 8009)
    def test_with_port(self):
        url = utils.absolutify(AbsolutifyTests.ABS_PATH)
        eq_('http://test.mo.com:8009/some/absolute/path', url)


@patch.object(utils.settings_base, 'INSTALLED_APPS', ('one', 'two', 'three'))
class GetAppsTests(TestCase):
    def test_exclude(self):
        eq_(utils.get_apps(exclude=['three']), ('one', 'two'))


@patch.object(utils.settings_base, 'MIDDLEWARE_CLASSES', ('foo', 'bar', 'baz'))
class GetMiddlewareTests(TestCase):
    def test_exclude(self):
        eq_(utils.get_middleware(exclude=['foo']), ('bar', 'baz'))


@patch.object(utils.settings_base, 'TEMPLATE_CONTEXT_PROCESSORS', ('a', 'b'))
class GetTemplateContextProcessorsTests(TestCase):
    def test_exclude(self):
        eq_(utils.get_template_context_processors(exclude=['a']), ('b',))
