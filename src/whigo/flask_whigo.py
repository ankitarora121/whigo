from flask import g, request

from whigo import get_application_context
from whigo.core import WhigoScope


def wrap_flask_app(flask_app, app_name):
    def whigo_flask_before_request():
        g.whigo_scope = WhigoScope(get_application_context(), f'flask-request-scope:{app_name}')

    def whigo_flask_after_request(response):
        end_params = {
            'request': {
                'url': request.url,
                'path': request.path,
                'method': request.method,
                'remote_addr': request.remote_addr
            }
        }
        g.whigo_scope.end(whigo_flask=end_params)
        return response

    flask_app.before_request(whigo_flask_before_request)
    flask_app.after_request(whigo_flask_after_request)
