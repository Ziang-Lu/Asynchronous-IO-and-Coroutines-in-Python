#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An example showing how to wrap a thread within a coroutine.
The calling thread and the new thread communicate via a message queue.
"""

import threading
import xml.sax
from queue import Queue
from typing import Coroutine

from coroutine import coroutine
from cosax import EventHandler
from cosax_bus import bus_info_printer, buses_to_dicts, filter_on_field


def thread_func(q: Queue, target: Coroutine) -> None:
    """
    Thread function to receive items, and feeds them into the given coroutine.
    :param q: Queue
    :param target: coroutine
    :return: None
    """
    while True:
        item = q.get()
        if item is GeneratorExit:
            target.close()
            return
        target.send(item)


@coroutine
def threaded(target: Coroutine):
    """
    A coroutine that fires a new thread to do the work.
    The calling thread and the new thread communicate via a message queue.
    :param target: coroutine
    :return: coroutine
    """
    # The calling thread and the new thread communicate via a message queue.
    q = Queue()
    th = threading.Thread(target=thread_func, args=(q, target))
    th.start()
    # Receive items in the current thread, and pass them into the new thread via
    # the queue
    try:
        while True:
            item = yield
            q.put(item)
    except GeneratorExit:
        q.put(GeneratorExit)


def main():
    printer = bus_info_printer()
    direction_filter = filter_on_field(
        field='direction', val='North Bound', target=printer
    )
    route_filter = filter_on_field(
        field='route', val='22', target=direction_filter
    )
    xml.sax.parse(
        source='allroutes.xml',
        handler=EventHandler(
            target=threaded(target=buses_to_dicts(target=route_filter))
        )
    )


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

# Note:
# Adding threads makes this example run about 50% slower.
