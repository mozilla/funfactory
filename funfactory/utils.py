from django.conf import settings


def absolutify(url):
    """Takes a URL and prepends the SITE_URL"""
    protocol = settings.PROTOCOL
    hostname = settings.DOMAIN
    port = settings.PORT
    if (protocol, port) in (('https://', 443), ('http://', 80)):
        return ''.join(map(str, (protocol, hostname, url)))
    else:
        return ''.join(map(str, (protocol, hostname, ':', port, url)))
