"""
config example:

{
    'namespace': 'coinswitch',
    'application': 'csweb',
    'environment': 'prod',
    'elasticsearch': {
        'host': 'localhost',
        'port': 8601
    }
}
"""

import datetime
import json
import logging
import uuid
from contextlib import ContextDecorator
from traceback import format_tb

import sys
from cmreslogging.handlers import CMRESHandler

log = logging.getLogger(__name__)


class WhigoScope:
    def __init__(self, scopename=None):
        self.scopename = scopename or WhigoScope.get_random_scopename()
        self.params = {}
        self.scoperun_id = str(uuid.uuid4())
        self.scope_start_time = datetime.datetime.now()

    def _format_date(self, datetime_object):
        return datetime_object.strftime('%Y/%m/%d %H:%M:%S Z')

    def add_params(self, **kwargs):
        self.params.update(kwargs)

    def end(self, **kwargs):
        scope_end_time = datetime.datetime.now()
        params = kwargs or {}
        duration = int(((scope_end_time - self.scope_start_time).total_seconds()) * 1000)
        end_params = {
            'whigo': {
                'scope_run_id': self.scoperun_id,
                'scope_name': self.scopename,
                'scope_duration': duration,
                'scope_start_time': self._format_date(self.scope_start_time),
                'scope_end_time': self._format_date(scope_end_time),
            },
            'params': {**params}
        }
        self.params.update(end_params)
        whigo_log(self.params)

    @staticmethod
    def get_random_scopename():
        return "unnamed-scope-{}".format(str(uuid.uuid4())[:8])


class scope(ContextDecorator):
    """
    Basic Usage:
        with scope('some-scope-name'):
            foo()

    Adding custom params to scope:
        with scope('some-scope-name') as sc:
            num_media_processed = foo()
            sc.add_params(num_media_processed=num_media_processed)
    """

    def __init__(self, scopename=None):
        self.scopename = scopename
        self.params = {}

    def __enter__(self):
        self.scope = WhigoScope(self.scopename)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        is_success = not bool(exc)
        if not is_success:
            formatted_traceback = format_tb(exc_tb)
            self.scope.add_params(exception_class_name=exc_type.__qualname__, exception_traceback=formatted_traceback, exception_str=str(exc))
        self.scope.end(is_success=is_success)
        return False

    def add_params(self, **kwargs):
        self.scope.add_params(**kwargs)


def get_es_handler(namespace, application, environment, elasticsearch):
    index_name = f"whigo-{namespace}"
    return CMRESHandler(hosts=[{'host': elasticsearch['host'], 'port': elasticsearch['port']}],
                        auth_type=CMRESHandler.AuthType.NO_AUTH,
                        es_index_name=index_name,
                        es_additional_fields={'app': application, 'environment': environment},
                        buffer_size=1000, use_ssl=True)


class WhigoLogger:
    __DEFAULT_WHIGO_LOGGER_NAME = 'whigo-logger'
    __DEFAULT_WHIGO_NAMESPACE = 'default-whigo-namespace'
    __DEFAULT_WHIGO_APPLICATION = 'default-whigo-application'
    __DEFAULT_WHIGO_ENVIRONMENT = 'default-whigo-environment'

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    logger = logging.getLogger(__DEFAULT_WHIGO_LOGGER_NAME)
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.DEBUG)

    @classmethod
    def configure(cls, cfg):
        namespace = cfg.get('namespace', cls.__DEFAULT_WHIGO_NAMESPACE)
        application = cfg.get('application', cls.__DEFAULT_WHIGO_APPLICATION)
        environment = cfg.get('environment', cls.__DEFAULT_WHIGO_ENVIRONMENT)
        elasticsearch = cfg.get('elasticsearch', None)
        cls.es_handler = get_es_handler(namespace, application, environment, elasticsearch)
        cls.logger.setLevel(logging.DEBUG)
        cls.logger.addHandler(cls.es_handler)

    @classmethod
    def get(cls):
        return cls.logger

    @classmethod
    def clear(cls):
        cls.es_handler = None
        cls.logger.handlers = [cls.stdout_handler]


class config(object):

    @classmethod
    def set(cls, cfg):
        cls.cfg = cfg
        WhigoLogger.configure(cfg)

    @classmethod
    def get(cls):
        return getattr(cls, 'cfg', None)

    @classmethod
    def clear(cls):
        cls.cfg = None
        WhigoLogger.clear()


def whigo_log(data):
    whigologger = WhigoLogger.get()
    whigologger.info(json.dumps(data), extra=data)
