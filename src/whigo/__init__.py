from whigo.application_session import initialize_application_session, whigo_application_session, get_application_session
from whigo.core import WhigoScopeContextDecorator
from whigo.flask_whigo import wrap_flask_app

initialize = initialize_application_session

initialize()

def scope(*args, **kwargs):
    return WhigoScopeContextDecorator(get_application_session(), *args, **kwargs)
