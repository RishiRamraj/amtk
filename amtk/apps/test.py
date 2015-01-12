#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
from amtk.utils import testcase as unittest
from mock import patch, MagicMock


# To be tested.
from amtk.apps import record


class Record(unittest.TestCase):
    '''
    Tests for functions in the record module. These tests are fairly mocky.
    '''
    def test_callback(self):
        '''
        A test for the callback function.
        '''
        # Create test data.
        channel = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = 'test'

        # Run the test.
        record.callback(channel, method, properties, body)

    @patch('amtk.apps.record.messages')
    def test_record(self, messages):
        '''
        A test for the record function.
        '''
        # Create test data.
        args = MagicMock()
        messages.connect.return_value = (MagicMock(), MagicMock())

        # Run the test.
        record.record(args)

    @patch('amtk.apps.record.record')
    @patch('amtk.apps.record.options')
    def test_main(self, options, record):
        '''
        A test for the main function.
        '''
        # Run the test.
        record.main()


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
