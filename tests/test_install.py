import sys
import subprocess
from subprocess import Popen
import unittest

from nose.tools import eq_

from tests import PLAYDOH


class TestInstall(unittest.TestCase):

    def test(self):
        # sys.executable is our tox virtualenv that includes
        # compiled/dev modules.
        p = Popen([sys.executable, 'manage.py', 'test'],
                   stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                   cwd=PLAYDOH)
        print p.stdout.read()
        eq_(p.wait(), 0)
