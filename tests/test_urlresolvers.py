from funfactory.urlresolvers import split_path
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
