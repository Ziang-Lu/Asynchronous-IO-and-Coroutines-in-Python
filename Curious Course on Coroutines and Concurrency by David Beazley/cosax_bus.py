#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An example showing how to dispatch SAX events into a pipeline of coroutines.
"""

import xml.sax
from coroutine import coroutine
from cosax import EventHandler


@coroutine
def buses_to_dicts(target):
    """
    A coroutine that receives collects bus information as a dictionary and feeds
    it to the given target coroutine.
    :param target: coroutine
    :return: coroutine
    """
    # State A: Looking for a bus
    while True:
        event, val = yield
        if event == 'start' and val[0] == 'bus':
            # State B: Collecting bus information as a dictionary
            bus_dict = {}
            fragments = []
            while True:
                event, val = yield
                if event == 'start':
                    fragments = []
                elif event == 'content':
                    fragments.append(val)
                elif event == 'end':
                    if val != 'bus':
                        bus_dict[val] = ''.join(fragments)
                    else:
                        target.send(bus_dict)
                        break


@coroutine
def filter_on_field(field, val, target):
    """
    A coroutine that filters the given field-value pair in the received
    dictionary, and feeds the filtered dictionary to the given target coroutine.
    :param field: str
    :param val: str
    :param target: coroutine
    :return: coroutine
    """
    while True:
        d = yield
        if d.get(field, None) == val:
            target.send(d)


@coroutine
def bus_info_printer():
    """
    A coroutine that prints the received bus information dictionary.
    :return: coroutine
    """
    while True:
        bus = yield
        print('%(route)s, %(id)s, "%(direction)s", %(latitude)s, %(longitude)s'
              % bus)


def main():
    direction_filter = filter_on_field(field='direction', val='North Bound',
                                       target=bus_info_printer())
    route_filter = filter_on_field(field='route', val='22',
                                   target=direction_filter)
    xml.sax.parse(source='allroutes.xml',
                  handler=EventHandler(
                      target=buses_to_dicts(target=route_filter)))


if __name__ == '__main__':
    main()


# Output:
# 22, 1485, "North Bound", 41.880481123924255, -87.62948191165924
# 22, 1629, "North Bound", 42.01851969751819, -87.6730209876751
# 22, 1489, "North Bound", 41.962393500588156, -87.66610128229314
# 22, 1533, "North Bound", 41.92381583870231, -87.6395345910803
# 22, 1779, "North Bound", 41.989253234863284, -87.66976165771484
# 22, 1595, "North Bound", 41.892801920572914, -87.62985568576389
# 22, 1567, "North Bound", 41.91437446296989, -87.63357444862267
# 22, 1795, "North Bound", 41.98753767747145, -87.66956552358774
# 22, 1543, "North Bound", 41.92852973937988, -87.64240264892578
# 22, 1315, "North Bound", 41.96697834559849, -87.66706085205078
# 22, 6069, "North Bound", 41.98728592755043, -87.66953517966074
# 22, 1891, "North Bound", 41.92987823486328, -87.64342498779297
# 22, 1569, "North Bound", 42.003393713033425, -87.6723536365437
# 22, 1617, "North Bound", 41.90174682617187, -87.63128570556641
# 22, 1821, "North Bound", 41.976410124037, -87.66838073730469
# 22, 1499, "North Bound", 41.96970504369491, -87.66764088166066
