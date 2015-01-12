#!/usr/bin/python
# -*- coding: utf-8 -*-

from amtk.utils import messages, options


def callback(channel, method, properties, body):
    '''
    Called when messages are consumed.
    '''
    print('Received %r' % (body))


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


def main():
    '''
    Application entry point.
    '''
    # Parse the command line arguments.
    description = 'Reads messages from the queue and prints them.'
    parameters = (
        options.amqp(routing_key='routing', queue=True),
        options.prefetch,
    )
    args = options.parse(description, parameters).parse_args()

    # Run until the user interrupts execution.
    record(args)
