#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
from amtk.utils import testcase as unittest
from mock import patch, MagicMock
import json
import datetime
import pytz
import dateutil.parser
from amtk.utils import time

# To be tested.
from amtk.apps import record, play, merge


# Timestamp constants.
def parse(value):
    return datetime.datetime.fromtimestamp(value, pytz.utc)

TIMESTAMPS = {
    'now': (
        1420070460,
        '2015-01-01T00:01:00.001+00:00',
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

# Test cases for the merge module.
CONTENT = (
    '{"body": "test", "creation_time": "2015-01-01T00:00:00+00:00", ',
    ('{"body": "test", "creation_time": null, "record_time": null, '
     '"message_id": "4"}'),
    ('{"body": "test", "creation_time": "2015-01-01T00:00:00+00:00", '
     '"record_time": "2015-01-01T00:00:00+00:00", "message_id": null}'),
    ('{"body": "test", "creation_time": "2015-01-01T00:00:00+00:00", '
     '"record_time": "2015-01-01T00:00:00+00:00", "message_id": "1"}'),
    ('{"body": "test", "creation_time": "2015-01-01T00:00:00+00:00", '
     '"record_time": "2015-01-01T00:00:00+00:00", "message_id": "1"}'),
    ('{"body": "test", "creation_time": "2015-01-01T00:00:00+00:00", '
     '"record_time": "2015-01-01T00:00:00+00:00", "message_id": "2"}'),
    ('{"body": "test", "creation_time": "2015-01-01T00:00:01+00:00", '
     '"record_time": "2015-01-01T00:00:01+00:00", "message_id": "3"}'),
    ('{"body": "test", "creation_time": "2015-01-01T00:00:02+00:00", '
     '"record_time": "2015-01-01T00:00:02+00:00", "message_id": "4"}'),
)


class Record(unittest.TestCase):
    '''
    Tests for functions in the record module. These tests are fairly mocky.
    '''
    @patch('amtk.apps.record.time')
    def test_write(self, _time):
        '''
        A test for the write function.
        '''
        created = TIMESTAMPS['created']
        now = TIMESTAMPS['now']

        # Mock time.now. server_time should not be mocked.
        _time.server_time = time.server_time
        _time.now.return_value = now[1]

        # Create test data.
        args = MagicMock()
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
        properties.headers = {'test': 'test'}
        properties.timestamp = created[0]
        properties.expiration = None
        body = 'body'

        # Run the test.
        record.write(args, channel, method, properties, body)

        # Check the result.
        expected = ('{"body": "body", "exchange": "exchange", "creation_time":'
                    ' "%s", "correlation_id": "correlation_id", "content_type"'
                    ': "content_type", "user_id": "user_id", "record_time": '
                    '"%s", "routing_key": "routing_key", "headers": {"test": '
                    '"test"}, "content_encoding": "content_encoding", '
                    '"reply_to": "reply_to", "absolute_expiry_time": null, '
                    '"message_id": "message_id"}\n')
        values = (created[1], now[1])
        args.output.write.assert_called_once_with(expected % values)

        self.assertTrue(args.output.flush.called)

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
    def test_main(self, options, _record):
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
    def test_wait_delta(self, time):
        '''
        Tests the wait_delta function.
        '''
        # Create test data.
        delta = 1.1
        last = TIMESTAMPS['last'][2]
        now = TIMESTAMPS['now'][2]

        # Run the test.
        result = play.wait_delta(delta)
        result(last, now)

        # Check the result.
        time.sleep.assert_called_once_with(1.1)

    @patch('amtk.apps.play.time')
    def test_wait_delta_none(self, time):
        '''
        Tests the wait_delta function with None for last.
        '''
        # Create test data.
        delta = 1.1
        last = None
        now = TIMESTAMPS['now'][2]

        # Run the test.
        result = play.wait_delta(delta)
        result(last, now)

        # Check the result.
        self.assertFalse(time.sleep.called)

    @patch('amtk.apps.play.time')
    def test_wait_timestamp(self, time):
        '''
        Tests the wait_timestamp function.
        '''
        # Create test data.
        last = TIMESTAMPS['last'][2]
        now = TIMESTAMPS['now'][2]

        # Run the test.
        play.wait_timestamp(last, now)

        # Check the result.
        time.sleep.assert_called_once_with(60.001)

    @patch('amtk.apps.play.time')
    def test_wait_timestamp_none(self, time):
        '''
        Tests the wait_timestamp function with a None last.
        '''
        # Create test data.
        last = None
        now = TIMESTAMPS['now'][2]

        # Run the test.
        play.wait_timestamp(last, now)

        # Check the result.
        self.assertFalse(time.sleep.called)

    def check_get_timing(self, timing):
        '''
        Tests the get_timing function.
        '''
        # Create test data.
        args = MagicMock()
        args.timing = timing

        # Run the test.
        return play.get_timing(args)

    def test_get_timing_record(self):
        '''
        Tests the get_timing function in record mode.
        '''
        result = self.check_get_timing('record')
        self.assertIs(result, play.wait_timestamp)

    def test_get_timing_created(self):
        '''
        Tests the get_timing function in created mode.
        '''
        result = self.check_get_timing('created')
        self.assertIs(result, play.wait_timestamp)

    @patch('amtk.apps.play.wait_delta')
    def test_get_timing_delta(self, wait_delta):
        '''
        A positive test for get_timing with a delta.
        '''
        self.check_get_timing('1.1')
        wait_delta.assert_called_once_with(1.1)

    def test_get_timing_delta_invalid(self):
        '''
        A positive test for get_timing with a delta.
        '''
        expected = 'must either be'
        with self.assertRaisesRegexp(ValueError, expected):
            self.check_get_timing('invalid')

    def test_get_timing_delta_negative(self):
        '''
        A positive test for get_timing with a delta.
        '''
        expected = 'positive'
        with self.assertRaisesRegexp(ValueError, expected):
            self.check_get_timing('-1.1')

    @patch('amtk.apps.play.pika')
    def check_publish(self, routing_key, pika, line=None):
        '''
        Structure for testing the publish function.
        '''
        # Create fake data.
        last = None
        wait = MagicMock()
        args = MagicMock()
        args.routing_key = routing_key
        args.mandatory = 'no'
        args.immediate = 'no'
        args.exchange = 'test'
        args.timing = 'record'
        channel = MagicMock()
        data = {
            'creation_time': TIMESTAMPS['created'][1],
            'record_time': TIMESTAMPS['now'][1],
            'routing_key': 'routing_key',
            'content_type': 'content_type',
            'content_encoding': 'content_encoding',
            'correlation_id': 'correlation_id',
            'reply_to': 'reply_to',
            'absolute_expiry_time': None,
            'message_id': 'message_id',
            'user_id': 'user_id',
            'body': 'body',
            'headers': {'test': 'test'},
        }
        line = line if line else json.dumps(data)

        # Run the test.
        result = play.publish(last, wait, args, channel, line)

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
        self.assertEqual(result, TIMESTAMPS['now'][2])

        # Check message properties.
        expected = {
            'user_id': u'user_id',
            'timestamp': TIMESTAMPS['created'][0],
            'correlation_id': u'correlation_id',
            'expiration': None,
            'headers': {'test': 'test'},
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
        args.timing = 'record'
        connection = MagicMock()
        channel = MagicMock()
        messages.connect.return_value = (
            connection,
            channel,
        )
        args.input.readline.side_effect = (
            json.dumps({'name': 'message 1'}),
            'invalid\n',
            '\n',
            json.dumps({'name': 'message 2'}),
            '',
        )

        # Run the test.
        play.play(args)

        # Check the result.
        self.assertTrue(publish.called)
        self.assertTrue(channel.close.called)
        self.assertTrue(connection.close.called)

    @patch('amtk.apps.play.play')
    @patch('amtk.apps.play.options')
    def test_main(self, options, _play):
        '''
        A test for the main function.
        '''
        # Run the test.
        play.main()

    @patch('amtk.apps.play.play')
    @patch('amtk.apps.play.options')
    def test_main_interrupt(self, options, _play):
        '''
        Ensure that KeyboardInterrupt is suppressed.
        '''
        # Create fake data.
        _play.side_effect = KeyboardInterrupt

        # Run the test.
        play.main()


class Merge(unittest.TestCase):
    '''
    Tests for functions in the merge module.
    '''
    @patch('amtk.apps.merge.builtins')
    def check_merge(self, order, builtins):
        '''
        A test for the merge function.
        '''
        file = unittest.file

        # Create fake data.
        args = MagicMock()
        args.order = order
        args.files = (
            file((CONTENT[0], CONTENT[3], CONTENT[4])),
            file((CONTENT[1], CONTENT[2], CONTENT[5])),
            file((CONTENT[6], CONTENT[7])),
        )

        # Run the test.
        merge.merge(args)

        # Check the result.
        result = builtins.print_text.call_args_list
        expected = [
            json.loads(CONTENT[4]),
            json.loads(CONTENT[5]),
            json.loads(CONTENT[6]),
            json.loads(CONTENT[7]),
        ]
        for index, value in enumerate(result):
            data = json.loads(value[0][0])
            self.assertEqual(data, expected[index])

    def test_merge_record(self):
        '''
        Test merge ordered by record.
        '''
        # Run the test.
        self.check_merge('record')

    def test_merge_created(self):
        '''
        Test merge ordered by created.
        '''
        # Run the test.
        self.check_merge('created')

    @patch('amtk.apps.merge.merge')
    @patch('amtk.apps.merge.options')
    def test_main(self, options, _merge):
        '''
        A test for the main function.
        '''
        # Run the test.
        merge.main()


class Integration(unittest.TestCase):
    '''
    Ensures that play can play recordings and vice versa.
    '''
    @patch('amtk.apps.record.time')
    def run_record(self, properties, body, _time):
        '''
        Used to run the record portion of the test.
        '''
        # Mock time.now. server_time should not be mocked.
        _time.server_time = time.server_time
        _time.now.return_value = TIMESTAMPS['now'][1]

        # Create test data.
        args = MagicMock()
        channel = MagicMock()
        method = MagicMock()
        method.exchange = 'exchange'
        method.routing_key = 'routing_key'

        # Run the test.
        record.write(args, channel, method, properties, body)

        # Return the result.
        return args.output.write.call_args[0][0]

    @patch('amtk.apps.play.pika')
    def run_play(self, line, pika):
        '''
        Used to run the play portion of the test.
        '''
        # Create fake data.
        last = None
        wait = MagicMock()
        args = MagicMock()
        args.mandatory = 'no'
        args.immediate = 'no'
        args.timing = 'record'
        args.exchange = 'exchange'
        args.routing_key = 'routing_key'
        channel = MagicMock()

        # Run the test.
        result = play.publish(last, wait, args, channel, line)

        # Return the results.
        properties = pika.spec.BasicProperties
        basic_publish = channel.basic_publish
        return result, properties, basic_publish

    def test_play_recording(self):
        '''
        Records some data and tries to play the result.
        '''
        # Create test data.
        properties = MagicMock()
        properties.message_id = 'message_id'
        properties.user_id = 'user_id'
        properties.reply_to = 'reply_to'
        properties.correlation_id = 'correlation_id'
        properties.content_type = 'content_type'
        properties.content_encoding = 'content_encoding'
        properties.timestamp = TIMESTAMPS['now'][0]
        properties.expiration = None
        properties.headers = {'test': 'test'}
        body = 'body'

        # Record the message.
        line = self.run_record(properties, body)

        # Play the message.
        result = self.run_play(line)
        result, properties, basic_publish = result

        # Check properties.
        expected = {
            'user_id': u'user_id',
            'timestamp': TIMESTAMPS['now'][0],
            'correlation_id': u'correlation_id',
            'expiration': None,
            'content_type': u'content_type',
            'reply_to': u'reply_to',
            'message_id': u'message_id',
            'content_encoding': u'content_encoding',
            'headers': {'test': u'test'},
        }
        self.assertEqual(properties.call_args[1], expected)

        # Check the body.
        publish = basic_publish.call_args[1]
        self.assertEqual(publish['body'], 'body')

    def test_recording_playback(self):
        '''
        Records some data and tries to play the result.
        '''
        # Create test data.
        line = ('{"body": "body", "exchange": "exchange", "creation_time": '
                '"%s", "correlation_id": "correlation_id", "content_type": '
                '"content_type", "user_id": "user_id", "record_time": "%s", '
                '"routing_key": "routing_key", "headers": {"test": "test"}, '
                '"content_encoding": "content_encoding", "reply_to": '
                '"reply_to", "absolute_expiry_time": null, "message_id": '
                '"message_id"}\n')
        values = (TIMESTAMPS['created'][1], TIMESTAMPS['now'][1])
        line = line % values

        # Play the message.
        result = self.run_play(line)
        result, properties, basic_publish = result

        # Decode the playback.
        properties = properties.call_args[1]
        prop = MagicMock()
        prop.message_id = properties['message_id']
        prop.user_id = properties['user_id']
        prop.reply_to = properties['reply_to']
        prop.correlation_id = properties['correlation_id']
        prop.content_type = properties['content_type']
        prop.content_encoding = properties['content_encoding']
        prop.headers = {'test': 'test'}
        prop.timestamp = properties['timestamp']
        prop.expiration = properties['expiration']
        body = basic_publish.call_args[1]['body']

        # Record the message.
        result = self.run_record(prop, body)

        # Check the line.
        self.assertEqual(result, line)


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
