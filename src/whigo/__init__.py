from whigo.application_context import initialize_application_context, whigo_application_context
from whigo.core import WhigoScopeContextDecorator

initialize = initialize_application_context


def scope(*args, **kwargs):
    return WhigoScopeContextDecorator(whigo_application_context, *args, **kwargs)
