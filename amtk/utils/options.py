#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse


def amqp(routing_key, queue=False):
    '''
    Adds amqp parameters to the parser.
    '''
    def result(parser):
        # Add basic messaging parameters.
        help = 'The messaging exchange.'
        parser.add_argument('exchange', type=str, help=help)

        help = 'The exchange type.'
        choices = ('fanout', 'direct', 'topic')
        parser.add_argument('type', type=str, help=help, choices=choices)

        # When recording, the routing key is used as normal, but when playing
        # back the user can optionally override the routing key for testing
        # purposes. Otherwise the routing key used is the one obtained when
        # recording.
        record = 'The routing key used to extract messages.'
        play = 'Override the routing key found when recording.'
        help = play if routing_key == 'play' else record
        name = '--routing_key' if routing_key == 'play' else 'routing_key'
        parser.add_argument(name, type=str, help=help)

        # Sometimes it's necessary to name the queue explicitly. If the
        # queue name is '', the server chooses the name.
        help = 'The name of the queue.'
        name = 'queue' if queue else '--queue'
        default = None if queue else ''
        parser.add_argument(name, type=str, default=default, help=help)

        # Add authentication parameters.
        help = 'The rabbitmq user.'
        parser.add_argument('--user', type=str, default='guest', help=help)
        help = 'The rabbitmq password.'
        parser.add_argument('--password', type=str, default='guest', help=help)

        # Add connection parameters.
        help = 'The rabbitmq address.'
        parser.add_argument('--host', type=str, default='localhost',
                            help=help)
        help = 'The rabbitmq port.'
        parser.add_argument('--port', type=int, default=5672, help=help)
        help = 'The rabbitmq virtual host.'
        parser.add_argument('--virtual_host', type=str, default='/', help=help)

    return result


def parse(description, parameters):
    '''
    Parses command line arguments and returns the args object. options is a
    list of functions that accept the parser as a parameter.
    '''
    # Create the parser.
    parser = argparse.ArgumentParser(description=description)

    # Add parameters.
    for parameter in parameters:
        parameter(parser)

    return parser
