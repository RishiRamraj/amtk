#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
from amtk.utils import testcase as unittest
from mock import patch, MagicMock
import datetime
import pytz

# To be tested.
from amtk.utils import options, messages, time, misc


class Options(unittest.TestCase):
    '''
    Tests for functions in the options module.
    '''
    def test_parse(self):
        '''
        A test for the parse function.
        '''
        # Create test data.
        description = 'test'
        parameters = (MagicMock(), MagicMock())

        # Run the test.
        result = options.parse(description, parameters)

        # Check the result.
        self.assertEqual(result.description, description)
        for parameter in parameters:
            parameter.assert_called_once_with(result)

    def check_parser(self, parser, cases):
        '''
        A utility to implement test cases of the form:

        cases = [
            {
                'test': 'test arguments'
                'expected': {
                    'attribute': 'value',
                }
            },
        ]
        '''
        for case in cases:
            # Parse the test.
            result = parser.parse_args(case['test'].split())

            # Check the result.
            for attribute, value in case['expected'].items():
                self.assertEqual(getattr(result, attribute), value)

    def test_amqp_record(self):
        '''
        A test for the amqp function in record mode.
        '''
        # Create test data.
        description = 'test'
        parameters = (options.amqp(routing_key='routing', queue=True), )

        # Create test cases.
        cases = (
            {
                'test': 'exchange key',
                'expected': {
                    'exchange': 'exchange',
                    'routing_key': 'key',
                    'queue': '',
                    'user': 'guest',
                    'password': 'guest',
                    'host': 'localhost',
                    'port': 5672,
                    'virtual_host': '/',
                },
            },
            {
                'test': ('test test --queue test --user user '
                         '--password password --host host --port 123 '
                         '--virtual_host virtual_host'),
                'expected': {
                    'queue': 'test',
                    'user': 'user',
                    'password': 'password',
                    'host': 'host',
                    'port': 123,
                    'virtual_host': 'virtual_host',
                },
            },
        )

        # Run the test.
        parser = options.parse(description, parameters)
        self.check_parser(parser, cases)

    def test_amqp_play(self):
        '''
        A test for the amqp function in play mode.
        '''
        # Create test data.
        description = 'test'
        parameters = (options.amqp(routing_key='play'), )

        # Create test cases.
        cases = (
            {
                'test': 'test',
                'expected': {
                    'routing_key': None,
                },
            },
            {
                'test': 'test --routing_key test',
                'expected': {
                    'routing_key': 'test',
                },
            },
        )

        # Run the test.
        parser = options.parse(description, parameters)
        self.check_parser(parser, cases)

    def test_prefetch(self):
        '''
        A test for the prefetch function.
        '''
        # Create test data.
        description = 'test'
        parameters = (options.prefetch, )

        # Create test cases.
        cases = (
            {
                'test': '',
                'expected': {
                    'prefetch_size': 0,
                    'prefetch_count': 1,
                },
            },
            {
                'test': '--prefetch_size 2 --prefetch_count 3',
                'expected': {
                    'prefetch_size': 2,
                    'prefetch_count': 3,
                },
            },
        )

        # Run the test.
        parser = options.parse(description, parameters)
        self.check_parser(parser, cases)

    def test_timing(self):
        '''
        A test for the timing function.
        '''
        # Create test data.
        description = 'test'
        parameters = (options.timing, )

        # Create test cases.
        cases = (
            {
                'test': '',
                'expected': {
                    'timing': 'record',
                },
            },
            {
                'test': '--timing 0',
                'expected': {
                    'timing': '0',
                },
            },
        )

        # Run the test.
        parser = options.parse(description, parameters)
        self.check_parser(parser, cases)

    def test_publish(self):
        '''
        A test for the publish function.
        '''
        # Create test data.
        description = 'test'
        parameters = (options.publish, )

        # Create test cases.
        cases = (
            {
                'test': '',
                'expected': {
                    'mandatory': 'no',
                    'immediate': 'no',
                },
            },
            {
                'test': '--mandatory yes --immediate yes',
                'expected': {
                    'mandatory': 'yes',
                    'immediate': 'yes',
                },
            },
        )

        # Run the test.
        parser = options.parse(description, parameters)
        self.check_parser(parser, cases)

    def test_data(self):
        '''
        A test for the data function. Data is a file type, so testing it using
        the conventional method is not possible.
        '''
        # Create test data.
        parser = MagicMock()

        # Run the test.
        options.data(parser)


class Messages(unittest.TestCase):
    '''
    Tests for functions in the messages module. These tests are fairly mocky.
    '''
    @patch('amtk.utils.messages.pika')
    def test_connect(self, pika):
        '''
        A test for the connect function for completion.
        '''
        # Create test data.
        args = MagicMock()
        args.user = 'user'
        args.password = 'password'
        args.host = 'host'
        args.port = 123
        args.virtual_host = 'vhost'
        args.exchange = 'exchange'

        # Run the test.
        messages.connect(args)

        # Check the result.
        self.assertTrue(pika.credentials.PlainCredentials.called)
        self.assertTrue(pika.ConnectionParameters.called)
        self.assertTrue(pika.BlockingConnection.called)

    @patch('amtk.utils.messages.pika')
    def test_subscribe(self, pika):
        '''
        A test for the subscribe function for completion.
        '''
        # Create test data.
        channel = MagicMock()
        args = MagicMock()
        args.queue = 'queue'
        args.exchange = 'exchange'
        args.routing_key = 'routing_key'

        # Run the test.
        messages.subscribe(channel, args)

        # Check the result.
        self.assertTrue(channel.queue_declare.called)
        self.assertTrue(channel.queue_bind.called)

    @patch('amtk.utils.messages.pika')
    def test_qos(self, pika):
        '''
        A test for the qos function for completion.
        '''
        # Create test data.
        channel = MagicMock()
        args = MagicMock()
        args.prefetch_size = 2
        args.prefetch_count = 3

        # Run the test.
        messages.qos(channel, args)

        # Check the result.
        channel.basic_qos.assert_called_once_with(
            prefetch_size=2,
            prefetch_count=3,
        )


class Time(unittest.TestCase):
    '''
    Tests for functions in the time module.
    '''
    def test_server_time(self):
        '''
        A test for the server_time function.
        '''
        # Create test data.
        timestamp = 1421562419

        # Run the test.
        result = time.server_time(timestamp)

        # Check the result.
        expected = '2015-01-18T06:26:59+00:00'
        self.assertEqual(result, expected)

    def test_server_time_none(self):
        '''
        If no timestamp is given, the parser should return None.
        '''
        # Create test data.
        timestamp = None

        # Run the test.
        result = time.server_time(timestamp)

        # Check the result.
        self.assertIsNone(result)

    def test_timestamp(self):
        '''
        A positive test for timestamp.
        '''
        # Create test data.
        value = datetime.datetime(2015, 1, 18, 17, 44, 24, 0, pytz.utc)

        # Run the test.
        result = time.timestamp(value)

        # Check the result.
        expected = 1421603064
        self.assertEqual(result, expected)


class Misc(unittest.TestCase):
    '''
    Tests for functions in the misc module.
    '''
    def test_optional(self):
        '''
        A positive test for the optional function.
        '''
        # Create test data.
        function = lambda value: value+1

        # Run the test.
        result = misc.optional(function)

        # Check the result.
        self.assertEqual(result(0), 1)

    def test_optional_null(self):
        '''
        A negative test for the optional function.
        '''
        # Create test data.
        function = lambda value: value+1

        # Run the test.
        result = misc.optional(function)

        # Check the result.
        self.assertIsNone(result(None))


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
