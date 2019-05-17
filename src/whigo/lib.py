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
import logging
import uuid
from contextlib import ContextDecorator
from traceback import format_tb

from cmreslogging.handlers import CMRESHandler


log = logging.getLogger(__name__)


class WhigoScope:
    def __init__(self, scopename):
        self.scopename = scopename
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
            'scope_run_id': self.scoperun_id,
            'scope_name': self.scopename,
            'scope_duration': duration,
            'scope_start_time': self._format_date(self.scope_start_time),
            'scope_end_time': self._format_date(scope_end_time),
            **params
        }
        self.params.update(end_params)
        _emit(self.params)


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
        self.scopename = scopename or scope.get_random_scopename()
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

    @staticmethod
    def get_random_scopename():
        return "unnamed-scope-{}".format(str(uuid.uuid4())[:8])

    def add_params(self, **kwargs):
        self.scope.add_params(**kwargs)


def setup_es_logger(namespace, application, environment, elasticsearch):
    index_name = f"whigo_namespace_{namespace}"
    handler = CMRESHandler(hosts=[{'host': elasticsearch['host'], 'port': elasticsearch['port']}],
                           auth_type=CMRESHandler.AuthType.NO_AUTH,
                           es_index_name=index_name,
                           es_additional_fields={'app': application, 'environment': environment},
                           buffer_size=1000, use_ssl=True)
    log = logging.getLogger(index_name)
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)
    return log


class config(object):

    @classmethod
    def set(cls, config):
        cls.config = config
        cls.logger = setup_es_logger(config['namespace'], config['application'], config['environment'], config['elasticsearch'])

    @classmethod
    def get_logger(cls):
        if not hasattr(cls, 'logger'):
            cls.logger = None
        return cls.logger


def _emit(data, msg=None):
    whigologger = config.get_logger()
    if not whigologger:
        log.warning("No logger found")
        raise Exception

    whigologger.info(msg, extra=data)
