#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import dateutil.parser
from amtk.utils import options, builtins, misc


def merge(args):
    '''
    Merges and prints messages.
    '''
    # The content of the merged dataset. This dictionary contains a map
    # between the message ids and the data object.
    content = {}

    # This dictionary contains a map between the ordering date and a list of
    # message ids that correspond to that date.
    dates = {}

    # Get the order parameters.
    parser = misc.optional(dateutil.parser.parse)
    map = {
        'record': 'record_time',
        'created': 'creation_time',
    }
    key = map[args.order]

    # Read the data from the files.
    for file in args.files:
        for line in file.readlines():
            try:
                # Parse the data.
                data = json.loads(line)

            except ValueError:
                continue

            # Ignore any undated lines.
            date = parser(data[key])
            if date is None:
                continue

            # Ignore existing data.
            id = data['message_id']
            if id is None or id in content:
                continue

            # Store the line. To ensure that content is properly formatted,
            # it is re-encoded using json.
            content[id] = json.dumps(data)

            # Store the order.
            dates.setdefault(date, [])
            dates[date].append(id)

    # Print the content in order.
    order = sorted(dates.keys())
    for date in order:
        # Print each message at that date.
        for id in dates[date]:
            builtins.print_text(content[id])


def main():
    '''
    Application entry point.
    '''
    # Parse the command line arguments.
    description = ('Merge a number of recorded data files and print the '
                   'result. Note that the message id is used to merge the '
                   'data sets. Messages that cannot be parsed or lack a '
                   'message id are ignored.')
    parameters = (options.files, options.order)
    args = options.parse(description, parameters).parse_args()

    # Merge files.
    merge(args)
