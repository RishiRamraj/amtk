#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse


def files(parser):
    '''
    Adds a varidac positional option to list files.
    '''
    help = 'The source data files.'
    type = argparse.FileType('r')
    parser.add_argument('files', type=type, help=help, nargs='*')


def data(parser):
    '''
    Adds a data positional argument as readable.
    '''
    help = 'The source data file.'
    type = argparse.FileType('r')
    parser.add_argument('data', type=type, help=help)


def timing(parser):
    '''
    Adds timing parameters.
    '''
    help = ('Configures the time interval between messages. Can be one of '
            'record, create or the number of seconds between messages. If '
            'record is specified, the original record timing is used. If '
            'create is specified, the created on timestamp is used; note '
            'that this timing is only accurate to the second. If no timing '
            'is specified, record is used.')
    parser.add_argument('--timing', default='record', help=help)


def publish(parser):
    '''
    Adds publish parameters.
    '''
    name = '--mandatory'
    choices = ('yes', 'no')
    help = 'Delivery of the message is mandatory.'
    parser.add_argument(name, choices=choices, default='no', help=help)

    name = '--immediate'
    choices = ('yes', 'no')
    help = 'Raise an exception if the message cannot be delivered.'
    parser.add_argument(name, choices=choices, default='no', help=help)


def prefetch(parser):
    '''
    Adds prefetch parameters.
    '''
    help = 'The prefetch window size.'
    parser.add_argument('--prefetch_size', type=int, default=0, help=help)

    help = 'The prefetch message count.'
    parser.add_argument('--prefetch_count', type=int, default=1, help=help)


def amqp(routing_key, queue=False):
    '''
    Adds amqp parameters to the parser.
    '''
    def result(parser):
        # Add basic messaging parameters.
        help = 'The messaging exchange.'
        parser.add_argument('exchange', type=str, help=help)

        # When recording, the routing key is used as normal, but when playing
        # back the user can optionally override the routing key for testing
        # purposes. Otherwise the routing key used is the one obtained when
        # recording.
        record = 'The routing key used to extract messages.'
        play = 'Override the routing key found when recording.'
        help = play if routing_key == 'play' else record
        name = '--routing_key' if routing_key == 'play' else 'routing_key'
        parser.add_argument(name, type=str, help=help)

        if queue:
            # Sometimes it's necessary to name the queue explicitly. If the
            # queue name is '', the server chooses the name.
            help = 'The name of the queue.'
            parser.add_argument('--queue', type=str, default='', help=help)

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
