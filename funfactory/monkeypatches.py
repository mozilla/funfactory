import logging
from django.conf import settings


def patch():
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

    logging.debug("Note: funfactory monkey patches executed in %s" % __file__)
