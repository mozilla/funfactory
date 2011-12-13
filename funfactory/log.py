import logging

from django.conf import settings
from django.http import HttpRequest

import commonware


class AreciboHandler(logging.Handler):
    """An exception log handler that sends tracebacks to Arecibo."""
    def emit(self, record):
        from django.conf import settings
        arecibo = getattr(settings, 'ARECIBO_SERVER_URL', '')

        if arecibo and hasattr(record, 'request'):
            from django_arecibo.tasks import post
            post(record.request, 500)


def log_cef(name, severity=logging.INFO, env=None, username='none',
            signature=None, **kwargs):
    """
    Wraps cef logging function so we don't need to pass in the config
    dictionary every time. See bug 707060. ``env`` can be either a request
    object or just the request.META dictionary.
    """

    cef_logger = commonware.log.getLogger('cef')

    c = {'product': settings.CEF_PRODUCT,
         'vendor': settings.CEF_VENDOR,
         'version': settings.CEF_VERSION,
         'device_version': settings.CEF_DEVICE_VERSION,}

    # The CEF library looks for some things in the env object like
    # REQUEST_METHOD and any REMOTE_ADDR stuff.  Django not only doesn't send
    # half the stuff you'd expect, but it specifically doesn't implement
    # readline on its FakePayload object so these things fail.  I have no idea
    # if that's outdated code in Django or not, but andym made this
    # <strike>awesome</strike> less crappy so the tests will actually pass.
    # In theory, the last part of this if() will never be hit except in the
    # test runner.  Good luck with that.
    if isinstance(env, HttpRequest):
        r = env.META.copy()
    elif isinstance(env, dict):
        r = env
    else:
        r = {}

    # Drop kwargs into CEF config array, then log.
    c['environ'] = r
    c.update({
        'username': username,
        'signature': signature,
        'data': kwargs,
    })

    cef_logger.log(severity, name, c)
