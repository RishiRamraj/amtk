#!/usr/bin/env python
# -*- coding: utf-8 -*-


def optional(function):
    '''
    Wraps the function in logic that returns None if value is None. Otherwise
    it returns function(value).
    '''
    def result(value):
        return None if value is None else function(value)

    return result
