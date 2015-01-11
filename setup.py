#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup


version = '0.1.0'

description = '''
The Asynchronous Message Tool Kit. Utilities for the AMQP.
'''

setup(
    name='amtk',
    version=version,
    description=description,
    author='Rishi Ramraj',
    author_email='thereisnocowlevel@gmail.com',
    license=license,
    install_requires=[
        'setuptools',
        'pika',
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
        ],
    },
)
