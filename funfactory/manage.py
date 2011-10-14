#!/usr/bin/env python
import logging
import os
import site
import sys
import warnings


current_settings = None
execute_manager = None
log = logging.getLogger(__name__)
ROOT = None


def path(*a):
    if ROOT is None:
        _not_setup()
    return os.path.join(ROOT, *a)


def setup_environ(manage_file, settings=None):
    """Sets up a Django app within a manage.py file.

    Keyword Arguments

    **settings**
        An imported settings module. Without this, playdoh tries to import
        these modules (in order): settings_local, settings

    """
    # sys is global to avoid undefined local
    global sys, current_settings, execute_manager, ROOT

    ROOT = os.path.dirname(os.path.abspath(manage_file))

    # Adjust the python path and put local packages in front.
    prev_sys_path = list(sys.path)

    # Make settings_local importable
    sys.path.append(ROOT)
    # Give precedence to your app's parent dir, which contains __init__.py
    sys.path.append(os.path.abspath(os.path.join(ROOT, os.pardir)))

    site.addsitedir(path('apps'))
    site.addsitedir(path('lib'))

    # Local (project) vendor library
    site.addsitedir(path('vendor-local'))
    site.addsitedir(path('vendor-local/lib/python'))

    # Global (upstream) vendor library
    site.addsitedir(path('vendor'))
    site.addsitedir(path('vendor/lib/python'))

    # Move the new items to the front of sys.path. (via virtualenv)
    new_sys_path = []
    for item in list(sys.path):
        if item not in prev_sys_path:
            new_sys_path.append(item)
            sys.path.remove(item)
    sys.path[:0] = new_sys_path

    from django.core.management import execute_manager, setup_environ
    if not settings:
        if os.path.isfile(os.path.join(ROOT, 'settings_local.py')):
            import settings_local as settings
            warnings.warn("Using settings_local.py is deprecated. See "
                     "http://playdoh.readthedocs.org/en/latest/upgrading.html",
                          DeprecationWarning)
        else:
            import settings
    current_settings = settings
    validate_settings(settings)

    # If we want to use django settings anywhere, we need to set up the
    # required environment variables.
    setup_environ(settings)

    # Import for side-effect: configures logging handlers.
    # pylint: disable-msg=W0611
    import log_settings
    # Monkey-patch django forms to avoid having to use Jinja2's |safe
    # everywhere.
    import safe_django_forms
    safe_django_forms.monkeypatch()

    # Monkey-patch Django's csrf_protect decorator to use session-based CSRF
    # tokens:
    if 'session_csrf' in settings.INSTALLED_APPS:
        import session_csrf
        session_csrf.monkeypatch()

    # Configure Celery (optional)
    if 'djcelery' in settings.INSTALLED_APPS:
        import djcelery
        djcelery.setup_loader()


def validate_settings(settings):
    from django.core.exceptions import ImproperlyConfigured
    if settings.SECRET_KEY == '':
        msg = 'settings.SECRET_KEY cannot be blank! Check your local settings'
        if settings.DEBUG:
            warnings.warn(msg)
        else:
            raise ImproperlyConfigured(msg)

    if getattr(settings, 'SESSION_COOKIE_SECURE', None) is None:
        msg = ('settings.SESSION_COOKIE_SECURE should be set to True; '
               'otherwise, your session ids can be intercepted over HTTP!')
        if settings.DEBUG:
            warnings.warn(msg)
        else:
            raise ImproperlyConfigured(msg)

def _not_setup():
    raise EnvironmentError(
            'setup_environ() has not been called for this process')


def main():
    if current_settings is None:
        _not_setup()
    execute_manager(current_settings)
