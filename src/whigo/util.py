from functools import wraps


class AltContextDecorator(object):
    "A base class or mixin that enables context managers to work as decorators."

    def _recreate_cm(self):
        """Return a recreated instance of self.

        Allows an otherwise one-shot context manager like
        _GeneratorContextManager to support use as
        a decorator via implicit recreation.

        This is a private interface just for _GeneratorContextManager.
        See issue #11647 for details.
        """
        return self

    def __call__(self, func):
        self.func = func
        @wraps(func)
        def inner(*args, **kwds):
            with self._recreate_cm():
                return func(*args, **kwds)
        return inner