import logging


class AreciboHandler(logging.Handler):
    """An exception log handler that sends tracebacks to Arecibo."""
    def emit(self, record):
        from django.conf import settings
        arecibo = getattr(settings, 'ARECIBO_SERVER_URL', '')

        if arecibo and hasattr(record, 'request'):
            from django_arecibo.tasks import post
            post(record.request, 500)
