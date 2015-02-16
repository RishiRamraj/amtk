#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import pika


def connect(config):
    '''
    Connect to the amqp server. Returns the connection and channel objects.
    '''
    # Decode the connection parameters.
    credentials = pika.credentials.PlainCredentials(
        username=config.user,
        password=config.password,
    )
    parameters = pika.ConnectionParameters(
        host=config.host,
        port=config.port,
        virtual_host=config.virtual_host,
        credentials=credentials,
    )

    # Create the connection and channel.
    message = 'Connecting to messaging server %s:%d.'
    logging.debug(message, config.host, config.port)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare the exchange.
    message = 'Passiely declaring exchange %s.'
    logging.debug(message, config.exchange)
    channel.exchange_declare(
        exchange=config.exchange,
        passive=True,
    )

    return connection, channel


def subscribe(channel, config, passive=False, durable=False, exclusive=False,
              auto_delete=False):
    '''
    Create a queue to subscribe to the exchange.
    '''
    # Create the queue.
    message = 'Declaring queue %s.'
    logging.debug(message, config.queue)
    result = channel.queue_declare(
        queue=config.queue,
        passive=passive,
        durable=durable,
        exclusive=exclusive,
        auto_delete=auto_delete,
    )
    queue = result.method.queue

    # Bind to the exchange.
    message = 'Binding to exchange %s with routing key %s.'
    logging.debug(message, config.exchange, config.routing_key)
    channel.queue_bind(
        queue=queue,
        exchange=config.exchange,
        routing_key=config.routing_key,
    )

    return queue


def qos(channel, config):
    '''
    Set up basic quality of service parameters.
    '''
    message = 'Binding to exchange %s with routing key %s.'
    logging.debug(message, config.exchange, config.routing_key)
    channel.basic_qos(
        prefetch_size=config.prefetch_size,
        prefetch_count=config.prefetch_count,
    )
