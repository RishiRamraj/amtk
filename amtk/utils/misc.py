#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager


def optional(function):
    '''
    Wraps the function in logic that returns None if value is None. Otherwise
    it returns function(value).
    '''
    def result(value):
        return None if value is None else function(value)

    return result


@contextmanager
def suppress_interrupt():
    '''
    To ensure that KeyboardInterrupt doesn't throw a stack trace, this context
    manager suppresses the exception.
    '''
    try:
        yield

    except KeyboardInterrupt:
        pass
