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
    @patch('amtk.apps.record.builtins')
    def test_callback(self, builtins):
        '''
        A test for the callback function.
        '''
        # Create test data.
        channel = MagicMock()
        method = MagicMock()
        method.exchange = 'exchange'
        method.routing_key = 'routing_key'
        properties = MagicMock()
        properties.message_id = 'message_id'
        properties.user_id = 'user_id'
        properties.reply_to = 'reply_to'
        properties.correlation_id = 'correlation_id'
        properties.content_type = 'content_type'
        properties.content_encoding = 'content_encoding'
        properties.timestamp = 123
        properties.expiration = 456
        body = 'body'

        # Run the test.
        record.callback(channel, method, properties, body)

        # Check the result.
        expected = ('{"body": "body", "exchange": "exchange", "creation_time":'
                    ' 123, "correlation_id": "correlation_id", "content_type":'
                    ' "content_type", "user_id": "user_id", "routing_key":'
                    ' "routing_key", "content_encoding": "content_encoding",'
                    ' "reply_to": "reply_to", "absolute_expiry_time": 456,'
                    ' "message_id": "message_id"}')
        builtins.print_text.assert_called_once_with(expected)

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
