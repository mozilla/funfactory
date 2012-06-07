"""
Installs a skeleton Django app based on Mozilla's Playdoh.

1. Clones the Playdoh repo
2. Renames the project module to your custom package name
3. Creates a virtualenv
4. Installs/compiles the requirements
5. Creates a local settings file
Read more about it here: http://playdoh.readthedocs.org/
"""
import base64
from contextlib import contextmanager
from datetime import datetime
import logging
import optparse
import os
import re
import shutil
import subprocess
import sys
import textwrap


allow_user_input = True
verbose = True
log = logging.getLogger(__name__)


def clone_repo(pkg, dest, repo, repo_dest, branch):
    """Clone the Playdoh repo into a custom path."""
    git(['clone', '--recursive', '-b', branch, repo, repo_dest])


def init_pkg(pkg, repo_dest):
    """
    Initializes a custom named package module.

    This works by replacing all instances of 'project' with a custom module
    name.
    """
    vars = {'pkg': pkg}
    with dir_path(repo_dest):
        patch("""\
        diff --git a/manage.py b/manage.py
        index 40ebb0a..cdfe363 100755
        --- a/manage.py
        +++ b/manage.py
        @@ -3,7 +3,7 @@ import os
         import sys

         # Edit this if necessary or override the variable in your environment.
        -os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
        +os.environ.setdefault('DJANGO_SETTINGS_MODULE', '%(pkg)s.settings')

         try:
             # For local development in a virtualenv:
        diff --git a/project/settings/base.py b/project/settings/base.py
        index 312f280..c75e673 100644
        --- a/project/settings/base.py
        +++ b/project/settings/base.py
        @@ -7,7 +7,7 @@ from funfactory.settings_base import *
         # If you did not install Playdoh with the funfactory installer script
         # you may need to edit this value. See the docs about installing from a
         # clone.
        -PROJECT_MODULE = 'project'
        +PROJECT_MODULE = '%(pkg)s'

         # Bundles is a dictionary of two dictionaries, css and js, which list css files
         # and js files that can be bundled together by the minify app.
        diff --git a/setup.py b/setup.py
        index 58dbd93..9a38628 100644
        --- a/setup.py
        +++ b/setup.py
        @@ -3,7 +3,7 @@ import os
         from setuptools import setup, find_packages


        -setup(name='project',
        +setup(name='%(pkg)s',
               version='1.0',
               description='Django application.',
               long_description='',
        """ % vars)

        git(['mv', 'project', pkg])
        git(['commit', '-a', '-m', 'Renamed project module to %s' % pkg])


def generate_key(byte_length):
    """Return a true random ascii string that is byte_length long.

    The resulting key is suitable for cryptogrpahy.
    """
    if byte_length < 32:  # at least 256 bit
        raise ValueError('um, %s is probably not long enough for cryptography'
                         % byte_length)
    key = os.urandom(byte_length)
    key = base64.b64encode(key).rstrip('=')  # strip off padding
    key = key[0:byte_length]
    return key


def create_settings(pkg, repo_dest, db_user, db_name, db_password, db_host,
                    db_port):
    """
    Creates a local settings file out of the distributed template.

    This also fills in database settings and generates a secret key, etc.
    """
    vars = {'pkg': pkg,
            'db_user': db_user,
            'db_name': db_name,
            'db_password': db_password or '',
            'db_host': db_host or '',
            'db_port': db_port or '',
            'hmac_date': datetime.now().strftime('%Y-%m-%d'),
            'hmac_key': generate_key(40),
            'secret_key': generate_key(40)}
    with dir_path(repo_dest):
        shutil.copyfile('%s/settings/local.py-dist' % pkg,
                        '%s/settings/local.py' % pkg)
        patch("""\
            --- a/%(pkg)s/settings/local.py
            +++ b/%(pkg)s/settings/local.py
            @@ -9,11 +9,11 @@ from . import base
             DATABASES = {
                 'default': {
                     'ENGINE': 'django.db.backends.mysql',
            -        'NAME': 'playdoh_app',
            -        'USER': 'root',
            -        'PASSWORD': '',
            -        'HOST': '',
            -        'PORT': '',
            +        'NAME': '%(db_name)s',
            +        'USER': '%(db_user)s',
            +        'PASSWORD': '%(db_password)s',
            +        'HOST': '%(db_host)s',
            +        'PORT': '%(db_port)s',
                     'OPTIONS': {
                         'init_command': 'SET storage_engine=InnoDB',
                         'charset' : 'utf8',
            @@ -51,14 +51,14 @@ DEV = True
             # Playdoh ships with Bcrypt+HMAC by default because it's the most secure.
             # To use bcrypt, fill in a secret HMAC key. It cannot be blank.
             HMAC_KEYS = {
            -    #'2012-06-06': 'some secret',
            +    '%(hmac_date)s': '%(hmac_key)s',
             }

             from django_sha2 import get_password_hashers
             PASSWORD_HASHERS = get_password_hashers(base.BASE_PASSWORD_HASHERS, HMAC_KEYS)

             # Make this unique, and don't share it with anybody.  It cannot be blank.
            -SECRET_KEY = ''
            +SECRET_KEY = '%(secret_key)s'

             # Uncomment these to activate and customize Celery:
             # CELERY_ALWAYS_EAGER = False  # required to activate celeryd
            """ % vars)


