import copy
import datetime
import uuid
from contextlib import ContextDecorator
from traceback import format_tb

from whigo.old import whigo_log


class WhigoContext:
    def __init__(self, name, targets, context_data=None):
        self.name = name
        self.targets = targets
        self.context_metadata = dict(  # should be immutable
            context_name=name,
            **context_data
        )
        self.whigo_scope = None

    def push(self, data):
        combined_data = {**data, 'context_metadata': self.context_metadata}
        results = [t(combined_data) for t in self.targets]


def get_random_scopename():
    return "unnamed-scope-{}".format(str(uuid.uuid4())[:8])


class WhigoScope:
    def __init__(self, context: WhigoContext, scope_name=None):
        self.context = context
        self.scope_name = scope_name or get_random_scopename()
        self.scope_run_params = {}
        self._start()

    def _start(self):
        self.scope_start_time = datetime.datetime.now()
        self.scope_metadata = {
            'scope_run_id': str(uuid.uuid4()),
            'scope_name': self.scope_name,
        }

    def _format_date(self, datetime_object):
        return datetime_object.strftime('%Y/%m/%d %H:%M:%S Z')

    def add_params(self, **kwargs):
        self.scope_run_params.update(kwargs)

    def end(self, **kwargs):
        scope_end_time = datetime.datetime.now()
        params = kwargs or {}
        duration = int(((scope_end_time - self.scope_start_time).total_seconds()) * 1000)

        end_metadata = {
            'scope_duration': duration,
            'scope_end_time': self._format_date(scope_end_time),
            'scope_start_time': self._format_date(self.scope_start_time),
        }
        self.scope_metadata.update(end_metadata)
        self.scope_run_params.update(params)
        scope_run_data = self.get_scope_run_data()
        self.context.push(scope_run_data)

    def get_scope_run_data(self):
        return dict(params=self.scope_run_params, metadata=self.scope_metadata)


class WhigoScopeContextDecorator(ContextDecorator):
    """
    Basic Usage:
        with scope('some-scope-name'):
            foo()

    Adding custom params to scope:
        with scope('some-scope-name') as sc:
            num_media_processed = foo()
            sc.add_params(num_media_processed=num_media_processed)
    """

    def __init__(self, context, scope_name=None):
        self.context = context
        self.scope_name = scope_name

    def __enter__(self):
        self.whigo_scope = WhigoScope(self.context, self.scope_name)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
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
