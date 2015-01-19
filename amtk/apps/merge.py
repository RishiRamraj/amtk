#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from amtk.utils import options, builtins


def merge(args):
    '''
    Merges and prints messages.
    '''
    # The content of the merged dataset.
    content = {}

    # Read the data from the files.
    for file in args.files:
        for line in file.readlines():
            try:
                # Parse the data.
                data = json.loads(line)

            except ValueError:
                continue

            # Ignore existing data.
            id = data['message_id']
            if id is None or id in content:
                continue

            # Write the line. To ensure that content is properly formatted,
            # it is re-encoded using json.
            builtins.print_text(json.dumps(data))
            content.add(id)


def main():
    '''
    Application entry point.
    '''
    # Parse the command line arguments.
    description = ('Merge a number of recorded data files and print the '
                   'result. Note that the message id is used to merge the '
                   'data sets. Messages that cannot be parsed or lack a '
                   'message id are ignored.')
    parameters = (options.files, )
    args = options.parse(description, parameters).parse_args()

    # Merge files.
    merge(args)
