#!/usr/bin/env python
# -*- coding: utf-8 -*-


def optional(function, value):
    '''
    Returns function called with value if value is not None. Returns None
    otherwise.
    '''
    return None if value is None else function(value)
