# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from time import time
import logging

from lab import B
from plum import Dispatcher, Self, Referentiable

__all__ = ['Cache']

log_cache_call = logging.getLogger(__name__ + '.call')
log_cache_lab = logging.getLogger(__name__ + '.lab')


class Cache(Referentiable):
    """Cache for kernels and means.

    Caches output of calls. Also caches calls to `B.*`: call instead `cache.*`.
    """
    dispatch = Dispatcher(in_class=Self)

    def __init__(self):
        self._cache_call = {}
        self._cache_lab = {}
        self._start = time()
        self.depth = 0

    @dispatch(object)
    def _resolve(self, key):
        return id(key)

    @dispatch({int, str, bool})
    def _resolve(self, key):
        return key

    @dispatch({tuple, list})
    def _resolve(self, key):
        return tuple(self._resolve(x) for x in key)

    def __getitem__(self, key):
        return self._cache_call[self._resolve(key)]

    def __setitem__(self, key, output):
        self._cache_call[self._resolve(key)] = output

    def __getattr__(self, f):
        def call_cached(*args, **kw_args):
            # Let the key depend on the function name...
            key = (f,)

            # ...on the arguments...
            key += self._resolve(args)

            # ...and on the keyword arguments.
            if len(kw_args) > 0:
                # First, sort keyword arguments according to keys.
                items = tuple(sorted(kw_args.items(), key=lambda x: x[0]))
                key += self._resolve(items)

            # Cached execution.
            if key in self._cache_lab:
                out = self._cache_lab[key]
                log_cache_lab.debug('%4.0f ms: Hit for "%s".', self.dur(), f)
                return out
            else:
                self._cache_lab[key] = getattr(B, f)(*args, **kw_args)
                return self._cache_lab[key]

        return call_cached

    def dur(self):
        return (time() - self._start) * 1e3


def cache(f):
    """A decorator for `__call__` methods to cache their outputs."""

    def __call__(self, *args):
        inputs, cache = args[:-1], args[-1]
        try:
            out = cache[self, inputs]
            log_cache_call.debug('%4.0f ms: Hit for "%s".',
                                 cache.dur(), type(self).__name__)
            return out
        except KeyError:
            pass

        # Try reverse of arguments.
        try:
            out = B.transpose(cache[self, tuple(reversed(inputs))])
            log_cache_call.debug('%4.0f ms: Reversed hit for "%s".',
                                 cache.dur(), type(self).__name__)
            return out
        except KeyError:
            log_cache_call.debug('%4.0f ms: Miss for "%s": start; depth: %d.',
                                 cache.dur(), type(self).__name__, cache.depth)
            cache.depth += 1
            cache[self, inputs] = f(self, *args)
            cache.depth -= 1
            log_cache_call.debug('%4.0f ms: Miss for "%s": end.',
                                 cache.dur(), type(self).__name__)
            return cache[self, inputs]

    return __call__
