#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import pika
import time
import datetime
from amtk.utils import messages, options, builtins


def wait(args, last, current):
    '''
    Wait until the next message should be processed.
    '''
    # Get the time delta.
    delta = 0
    if last:
        timestamp = datetime.datetime.fromtimestamp
        delta = (timestamp(current) - timestamp(last)).seconds

    # Check to see if it's been overridden.
    check = lambda value: value is not None and value >= 0
    seconds = args.timing if check(args.timing) else delta

    # Wait for the next message.
    time.sleep(seconds)


def publish(timestamp, args, channel, line):
    '''
    Publishes a line from stdin to the message queue. This function returns
    the timestamp of the last valid message processed.
    '''
    try:
        # Decode the data.
        data = json.loads(line)

    except ValueError:
        builtins.print_text('Invalid message: %s' % line)
        return timestamp

    # Wait to publish.
    wait(args, timestamp, data['creation_time'])

    # Get publish parameters.
    key = args.routing_key
    routing_key = key if key else data['routing_key']
    mandatory = args.mandatory == 'yes'
    immediate = args.immediate == 'yes'
    properties = pika.spec.BasicProperties(
        content_type=data['content_type'],
        content_encoding=data['content_encoding'],
        correlation_id=data['correlation_id'],
        reply_to=data['reply_to'],
        expiration=data['absolute_expiry_time'],
        message_id=data['message_id'],
        timestamp=data['creation_time'],
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

    return data['creation_time']


def play(args):
    '''
    Reads and publishes messages.
    '''
    # Connect to the server.
    connection, channel = messages.connect(args)

    # Read the data.
    timestamp = None
    for line in args.data.readlines():
        # Publish the data.
        timestamp = publish(timestamp, args, channel, line)

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
