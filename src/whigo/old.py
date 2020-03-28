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

import logging
from pprint import pprint
from typing import Callable

from dataclasses import dataclass
import sys
from cmreslogging.handlers import CMRESHandler

log = logging.getLogger(__name__)


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


@dataclass
class WhigoConfig:
    outputCallable: Callable[[dict],None]

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
    pprint(data)
    # whigologger = WhigoLogger.get()
    # whigologger.info(json.dumps(data), extra=data)
