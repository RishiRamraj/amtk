#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytz
import datetime


def server_time(timestamp):
    '''
    Returns a datetime object from a timestamp. It's not clear how to get the
    timezone of the amqp server, which reports the timestamp. The amqp spec
    is somewhat vague on the subject. Based on experiments, the times seem to
    be measured at UTC.

    This function abstracts away this problem. Once a clear answer is found,
    this function can be changed.
    '''
    parser = datetime.datetime.fromtimestamp
    parse = lambda target: parser(target, tz=pytz.utc).isoformat()
    return None if timestamp is None else parse(timestamp)
