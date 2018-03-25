#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An example showing how to dispatch SAX events into a coroutine object.
"""

import xml.sax
from coroutine import coroutine


class EventHandler(xml.sax.ContentHandler):
    def __init__(self, target):
        self._target = target

    def startElement(self, name, attrs):
        self._target.send(('start', (name, attrs)))

    def characters(self, content):
        self._target.send(('content', content))

    def endElement(self, name):
        self._target.send(('end', name))


@coroutine
def printer():
    """
    A coroutine that prints the received line.
    :return: coroutine
    """
    while True:
        event = yield
        print(event)


def main():
    xml.sax.parse(source='allroutes.xml', handler=MyHandler(target=printer()))


if __name__ == '__main__':
    main()
