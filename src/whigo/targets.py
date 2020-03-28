import logging

from cmreslogging.handlers import CMRESHandler


def get_es_handler(cmres_config):
    default_kwargs = dict(
        # hosts=[{'host': elasticsearch['host'], 'port': elasticsearch['port']}],
        auth_type=CMRESHandler.AuthType.NO_AUTH,
        es_index_name=f"whigo-es",
        buffer_size=1000, use_ssl=True
    )
    combined_kwargs = {**default_kwargs, **cmres_config}
    return CMRESHandler(**combined_kwargs)


class ElasticSearchTarget:
    def __init__(self, cmres_config):
        self.handler = get_es_handler(cmres_config)
        self.target_logger = logging.getLogger('whigologger')
        self.target_logger.setLevel(logging.DEBUG)
        self.target_logger.propagate = False
        self.target_logger.addHandler(self.handler)


    def __call__(self, data):
        self.target_logger.info('m', extra=data)
