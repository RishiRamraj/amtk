# amtk
The Asynchronous Message Tool Kit. Utilities for the AMQP.

Currently only two tools are supported; record and play.

## Installation

The AMTK is a Python package and can be found on PyPI:
https://pypi.python.org/pypi/amtk

To install the package, use pip:
```
pip install amtk
```

## Record

The record tool reads messages from the exchange and prints
them to stdout. You can use pipes to send the data to a file,
which you can play back later.

Messages are recorded in json format. One message should occupy
one line in the output.


```
usage: amtk.record [-h] [--queue QUEUE] [--user USER] [--password PASSWORD]
                   [--host HOST] [--port PORT] [--virtual_host VIRTUAL_HOST]
                   [--prefetch_size PREFETCH_SIZE]
                   [--prefetch_count PREFETCH_COUNT]
                   exchange routing_key

Reads messages from the queue and prints them. The exchange should be created
before this tool is used.

positional arguments:
  exchange              The messaging exchange.
  routing_key           The routing key used to extract messages.

optional arguments:
  -h, --help            show this help message and exit
  --queue QUEUE         The name of the queue.
  --user USER           The rabbitmq user.
  --password PASSWORD   The rabbitmq password.
  --host HOST           The rabbitmq address.
  --port PORT           The rabbitmq port.
  --virtual_host VIRTUAL_HOST
                        The rabbitmq virtual host.
  --prefetch_size PREFETCH_SIZE
                        The prefetch window size.
  --prefetch_count PREFETCH_COUNT
                        The prefetch message count.
```

## Play

The play tool reads messages from a file and sends them to the
target exchange. You can use the record tool to determine the
format required for play.

Messages are recorded in json format. One message should occupy
one line in the input.


```
usage: amtk.play [-h] [--routing_key ROUTING_KEY] [--user USER]
                 [--password PASSWORD] [--host HOST] [--port PORT]
                 [--virtual_host VIRTUAL_HOST] [--mandatory {yes,no}]
                 [--immediate {yes,no}] [--timing TIMING]
                 data exchange

Reads messages from stdin and publishes them. The exchange should be created
before this tool is used.

positional arguments:
  data                  The source data file.
  exchange              The messaging exchange.

optional arguments:
  -h, --help            show this help message and exit
  --routing_key ROUTING_KEY
                        Override the routing key found when recording.
  --user USER           The rabbitmq user.
  --password PASSWORD   The rabbitmq password.
  --host HOST           The rabbitmq address.
  --port PORT           The rabbitmq port.
  --virtual_host VIRTUAL_HOST
                        The rabbitmq virtual host.
  --mandatory {yes,no}  Delivery of the message is mandatory.
  --immediate {yes,no}  Raise an exception if the message cannot be delivered.
  --timing TIMING       Number of seconds between messages. If no timing is
                        specified then the original timing is used.
```
