#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from mock import MagicMock


# To avoid having to import multiple test modules.
main = unittest.main


class TestCase(unittest.TestCase):
    '''
    Minor customisations to the test suite.
    '''
    def shortDescription(self):
        '''
        Use the test names, not the doc strings, to identify tests.
        '''
        return None


def file(lines):
    '''
    Used to create fake files.
    '''
    result = MagicMock()
    result.readlines.return_value = lines
    return result
