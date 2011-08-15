from django.conf import settings

from mock import patch
from nose.tools import eq_
from test_utils import TestCase

from funfactory.utils import absolutify


class AbsolutifyTests(TestCase):
    def setUp(self):
        super(AbsolutifyTests, self).setUp()

        self.settings_patcher = patch.object(settings, '_wrapped')
        self.settings_mock = self.settings_patcher.start()
        self.settings_mock.DOMAIN = 'test.mo.com'
        self.settings_mock.PROTOCOL = 'http://'

        self.abs_path = '/some/absolute/path'

    def tearDown(self):
        self.settings_patcher.stop()
        super(AbsolutifyTests, self).tearDown()

    def test_basic(self):
        self.settings_mock.PORT = 80

        url = absolutify(self.abs_path)
        eq_('http://test.mo.com/some/absolute/path', url)

    def test_https(self):
        self.settings_mock.PROTOCOL = 'https://'
        self.settings_mock.PORT = 443

        url = absolutify(self.abs_path)
        eq_('https://test.mo.com/some/absolute/path', url)

    def test_with_port(self):
        self.settings_mock.PORT = 8000

        url = absolutify(self.abs_path)
        eq_('http://test.mo.com:8000/some/absolute/path', url)
