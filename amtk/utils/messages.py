#!/usr/bin/python
# -*- coding: utf-8 -*-

import pika


def connect(args):
    '''
    Connect to the amqp server. Returns the connection and channel objects.
    '''
    # Decode the connection parameters.
    credentials = pika.credentials.PlainCredentials(
        username=args.user,
        password=args.password,
    )
    parameters = pika.ConnectionParameters(
        host=args.host,
        port=args.port,
        virtual_host=args.virtual_host,
        credentials=credentials,
    )

    # Create the connection and channel.
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare the exchange.
    channel.exchange_declare(
        exchange=args.exchange,
        passive=True,
    )

    return connection, channel


def subscribe(channel, args):
    '''
    Create a queue to subscribe to the exchange.
    '''
    # Create the queue.
    result = channel.queue_declare(
        queue=args.queue,
        exclusive=True,
        auto_delete=True,
    )
    queue = result.method.queue

    # Bind to the exchange.
    channel.queue_bind(
        queue=queue,
        exchange=args.exchange,
        routing_key=args.routing_key,
    )

    return queue


def qos(channel, args):
    '''
    Set up basic quality of service parameters.
    '''
    channel.basic_qos(
        prefetch_size=args.prefetch_size,
        prefetch_count=args.prefetch_count,
    )
