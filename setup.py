#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


version = '0.3.0'

description = '''
The Asynchronous Message Tool Kit. Utilities for the AMQP.
'''
long_description = '''
The Asynchronous Message Tool Kit. Utilities for the AMQP.
Currently three tools are supported; record, play and merge.

The record tool reads messages from the exchange and prints
them to stdout. Messages are recorded in json format.

The play tool reads messages from a file and sends them to the
target exchange.

The merge tool uses message_ids to merge recordings into a single
file.
'''

url = 'https://github.com/RishiRamraj/amtk'
download_url = 'https://github.com/RishiRamraj/amtk/archive/%s.tar.gz'

setup(
    name='amtk',
    version=version,
    description=description,
    long_description=long_description,
    license='MIT',
    author='Rishi Ramraj',
    author_email='thereisnocowlevel@gmail.com',
    url=url,
    download_url=download_url % version,
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'pika',
        'pytz',
        'python-dateutil',
    ],
    tests_require=[
        'mock',
        'nose',
    ],
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'amtk.play = amtk.apps.play:main',
            'amtk.record = amtk.apps.record:main',
            'amtk.merge = amtk.apps.merge:main',
        ],
    },
)
