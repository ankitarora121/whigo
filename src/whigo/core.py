import datetime
import uuid
from contextlib import ContextDecorator
from traceback import format_tb

from whigo.util import AltContextDecorator


class WhigoSession:
    def __init__(self, name, targets, session_data=None):
        self.name = name
        self.targets = targets
        self.session_metadata = dict(  # should be immutable
            session_name=name,
            **(session_data or {})
        )
        self.whigo_scope = None

    def push(self, scope_run_data):
        combined_data = {'scope': scope_run_data, 'session': self.session_metadata}
        results = [t(combined_data) for t in self.targets]


def get_random_scopename():
    return "scope-{}".format(str(uuid.uuid4())[:8])


class WhigoScope:
    def __init__(self, session: WhigoSession, scope_name=None, auto_flask_scope_detection=True):
        self.session = session
        self.scope_name = scope_name or get_random_scopename()
        self.scope_run_params = {}
        self.auto_flask_scope_detection = False
        self.scope_run_id = f'sr-{str(uuid.uuid4())}'
        self._start()

    def _start(self):

        self.scope_start_time = datetime.datetime.now()
        self.scope_metadata = {
            'run_id': self.scope_run_id,
            'name': self.scope_name,
        }


    def _format_date(self, datetime_object):
        return datetime_object.strftime('%Y/%m/%d %H:%M:%S Z')

    def add_params(self, **kwargs):
        self.scope_run_params.update(kwargs)

    def end(self, **kwargs):
        # if self.auto_flask_scope_detection:
        #     try:
        #         from flask import g
        #         detected_flask_whigo_scope = getattr(g, 'whigo_scope', None)
        #         self.scope_metadata['detected_flask_whigo_scope'] = detected_flask_whigo_scope.scope_run_id
        #     except Exception as e:
        #         pass

        scope_end_time = datetime.datetime.now()
        params = kwargs or {}
        duration = int(((scope_end_time - self.scope_start_time).total_seconds()) * 1000)

        end_metadata = {
            'duration': duration,
            'end_time': self._format_date(scope_end_time),
            'start_time': self._format_date(self.scope_start_time),
        }
        self.scope_metadata.update(end_metadata)
        self.scope_run_params.update(params)
        scope_run_data = self.get_scope_run_data()
        self.session.push(scope_run_data)

    def get_scope_run_data(self):
        return dict(params=self.scope_run_params, metadata=self.scope_metadata)


class WhigoScopeContextDecorator(AltContextDecorator):
    """
    Basic Usage:
        with scope('some-scope-name'):
            foo()

    Adding custom params to scope:
        with scope('some-scope-name') as sc:
            num_media_processed = foo()
            sc.add_params(num_media_processed=num_media_processed)
    """

    def __init__(self, session, scope_name=None):
        self.session = session
        self.scope_name = scope_name

    def __enter__(self):
        self.whigo_scope = WhigoScope(self.session, self.scope_name)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        func = getattr(self, 'func', None)
        if func:
            func_details = {
                'name': func.__name__,
                'module': func.__module__
            }
            self.whigo_scope.add_params(**dict(function_details=func_details))

        is_success = not bool(exc)
        if not is_success:
            formatted_traceback = format_tb(exc_tb)
            self.whigo_scope.add_params(exception_class_name=exc_type.__qualname__,
                                        exception_traceback=formatted_traceback,
                                        exception_str=str(exc))
        self.whigo_scope.end(is_success=is_success)
        return False

    def add_params(self, **kwargs):
        self.whigo_scope.add_params(**kwargs)
