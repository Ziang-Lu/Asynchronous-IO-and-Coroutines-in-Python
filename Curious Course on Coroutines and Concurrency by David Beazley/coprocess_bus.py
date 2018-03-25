#!usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import sys
from cosax_bus import filter_on_field, bus_info_printer


def receive_from(f, target):
    """
    Unpickles items from the given file (pipe) and feeds them to the given
    coroutine.
    :param f: file
    :param target: coroutine
    :return: None
    """
    try:
        while True:
            item = pickle.load(f)
            target.send(item)
    except EOFError:
        target.close()


direction_filter = filter_on_field(field='direction', val='North Bound',
                                   target=bus_info_printer())
route_filter = filter_on_field(field='route', val='22',
                               target=direction_filter)
receive_from(f=sys.stdin, target=route_filter)
