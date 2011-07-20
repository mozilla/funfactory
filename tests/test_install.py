from functools import partial
import os
import shutil
import subprocess
from subprocess import check_call, Popen
import sys
import unittest

from nose.tools import eq_


shell = partial(check_call, shell=True)


class TestInstall(unittest.TestCase):

    def setUp(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        assert os.path.exists(os.path.join(root, 'setup.py')), (
                        'This does not appear to be the root dir: %s' % root)
        self.test_repo = os.path.join(root, '.playdoh', 'funtestapp')
        if not os.path.exists(self.test_repo):
            container = os.path.abspath(os.path.join(self.test_repo, '..'))
            if not os.path.exists(container):
                os.mkdir(container)
            check_call(['git', 'clone', '--recursive',
                        'git://github.com/mozilla/playdoh.git',
                        self.test_repo])
        else:
            proj_sh = partial(shell, cwd=self.test_repo)
            proj_sh('git pull origin base')
            proj_sh('git submodule sync -q')
            proj_sh('git submodule update --init')
            vend_sh = partial(shell,
                              cwd=os.path.join(self.test_repo, 'vendor'))
            vend_sh('git pull origin master')
            vend_sh('git submodule sync -q')
            vend_sh('git submodule update --init')

        st = os.path.join(self.test_repo, 'settings_local.py')
        if os.path.exists(st):
            os.unlink(st)
        shutil.copy(os.path.join(self.test_repo, 'settings_local.py-dist'),
                    st)

        db_user = os.environ.get('FF_DB_USER', 'root')
        db_pass = os.environ.get('FF_DB_PASS', '')
        db_name = os.environ.get('FF_DB_NAME', '_funfactory_test')

        with open(st, 'r') as f:
            new_st = f.read()
            new_st = new_st.replace("'USER': ''",
                                    "'USER': '%s'" % db_user)
            new_st = new_st.replace("'PASSWORD': ''",
                                    "'PASSWORD': '%s'" % db_pass)
            new_st = new_st.replace("'NAME': ''",
                                    "'NAME': '%s'" % db_name)

        with open(st, 'w') as f:
            f.write(new_st)

        # This is an empty, unused DB but must exist.
        shell('mysql -u root -e '
              '"create database if not exists _funfactory_test"')

    def test(self):
        # sys.executable is our tox virtualenv that includes
        # compiled/dev modules.
        p = Popen([sys.executable, 'manage.py', 'test'],
                   stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                   cwd=self.test_repo)
        print p.stdout.read()
        eq_(p.wait(), 0)
