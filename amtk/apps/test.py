#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
from amtk.utils import testcase as unittest
from mock import patch, MagicMock
import json


# To be tested.
from amtk.apps import record, play


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


class Play(unittest.TestCase):
    '''
    Tests for functions in the play module.
    '''
    def check_wait(self, time, timing, last, expected):
        '''
        Many of the tests for wait follow the same pattern.
        '''
        # Reset the sleep function; otherwise called once will
        # be false on the second iteration.
        time.sleep = MagicMock()

        # Create test data.
        args = MagicMock()
        args.timing = timing
        # Thu, 01 Jan 2015 00:00:00 GMT
        last = last
        # Thu, 01 Jan 2015 00:01:00 GMT
        current = 1420070460

        # Run the test.
        play.wait(args, last, current)

        # Check the result.
        time.sleep.assert_called_once_with(expected)

    @patch('amtk.apps.play.time')
    def test_wait(self, time):
        '''
        Tests the wait function.
        '''
        # Thu, 01 Jan 2015 00:00:00 GMT
        last = 1420070400

        # Run the tests.
        self.check_wait(time, None, last, 60)
        self.check_wait(time, None, None, 0)
        self.check_wait(time, 0, last, 0)
        self.check_wait(time, 1, last, 1)
        self.check_wait(time, -1, last, 60)

    def check_publish(self, routing_key):
        '''
        Structure for testing the publish function.
        '''
        # Create fake data.
        timestamp = None
        args = MagicMock()
        args.routing_key = routing_key
        args.mandatory = 'no'
        args.immediate = 'no'
        args.exchange = 'test'
        channel = MagicMock()
        data = {
            'creation_time': 123,
            'routing_key': 'routing_key',
            'content_type': 'content_type',
            'content_encoding': 'content_encoding',
            'correlation_id': 'correlation_id',
            'reply_to': 'reply_to',
            'absolute_expiry_time': 456,
            'message_id': 'message_id',
            'user_id': 'user_id',
            'body': 'body',
        }

        # Run the test.
        play.publish(timestamp, args, channel, data)

    @patch('amtk.apps.play.pika')
    @patch('amtk.apps.play.wait')
    def test_publish(self, wait, pika):
        '''
        Tests the publish function.
        '''
        self.check_publish(None)
        self.check_publish('routing_key')

    @patch('amtk.apps.play.builtins')
    @patch('amtk.apps.play.publish')
    @patch('amtk.apps.play.messages')
    def test_play(self, messages, publish, builtins):
        '''
        Tests the play function.
        '''
        # Create fake data.
        args = MagicMock()
        connection = MagicMock()
        channel = MagicMock()
        messages.connect.return_value = (
            connection,
            channel,
        )
        args.data.readlines.return_value = (
            json.dumps({'name': 'message 1'}),
            'invalid',
        )

        # Run the test.
        play.play(args)

        # Check the result.
        self.assertTrue(builtins.print_text.called)
        self.assertTrue(publish.called)
        self.assertTrue(channel.close.called)
        self.assertTrue(connection.close.called)

    @patch('amtk.apps.play.play')
    @patch('amtk.apps.play.options')
    def test_main(self, options, play):
        '''
        A test for the main function.
        '''
        # Run the test.
        play.main()


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
