#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
from amtk.utils import testcase as unittest
from mock import patch, MagicMock
import json
import datetime
import pytz
import dateutil.parser

# To be tested.
from amtk.apps import record, play


# Timestamp constants.
parse = lambda value: datetime.datetime.fromtimestamp(value, pytz.utc)
TIMESTAMPS = {
    'current': (
        1420070460,
        '2015-01-01T00:01:00.01+00:00',
        dateutil.parser.parse('2015-01-01T00:01:00.001+00:00'),
    ),
    'last': (
        1420070400,
        '2015-01-01T00:00:00+00:00',
        parse(1420070400),
    ),
    'created': (
        1421603064,
        '2015-01-18T17:44:24+00:00',
        parse(1421603064),
    ),
}


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
        properties.timestamp = TIMESTAMPS['created'][0]
        properties.expiration = None
        body = 'body'

        # Run the test.
        record.callback(channel, method, properties, body)

        # Check the result.
        expected = ('{"body": "body", "exchange": "exchange", "creation_time":'
                    ' "%s", "correlation_id": '
                    '"correlation_id", "content_type": "content_type", '
                    '"user_id": "user_id", "routing_key": "routing_key", '
                    '"content_encoding": "content_encoding", "reply_to": '
                    '"reply_to", "absolute_expiry_time": '
                    'null, "message_id": "message_id"}')
        value = TIMESTAMPS['created'][1]
        builtins.print_text.assert_called_once_with(expected % value)

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
    @patch('amtk.apps.play.time')
    def check_wait(self, timing, last, expected, time):
        '''
        Many of the tests for wait follow the same pattern.
        '''
        # Create test data.
        args = MagicMock()
        args.timing = timing
        last = last
        current = TIMESTAMPS['current'][2]

        # Run the test.
        play.wait(args, last, current)

        # Check the result.
        time.sleep.assert_called_once_with(expected)

    def test_wait(self):
        '''
        Tests the wait function.
        '''
        last = TIMESTAMPS['last'][2]

        # Run the tests.
        self.check_wait(None, last, 60.001)
        self.check_wait(None, None, 0)
        self.check_wait(0, last, 0)
        self.check_wait(1, last, 1)
        self.check_wait(-1, last, 60.001)

    @patch('amtk.apps.play.pika')
    @patch('amtk.apps.play.wait')
    def check_publish(self, routing_key, wait, pika, line=None):
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
            'creation_time': TIMESTAMPS['created'][1],
            'routing_key': 'routing_key',
            'content_type': 'content_type',
            'content_encoding': 'content_encoding',
            'correlation_id': 'correlation_id',
            'reply_to': 'reply_to',
            'absolute_expiry_time': None,
            'message_id': 'message_id',
            'user_id': 'user_id',
            'body': 'body',
        }
        line = line if line else json.dumps(data)

        # Run the test.
        result = play.publish(timestamp, args, channel, line)

        # Return the results.
        properties = pika.spec.BasicProperties
        basic_publish = channel.basic_publish
        return result, properties, basic_publish

    @patch('amtk.apps.play.builtins')
    def test_publish(self, builtins):
        '''
        A positive test for the publish function. The routing key is not
        overridden. builtins is mocked to ensure that the json is properly
        parsed.
        '''
        # Create fake data.
        routing_key = None

        # Run the test.
        result = self.check_publish(routing_key)
        result, properties, basic_publish = result

        # Check the result.
        self.assertFalse(builtins.print_text.called)
        self.assertEqual(result, TIMESTAMPS['created'][2])

        # Check message properties.
        expected = {
            'user_id': u'user_id',
            'timestamp': TIMESTAMPS['created'][0],
            'correlation_id': u'correlation_id',
            'expiration': None,
            'content_type': u'content_type',
            'reply_to': u'reply_to',
            'message_id': u'message_id',
            'content_encoding': u'content_encoding',
        }
        self.assertEqual(properties.call_args[1], expected)

        # Check the content sent to the channel.
        expected = {
            'body': u'body',
            'mandatory': False,
            'exchange': 'test',
            'routing_key': u'routing_key',
            'immediate': False,
            'properties': properties.return_value,
        }
        self.assertEqual(basic_publish.call_args[1], expected)

    def test_publish_routing_key(self):
        '''
        Tests routing key override.
        '''
        # Create fake data.
        routing_key = 'override'

        # Run the test.
        result = self.check_publish(routing_key)
        result, properties, basic_publish = result

        # Check the result.
        value = basic_publish.call_args[1]['routing_key']
        self.assertEqual(value, routing_key)

    @patch('amtk.apps.play.builtins')
    def test_publish_bad_json(self, builtins):
        '''
        The line given could not be parsed.
        '''
        # Create fake data.
        routing_key = None
        line = '{bad json'

        # Run the test.
        result = self.check_publish(routing_key, line=line)
        result, properties, basic_publish = result

        # Check the result.
        self.assertTrue(builtins.print_text.called)
        self.assertIsNone(result)

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
            json.dumps({'name': 'message 2'}),
        )

        # Run the test.
        play.play(args)

        # Check the result.
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
