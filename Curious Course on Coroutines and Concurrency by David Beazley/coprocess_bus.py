#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subprocess module wrapping coroutines, which communicates with the calling
process via a pipe.
"""

import pickle
import sys
from typing import Coroutine

from cosax_bus import bus_info_printer, filter_on_field


def receive_from(f, target: Coroutine) -> None:
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


printer = bus_info_printer()
direction_filter = filter_on_field(
    field='direction', val='North Bound', target=printer
)
route_filter = filter_on_field(field='route', val='22', target=direction_filter)
receive_from(sys.stdin, target=route_filter)
