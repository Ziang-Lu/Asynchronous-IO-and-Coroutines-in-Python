#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A very simple example illustrating the SAX XML parsing interface.
"""

import xml.sax


class MyHanlder(xml.sax.ContentHandler):

    def startElement(self, name, attrs):
        print(f'startElement {name}')

    def characters(self, content):
        print(f'characters {repr(content)[:40]}')

    def endElement(self, name):
        print(f'endElement {name}')


if __name__ == '__main__':
    xml.sax.parse(source='allroutes.xml', handler=MyHanlder())
