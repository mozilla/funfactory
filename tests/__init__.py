from functools import partial
import os
import shutil
import subprocess
from subprocess import check_call, Popen
import sys

from nose.plugins import Plugin

from funfactory import manage


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PLAYDOH = os.path.join(ROOT, '.playdoh', 'funtestapp')
shell = partial(check_call, shell=True)
DB_USER = os.environ.get('FF_DB_USER', 'root')
DB_PASS = os.environ.get('FF_DB_PASS', '')
DB_NAME = os.environ.get('FF_DB_NAME', '_funfactory_test')
FF_PLAYDOH_REMOTE = os.environ.get('FF_PLAYDOH_REMOTE',
                                   'git://github.com/mozilla/playdoh.git')
FF_PLAYDOH_BRANCH = os.environ.get('FF_PLAYDOH_BRANCH', 'master')


def test_root():
    assert os.path.exists(os.path.join(ROOT, 'setup.py')), (
                    'This does not appear to be the root dir: %s' % ROOT)


class FunFactoryTests(Plugin):
    """Enables the fun factory test suite."""
    __test__ = False  # Nose: do not collect as test
    name = 'ff-tests'
    score = 999  # needs to execute early

    def options(self, parser, env=os.environ):
        super(FunFactoryTests, self).options(parser, env=env)
        self.parser = parser

    def configure(self, options, conf):
        super(FunFactoryTests, self).configure(options, conf)
        self.enabled = True  # Enables the plugin without a cmd line flag
        self.options = options

    def begin(self):
        if not os.path.exists(PLAYDOH):
            container = os.path.abspath(os.path.join(PLAYDOH, '..'))
            if not os.path.exists(container):
                os.mkdir(container)
            check_call(['git', 'clone', '--recursive',
                        '--branch', FF_PLAYDOH_BRANCH,
                        FF_PLAYDOH_REMOTE,
                        PLAYDOH])
        else:
            proj_sh = partial(shell, cwd=PLAYDOH)
            proj_sh('git pull origin %s' % FF_PLAYDOH_BRANCH)
            proj_sh('git submodule sync -q')
            proj_sh('git submodule update --init --recursive')

        st = os.path.join(PLAYDOH, 'project', 'settings', 'local.py')
        if os.path.exists(st):
            os.unlink(st)
        shutil.copy(os.path.join(PLAYDOH, 'project', 'settings',
                                 'local.py-dist'),
                    st)

        with open(st, 'r') as f:
            new_st = f.read()
            new_st = new_st.replace("'USER': 'root'",
                                    "'USER': '%s'" % DB_USER)
            new_st = new_st.replace("'PASSWORD': ''",
                                    "'PASSWORD': '%s'" % DB_PASS)
            new_st = new_st.replace("'NAME': 'playdoh_app'",
                                    "'NAME': '%s'" % DB_NAME)
            new_st = new_st.replace("SECRET_KEY = ''",
                                    "SECRET_KEY = 'testinglolz'")
            new_st = new_st + "\nfrom . import base\nINSTALLED_APPS = list(base.INSTALLED_APPS) + " \
                     "['django.contrib.admin']\n"

        with open(st, 'w') as f:
            f.write(new_st)

        extra = ''
        if DB_PASS:
            extra = '--password=%s' % DB_PASS
        shell('mysql -u %s %s -e "create database if not exists %s"'
              % (DB_USER, extra, DB_NAME))
        check_call([sys.executable, 'manage.py', 'syncdb', '--noinput'],
                   cwd=PLAYDOH)

        # For in-process tests:
        wd = os.getcwd()
        os.chdir(PLAYDOH)  # Simulate what happens in a real app.
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
        try:
            manage.setup_environ(os.path.join(PLAYDOH, 'manage.py'))
        finally:
            os.chdir(wd)
        # Puts path back to this dev version of funfactory:
        sys.path.insert(0, ROOT)
