#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A very simple example illustrating the SAX XML parsing interface.
"""

import xml.sax
from typing import Any


class MyHanlder(xml.sax.ContentHandler):

    def startElement(self, name: str, attrs: dict):
        print('startElement', name)

    def characters(self, content: Any):
        print('characters', repr(content)[:40])

    def endElement(self, name: str):
        print('endElement', name)


if __name__ == '__main__':
    xml.sax.parse(source='allroutes.xml', handler=MyHanlder())
