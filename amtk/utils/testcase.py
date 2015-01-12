#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest


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
