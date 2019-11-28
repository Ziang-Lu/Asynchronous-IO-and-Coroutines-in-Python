#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo for the usage of "gevent" framework, rather than "asyncio"
framework.
"""

__author__ = 'Ziang Lu'

import gevent
from gevent import monkey

# Since all IO operations in the standard library are BLOCKING, if we use
# "gevent" directly, it will internally use those BLOCKING IO operations in the
# standard library, which makes using "gevent" meaningless.
# Thus, we do monkey patching to replace all the blocking IO operations in the
# standard library, with the corresponding NON-BLOCKING (cooperative) IO
# operations defined in "gevent".
monkey.patch_all()

import random
from threading import current_thread


def hello() -> None:
    """
    Dummy function to run in a Greenlet.
    :return: None
    """
    print('Hello, world!')
    gevent.sleep(1)
    print('Hello again!')


greenlets = [gevent.spawn(hello)]
gevent.joinall(greenlets)

# Output:
# Hello, world!
# (Will be pending here for around 1 second)
# Hello again!


def mygen(a: list) -> None:
    """
    Function to randomly remove elements from the given list, run in a Greenlet.
    :param a: list
    :return: None
    """
    while len(a):
        i = random.randint(0, len(a) - 1)
        print(a.pop(i))
        gevent.sleep(1)


greenlets = [
    gevent.spawn(mygen, ['ss', 'dd', 'gg']),
    gevent.spawn(mygen, [1, 2, 5, 6])
]
gevent.joinall(greenlets)

# Output:
# dd
# 6
# gg
# 2
# ss
# 1
# 5
