import json
from pprint import pprint
import uuid
from sys import stdout

from whigo.core import WhigoContext
from whigo.targets import ElasticSearchTarget

whigo_application_context = None


def get_random_context_name():
    return f'app_context_{str(uuid.uuid4())}'


_stdout_target = lambda x: stdout.write(json.dumps(x))
_default_targets = [pprint]

def initialize_application_context(targets=None, es_target_config=None, context_name=None, context_data=None):
    # initializes a default module level context
    if es_target_config and targets:
        raise Exception("one of them can be passed")

    if es_target_config:
        context_targets = [ElasticSearchTarget(es_target_config)]
    else:
        context_targets = targets or _default_targets

    context_name = context_name or get_random_context_name()
    context_data = context_data or {}
    global whigo_application_context
    whigo_application_context = WhigoContext(context_name, context_targets, context_data)

def get_application_context():
    global whigo_application_context
    if not whigo_application_context:
        raise Exception("Application context not initialized")
    return whigo_application_context