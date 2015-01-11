#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
from amtk.utils import testcase as unittest
from mock import MagicMock


# To be tested.
from amtk.utils import options


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
        A test for the amqp function in record mode. Usually the queue should
        be explicitly required in this mode, but the test_amqp_queue function
        covers that case.
        '''
        # Create test data.
        description = 'test'
        parameters = (options.amqp(routing_key='routing'), )

        # Create test cases.
        cases = (
            {
                'test': 'test topic test',
                'expected': {
                    'exchange': 'test',
                    'type': 'topic',
                    'routing_key': 'test',
                    'queue': '',
                    'user': 'guest',
                    'password': 'guest',
                    'host': 'localhost',
                    'port': 5672,
                    'virtual_host': '/',
                },
            },
            {
                'test': ('test topic test --queue test --user user '
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

    def test_amqp_queue(self):
        '''
        A test for the amqp function in record mode with queue required.
        '''
        # Create test data.
        description = 'test'
        parameters = (options.amqp(routing_key='routing', queue=True), )

        # Create test cases.
        cases = (
            {
                'test': 'test topic test queue',
                'expected': {
                    'exchange': 'test',
                    'type': 'topic',
                    'routing_key': 'test',
                    'queue': 'queue',
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
                'test': 'test topic',
                'expected': {
                    'routing_key': None,
                },
            },
            {
                'test': 'test topic --routing_key test',
                'expected': {
                    'routing_key': 'test',
                },
            },
        )

        # Run the test.
        parser = options.parse(description, parameters)
        self.check_parser(parser, cases)


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
