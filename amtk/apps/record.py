#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from amtk.utils import messages, options, time, misc


def write(args, channel, method, properties, body):
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
        'headers': properties.headers,
    }

    # Write a single line of json.
    args.output.write(json.dumps(data) + '\n')

    # Flush the buffer so that commands that are piped to this utility will
    # get the next message instantly. This feature is useful if you want to
    # pipe messages from one exchange to the next; just record and pipe it to
    # play.
    args.output.flush()


def record(args):
    '''
    Reads and prints messages.
    '''
    # Connect to the server.
    connection, channel = messages.connect(args)

    # Subscribe to the exchange.
    queue = messages.subscribe(channel, args, exclusive=True, auto_delete=True)
    messages.qos(channel, args)

    # Create a callback that closures over the args parameter.
    def callback(channel, method, properties, body):
        write(args, channel, method, properties, body)

    # Setup the consumption callback.
    channel.basic_consume(
        callback,
        queue=queue,
        no_ack=True,
        exclusive=True,
    )

    # Stop on a keyboard interrupt.
    with misc.suppress_interrupt():
        # Start consuming messages.
        channel.start_consuming()

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
        options.output,
        options.version(),
    )
    args = options.parse(description, parameters).parse_args()

    # Run until the user interrupts execution.
    record(args)
