import logging

from django.conf import settings

import settings_base

log = logging.getLogger('funfactory')


def absolutify(url):
    """Takes a URL and prepends the SITE_URL"""
    site_url = getattr(settings, 'SITE_URL', False)

    # If we don't define it explicitly
    if not site_url:
        protocol = settings.PROTOCOL
        hostname = settings.DOMAIN
        port = settings.PORT
        if (protocol, port) in (('https://', 443), ('http://', 80)):
            site_url = ''.join(map(str, (protocol, hostname)))
        else:
            site_url = ''.join(map(str, (protocol, hostname, ':', port)))

    return site_url + url


def get_middleware(exclude):
    """
    Returns the default funfactory MIDDLEWARE_CLASSES list without the
    middlewares listed in exclude.
    """

    return filter(lambda m: m not in exclude, settings_base.MIDDLEWARE_CLASSES)


def get_apps(exclude):
    """
    Returns the default funfactory INSTALLED_APPS list without the apps
    listed in exclude.
    """

    return filter(lambda a: a not in exclude, settings_base.INSTALLED_APPS)


def get_template_context_processors(exclude):
    """
    Returns the default funfactory TEMPLATE_CONTEXT_PROCESSORS without the
    processors listed in exclude.
    """

    return filter(lambda p: p not in exclude,
        settings_base.TEMPLATE_CONTEXT_PROCESSORS)
