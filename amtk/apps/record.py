#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from amtk.utils import messages, options, builtins, time


def callback(channel, method, properties, body):
    '''
    Called when messages are consumed.
    '''
    # Decode the result.
    data = {
        'exchange': method.exchange,
        'routing_key': method.routing_key,
        'message_id': properties.message_id,
        'user_id': properties.user_id,
        'reply_to': properties.reply_to,
        'correlation_id': properties.correlation_id,
        'content_type': properties.content_type,
        'content_encoding': properties.content_encoding,
        'absolute_expiry_time': time.server_time(properties.expiration),
        'creation_time': time.server_time(properties.timestamp),
        'record_time': time.now(),
        'body': body,
    }

    # Write a single line of json.
    builtins.print_text(json.dumps(data))


def record(args):
    '''
    Reads and prints messages.
    '''
    # Connect to the server.
    connection, channel = messages.connect(args)

    # Subscribe to the exchange.
    queue = messages.subscribe(channel, args)

    # Setup the consumption callback.
    messages.qos(channel, args)
    channel.basic_consume(
        callback,
        queue=queue,
        no_ack=True,
        exclusive=True,
    )

    try:
        # Start consuming messages.
        channel.start_consuming()

    except KeyboardInterrupt:
        # Stop on a keyboard interrupt.
        pass

    # Close the connection.
    channel.close()
    connection.close()


def main():
    '''
    Application entry point.
    '''
    # Parse the command line arguments.
    description = ('Reads messages from the queue and prints them. The '
                   'exchange should be created before this tool is used.')
    parameters = (
        options.amqp(routing_key='routing', queue=True),
        options.prefetch,
    )
    args = options.parse(description, parameters).parse_args()

    # Run until the user interrupts execution.
    record(args)
