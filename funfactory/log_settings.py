import logging
import logging.handlers

from django.conf import settings

import commonware.log
import cef
import dictconfig


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


base_fmt = ('%(name)s:%(levelname)s %(message)s '
            ':%(pathname)s:%(lineno)s')
use_syslog = settings.HAS_SYSLOG and not settings.DEBUG

cfg = {
    'version': 1,
    'filters': {},
    'formatters': {
        'debug': {
            '()': commonware.log.Formatter,
            'datefmt': '%H:%M:%s',
            'format': '%(asctime)s ' + base_fmt,
        },
        'prod': {
            '()': commonware.log.Formatter,
            'datefmt': '%H:%M:%s',
            'format': '%s: [%%(REMOTE_ADDR)s] %s' % (settings.SYSLOG_TAG,
                                                     base_fmt),
        },
        'cef': {
            '()': cef.SysLogFormatter,
            'datefmt': '%H:%M:%s',
        },
    },
    'handlers': {
        'console': {
            '()': logging.StreamHandler,
            'formatter': 'debug',
        },
        'syslog': {
            '()': logging.handlers.SysLogHandler,
            'facility': logging.handlers.SysLogHandler.LOG_LOCAL7,
            'formatter': 'prod',
        },
        'arecibo': {
            'level': 'ERROR',
            'class': 'funfactory.log.AreciboHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'cef_syslog': {
            '()': logging.handlers.SysLogHandler,
            'facility': logging.handlers.SysLogHandler.LOG_LOCAL4,
            'formatter': 'cef',
        },
        'cef_console': {
            '()': logging.StreamHandler,
            'formatter': 'cef',
        },
        'null': {
            '()': NullHandler,
        }
    },
    'loggers': {
        'django.request': {
            # 'handlers': ['mail_admins', 'arecibo'],
            'handlers': ['mail_admins', 'arecibo'],
            'level': 'ERROR',
            'propagate': False,
        },
        'cef': {
            'handlers': ['cef_syslog' if use_syslog else 'cef_console'],
        }
    },
    'root': {},
}

for key, value in settings.LOGGING.items():
    cfg[key].update(value)

# Set the level and handlers for all loggers.
for logger in cfg['loggers'].values() + [cfg['root']]:
    if 'handlers' not in logger:
        logger['handlers'] = ['syslog' if use_syslog else 'console']
    if 'level' not in logger:
        logger['level'] = settings.LOG_LEVEL
    if logger is not cfg['root'] and 'propagate' not in logger:
        logger['propagate'] = False

dictconfig.dictConfig(cfg)

