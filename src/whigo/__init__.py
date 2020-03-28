from whigo.application_context import initialize_application_context, whigo_application_context, get_application_context
from whigo.core import WhigoScopeContextDecorator
from whigo.flask_whigo import wrap_flask_app

initialize = initialize_application_context

initialize()

def scope(*args, **kwargs):
    return WhigoScopeContextDecorator(get_application_context(), *args, **kwargs)
