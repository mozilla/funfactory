# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.test import TestCase

from funfactory.urlresolvers import reverse, split_path
from mock import patch
from nose.tools import eq_


# split_path tests use a test generator, which cannot be used inside of a
# TestCase class
def test_split_path():
    testcases = [
        # Basic
        ('en-US/some/action', ('en-US', 'some/action')),
        # First slash doesn't matter
        ('/en-US/some/action', ('en-US', 'some/action')),
        # Nor does capitalization
        ('En-uS/some/action', ('en-US', 'some/action')),
        # Unsupported languages return a blank language
        ('unsupported/some/action', ('', 'unsupported/some/action')),
        ]

    for tc in testcases:
        yield check_split_path, tc[0], tc[1]


def check_split_path(path, result):
    res = split_path(path)
    eq_(res, result)


# Test urlpatterns
urlpatterns = patterns('',
    url(r'^test/$', lambda r: None, name='test.view')
)


class FakePrefixer(object):
    def __init__(self, fix):
        self.fix = fix


@patch('funfactory.urlresolvers.get_url_prefix')
class TestReverse(TestCase):
    urls = 'tests.test_urlresolvers'

    def test_unicode_url(self, get_url_prefix):
        # If the prefixer returns a unicode URL it should be escaped and cast
        # as a str object.
        get_url_prefix.return_value = FakePrefixer(lambda p: u'/Françoi%s' % p)
        result = reverse('test.view')

        # Ensure that UTF-8 characters are escaped properly.
        self.assertEqual(result, '/Fran%C3%A7oi/test/')
        self.assertEqual(type(result), str)
