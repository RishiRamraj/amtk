#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import pika
import time
import dateutil.parser
from amtk.utils import (
    messages, options, builtins, misc, time as timeutils
)


def wait_delta(delta):
    '''
    Wait a specified delta number of seconds.
    '''
    def result(last, now):
        # Exit early.
        if last is None:
            return

        time.sleep(delta)

    return result


def wait_timestamp(last, now):
    '''
    Wait for the difference between now and last.
    '''
    # Exit early.
    if last is None:
        return

    # Get the time delta.
    delta = (now - last).total_seconds()

    # Wait for the next message.
    time.sleep(delta)


def get_timing(args):
    '''
    Test and return the wait function.
    '''
    # Check for a timestamp timing mode.
    if args.timing in ('record', 'created'):
        return wait_timestamp

    # Check for a delta.
    try:
        # Get the delta.
        timing = float(args.timing)
    except ValueError:
        message = ('Timing must either be record, created or delta '
                   'seconds between messages. %s provided.')
        raise ValueError(message % args.timing)

    # Ensure that the timing is > 0.
    if timing < 0:
        raise ValueError('Timing must be a positive number.')

    return wait_delta(timing)


def publish(last, wait, args, channel, line):
    '''
    Publishes a line from stdin to the message queue. This function returns
    the timestamp of the last valid message processed.
    '''
    try:
        # Decode the data.
        data = json.loads(line)

    except ValueError:
        builtins.print_text('Invalid message: %s' % line)
        return last

    # Parse timestamps.
    parser = misc.optional(dateutil.parser.parse)
    expiry_time = parser(data['absolute_expiry_time'])
    creation_time = parser(data['creation_time'])
    record_time = parser(data['record_time'])

    # Wait to publish.
    now = {
        'created': creation_time,
        'record': record_time,
    }
    wait(last, now.get(args.timing))

    # Get publish parameters.
    key = args.routing_key
    routing_key = key if key else data['routing_key']
    mandatory = args.mandatory == 'yes'
    immediate = args.immediate == 'yes'

    # Set the properties.
    parser = misc.optional(timeutils.timestamp)
    properties = pika.spec.BasicProperties(
        content_type=data['content_type'],
        content_encoding=data['content_encoding'],
        correlation_id=data['correlation_id'],
        reply_to=data['reply_to'],
        expiration=parser(expiry_time),
        message_id=data['message_id'],
        timestamp=parser(creation_time),
        user_id=data['user_id'],
    )

    # Publish the message.
    channel.basic_publish(
        exchange=args.exchange,
        routing_key=routing_key,
        body=data['body'],
        properties=properties,
        mandatory=mandatory,
        immediate=immediate,
    )

    return creation_time


def play(args):
    '''
    Reads and publishes messages.
    '''
    # Connect to the server.
    connection, channel = messages.connect(args)

    # Get timing parameters.
    wait = get_timing(args)
    last = None

    # Read the data.
    for line in args.data.readlines():
        # Publish the data.
        last = publish(last, wait, args, channel, line)

    # Close the connection.
    channel.close()
    connection.close()


def main():
    '''
    Application entry point.
    '''
    # Parse the command line arguments.
    description = ('Reads messages from stdin and publishes them. The '
                   'exchange should be created before this tool is used.')
    parameters = (
        options.data,
        options.amqp(routing_key='play', queue=False),
        options.publish,
        options.timing,
    )
    args = options.parse(description, parameters).parse_args()

    # Run until the user interrupts execution.
    play(args)
