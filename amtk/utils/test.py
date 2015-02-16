#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
from amtk.utils import testcase as unittest
from mock import patch, MagicMock
import StringIO
import datetime
import pytz
import argparse

# To be tested.
from amtk.utils import options, messages, time, misc


class OptionsUtils(unittest.TestCase):
    '''
    Tests for functions in the options module.
    '''
    def check_parser(self, parser, tests):
        '''
        A utility to implement tests of the form:

        tests = [
            {
                'test': 'test arguments'
                'expected': {
                    'attribute': 'value',
                }
            },
        ]
        '''
        for test in tests:
            # Parse the test.
            result = parser.parse_args(test['test'].split())

            # Check the result.
            for attribute, value in test['expected'].items():
                self.assertEqual(getattr(result, attribute), value)


class Options(OptionsUtils):
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
        result = options.configure(description, parameters)

        # Check the result.
        self.assertEqual(result.description, description)
        for parameter in parameters:
            parameter.assert_called_once_with(result)

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
        parser = options.configure(description, parameters)
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
        parser = options.configure(description, parameters)
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
        parser = options.configure(description, parameters)
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
        parser = options.configure(description, parameters)
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
        parser = options.configure(description, parameters)
        self.check_parser(parser, cases)

    def check_file_stdio(self, target, name, stdin=True):
        '''
        A positive test for a file parameter with stdio defaults.
        '''
        # Create test data.
        parser = argparse.ArgumentParser()
        target(parser)

        # Run the test.
        result = getattr(parser.parse_args([]), name)

        # TODO: For some reason, when this function is called by the nose
        # test runner for a writable file, the result is a StrioIO instance,
        # whose name cannot be directly tested.
        if isinstance(result, StringIO.StringIO):
            return

        # Check the result.
        file = getattr(result, 'name')
        expected = '<stdin>' if stdin else '<stdout>'
        self.assertEqual(file, expected)

    def test_input(self):
        '''
        A test for the input function. input is a file type, so testing it
        using the conventional method is not possible.
        '''
        self.check_file_stdio(options.input, 'input')

    def test_output(self):
        '''
        A test for the output function. output is a file type, so testing it
        using the conventional method is not possible.
        '''
        self.check_file_stdio(options.output, 'output', stdin=False)

    def test_files(self):
        '''
        A test for the files function. files is a file type, so testing it
        using the conventional method is not possible.
        '''
        # Create test data.
        parser = argparse.ArgumentParser()

        # Run the test.
        options.files(parser)

    def test_order(self):
        '''
        A test for the order function.
        '''
        # Create test data.
        description = 'test'
        parameters = (options.order, )

        # Create test cases.
        cases = (
            {
                'test': '',
                'expected': {
                    'order': 'record',
                },
            },
            {
                'test': '--order created',
                'expected': {
                    'order': 'created',
                },
            },
        )

        # Run the test.
        parser = options.configure(description, parameters)
        self.check_parser(parser, cases)

    def test_version(self):
        '''
        A test for the version function. This function is difficult to test
        because when parsed, because calling the parser immediately exits
        the program after printing the version.

        The SystemExit exception can be caught, but the test still pollutes
        stdout when run.
        '''
        # Create test data.
        parser = argparse.ArgumentParser(prog='test')

        # Run the test.
        options.version()(parser)


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

    @patch('amtk.utils.time.datetime')
    def test_now(self, _datetime):
        '''
        A positive test for now, for completion.
        '''
        # Create fake data.
        test = datetime.datetime(2015, 1, 1, tzinfo=pytz.utc)
        _datetime.datetime.now.return_value = test

        # Run the test.
        result = time.now()

        # Check the result.
        expected = '2015-01-01T00:00:00+00:00'
        self.assertEqual(result, expected)


class Misc(unittest.TestCase):
    '''
    Tests for functions in the misc module.
    '''
    def test_optional(self):
        '''
        A positive test for the optional function.
        '''
        # Run the test.
        result = misc.optional(lambda value: value+1)

        # Check the result.
        self.assertEqual(result(0), 1)

    def test_optional_null(self):
        '''
        A negative test for the optional function.
        '''
        # Run the test.
        result = misc.optional(lambda value: value+1)

        # Check the result.
        self.assertIsNone(result(None))

    def test_suppress_interrupt(self):
        '''
        A positive test for the KeyboardInterrupt suppressor.
        '''
        # Run the test.
        with misc.suppress_interrupt():
            raise KeyboardInterrupt()


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
