from cmreslogging.handlers import CMRESHandler


def get_es_handler(namespace, application, environment, elasticsearch):
    index_name = f"whigo-{namespace}"
    return CMRESHandler(hosts=[{'host': elasticsearch['host'], 'port': elasticsearch['port']}],
                        auth_type=CMRESHandler.AuthType.NO_AUTH,
                        es_index_name=index_name,
                        es_additional_fields={'app': application, 'environment': environment},
                        buffer_size=1000, use_ssl=True)


class ElasticSearchTarget:
    def __init__(self, config):
        # get_es_handler()
        pass

    def __call__(self, data):
        pass