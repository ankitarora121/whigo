import json
import uuid
from pprint import pprint
from sys import stdout

from whigo.core import WhigoSession
from whigo.targets import ElasticSearchTarget

whigo_application_session = None


def get_random_session_name():
    return f'default_session'


_stdout_target = lambda x: stdout.write(json.dumps(x))
_default_targets = [pprint]

def initialize_application_session(targets=None, es_target_config=None, session_name=None, session_data=None):
    # initializes a default module level session
    if es_target_config and targets:
        raise Exception("one of them can be passed")

    if es_target_config:
        session_targets = [ElasticSearchTarget(es_target_config)]
    else:
        session_targets = targets or _default_targets

    session_name = session_name or get_random_session_name()
    session_data = session_data or {}
    global whigo_application_session
    whigo_application_session = WhigoSession(session_name, session_targets, session_data)

def get_application_session():
    global whigo_application_session
    if not whigo_application_session:
        raise Exception("Application session not initialized")
    return whigo_application_session