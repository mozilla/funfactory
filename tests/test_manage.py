import smtplib
import xml.dom
import unittest

from nose.tools import eq_, raises

from funfactory.manage import import_mod_by_name


class TestImporter(unittest.TestCase):

    def test_single_mod(self):
        eq_(import_mod_by_name('smtplib'), smtplib)

    def test_mod_attr(self):
        eq_(import_mod_by_name('smtplib.SMTP'), smtplib.SMTP)

    def test_multiple_attrs(self):
        eq_(import_mod_by_name('smtplib.SMTP.connect'),
            smtplib.SMTP.connect)

    def test_multiple_mods(self):
        eq_(import_mod_by_name('xml.dom'), xml.dom)

    @raises(ImportError)
    def test_unknown_mod(self):
        import_mod_by_name('notthenameofamodule')
