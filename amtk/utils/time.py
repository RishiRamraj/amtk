#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytz
import datetime


# The datetime epoch obect.
EPOCH = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)


def server_time(timestamp):
    '''
    Returns a datetime object from a timestamp. It's not clear how to get the
    timezone of the amqp server, which reports the timestamp. The amqp spec
    is somewhat vague on the subject. Based on experiments, the times seem to
    be measured at UTC.

    This function abstracts away this problem. Once a clear answer is found,
    this function can be changed.
    '''
    def parse(target):
        parser = datetime.datetime.fromtimestamp
        return parser(target, tz=pytz.utc).isoformat()

    return None if timestamp is None else parse(timestamp)


def timestamp(value):
    '''
    Returns the timestamp of a datetime object.
    '''
    return int((value - EPOCH).total_seconds())


def now():
    '''
    Returns a datetime now object at utc. For convenience.
    '''
    return datetime.datetime.now(tz=pytz.utc).isoformat()