def create_virtualenv(pkg, repo_dest, python):
    """Creates a virtualenv within which to install your new application."""
    workon_home = os.environ.get('WORKON_HOME')
    venv_cmd = find_executable('virtualenv')
    python_bin = find_executable(python)
    if not python_bin:
        raise EnvironmentError('%s is not installed or not '
                               'available on your $PATH' % python)
    if workon_home:
        # Can't use mkvirtualenv directly here because relies too much on
        # shell tricks. Simulate it:
        venv = os.path.join(workon_home, pkg)
    else:
        venv = os.path.join(repo_dest, '.virtualenv')
    if venv_cmd:
        if not verbose:
            log.info('Creating virtual environment in %r' % venv)
        args = ['--python', python_bin, venv]
        if not verbose:
            args.insert(0, '-q')
        subprocess.check_call([venv_cmd] + args)
    else:
        raise EnvironmentError('Could not locate the virtualenv. Install with '
                               'pip install virtualenv.')
    return venv


def install_reqs(venv, repo_dest):
    """Installs all compiled requirements that can't be shipped in vendor."""
    with dir_path(repo_dest):
        args = ['-r', 'requirements/compiled.txt']
        if not verbose:
            args.insert(0, '-q')
        subprocess.check_call([os.path.join(venv, 'bin', 'pip'), 'install'] +
                              args)


def find_executable(name):
    """
    Finds the actual path to a named command.

    The first one on $PATH wins.
    """
    for pt in os.environ.get('PATH', '').split(':'):
        candidate = os.path.join(pt, name)
        if os.path.exists(candidate):
            return candidate


def patch(hunk):
    args = ['-p1', '-r', '.']
    if not verbose:
        args.insert(0, '--quiet')
    ps = subprocess.Popen(['patch'] + args, stdin=subprocess.PIPE)
    ps.stdin.write(textwrap.dedent(hunk))
    ps.stdin.close()
    rs = ps.wait()
    if rs != 0:
        raise RuntimeError('patch %s returned non-zeo exit '
                           'status %s' % (file, rs))


@contextmanager
def dir_path(dir):
    """with dir_path(path) to change into a directory."""
    old_dir = os.getcwd()
    os.chdir(dir)
    yield
    os.chdir(old_dir)


def git(cmd_args):
    args = ['git']
    cmd = cmd_args.pop(0)
    args.append(cmd)
    if not verbose:
        if cmd != 'mv':  # doh
            args.append('--quiet')
    args.extend(cmd_args)
    if verbose:
        log.info(' '.join(args))
    subprocess.check_call(args)


def resolve_opt(opt, prompt):
    if not opt:
        if not allow_user_input:
            raise ValueError('%s (value was not set, using --no-input)'
                             % prompt)
        opt = raw_input(prompt)
    return opt


def main():
    global allow_user_input, verbose
    ps = optparse.OptionParser(usage='%prog [options]\n' + __doc__)
    ps.add_option('-p', '--pkg', help='Name of your top level project package.')
    ps.add_option('-d', '--dest',
                  help='Destination dir to put your new app. '
                       'Default: %default',
                  default=os.getcwd())
    ps.add_option('-r', '--repo',
                  help='Playdoh repository to clone. Default: %default',
                  default='git://github.com/mozilla/playdoh.git')
    ps.add_option('-b', '--branch',
                  help='Repository branch to clone. Default: %default',
                  default='master')
    ps.add_option('--repo-dest',
                  help='Clone repository into this directory. '
                       'Default: DEST/PKG')
    ps.add_option('--venv',
                  help='Path to an existing virtualenv you want to use. '
                       'Otherwise, a new one will be created for you.')
    ps.add_option('-P', '--python',
                  help='Python interpreter to use in your virtualenv. '
                       'Default: which %default',
                  default='python')
    ps.add_option('--db-user',
                  help='Database user of your new app. Default: %default',
                  default='root')
    ps.add_option('--db-name',
                  help='Database name for your new app. Default: %default',
                  default='playdoh_app')
    ps.add_option('--db-password',
                  help='Database user password. Default: %default',
                  default=None)
    ps.add_option('--db-host',
                  help='Database connection host. Default: %default',
                  default=None)
    ps.add_option('--db-port',
                  help='Database connection port. Default: %default',
                  default=None)
    ps.add_option('--no-input', help='Never prompt for user input',
                  action='store_true', default=False)
    ps.add_option('-q', '--quiet', help='Less output',
                  action='store_true', default=False)
    (options, args) = ps.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s",
                        stream=sys.stdout)
    allow_user_input = not options.no_input
    verbose = not options.quiet
    options.pkg = resolve_opt(options.pkg, 'Top level package name: ')
    if not re.match('[a-zA-Z0-9_]+', options.pkg):
        ps.error('Package name %r can only contain letters, numbers, and '
                 'underscores' % options.pkg)
    if not find_executable('mysql_config'):
        ps.error('Cannot find mysql_config. Please install MySQL!')
    if not options.repo_dest:
        options.repo_dest = os.path.abspath(os.path.join(options.dest,
                                                         options.pkg))
    clone_repo(options.pkg, options.dest, options.repo, options.repo_dest,
               options.branch)
    if options.venv:
        venv = options.venv
    elif os.environ.get('VIRTUAL_ENV'):
        venv = os.environ['VIRTUAL_ENV']
        log.info('Using existing virtualenv in %s' % venv)
    else:
        venv = create_virtualenv(options.pkg, options.repo_dest, options.python)
    install_reqs(venv, options.repo_dest)
    init_pkg(options.pkg, options.repo_dest)
    create_settings(options.pkg, options.repo_dest, options.db_user,
                    options.db_name, options.db_password, options.db_host,
                    options.db_port)
    if verbose:
        log.info('')
        log.info('Aww yeah. Just installed you some Playdoh.')
        log.info('')
        log.info('cd %s' % options.repo_dest)
        if os.environ.get('WORKON_HOME'):
            log.info('workon %s' % options.pkg)
        else:
            log.info('source %s/bin/activate'
                     % venv.replace(options.repo_dest, '.'))
        log.info('python manage.py runserver')
        log.info('')


if __name__ == '__main__':
    main()
