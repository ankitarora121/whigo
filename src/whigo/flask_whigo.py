from flask import g

from whigo import get_application_context
from whigo.core import WhigoScope


def _get_random_context_name():
    pass

def whigo_flask_before_request():
    g.whigo_scope = WhigoScope(get_application_context(), 'flask_whigo_scope')


def whigo_flask_after_request(response):
    end_params = {
        # request path, ip,
        # response status
    }
    g.whigo_scope.end(whigo_flask=end_params)
    return response



def wrap_flask_app(flask_app, whigo_context):
    flask_app.before_request(whigo_flask_before_request)
