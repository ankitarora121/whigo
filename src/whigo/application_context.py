import uuid
from sys import stdout

from whigo.core import WhigoContext
from whigo.targets import ElasticSearchTarget

whigo_application_context = None


def get_random_context_name():
    return f'context_{str(uuid.uuid4())}'


def initialize_application_context(target=stdout, es_target_config=None, context_name=None, context_data=None):
    # initializes a default module level context
    if es_target_config and target:
        raise Exception("one of them can be passed")

    target = target or ElasticSearchTarget(es_target_config)

    context_name = context_name or get_random_context_name()
    context_data = context_data or {}
    context_name = f'app_context_{context_name}'
    global whigo_application_context
    whigo_application_context = WhigoContext(context_name, target, context_data)
