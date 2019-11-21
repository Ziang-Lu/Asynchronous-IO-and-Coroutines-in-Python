#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo for the usage of "async" and "await" keywords.

From Python 3.5, Python provides "async" and "await" keywords to support
asynchronous IO and coroutine, and to simplify the code:
Simply replace the previous "@asyncio.coroutine" with "async" in the function
declaration, and replace the previous "yield from" with "await".

Also, note that the way to run coroutines also changed:
- Higher-level API using asyncio module functions
- Lower-level API using the event loop directly, as in the previous demo
"""

__author__ = 'Ziang Lu'

import asyncio
import random
import threading
from typing import Coroutine


async def hello() -> Coroutine:
    """
    Dummy coroutine.
    :return: coroutine
    """
    th_name = threading.current_thread().name
    print(f'Hello, world! ({th_name})')
    await asyncio.sleep(1)
    print(f'Hello again! ({th_name})')


asyncio.run(hello())

# Output:
# Hello, world!
# (Will be pending here for around 1 second)
# Hello again!


async def mygen(a: list) -> Coroutine:
    """
    Coroutine to randomly remove elements from the given list.
    :param a: list
    :return: coroutine
    """
    while len(a):
        i = random.randint(0, len(a) - 1)
        print(a.pop(i))
        await asyncio.sleep(delay=1)


async def print_list_demo() -> None:
    tasks = [mygen(['ss', 'dd', 'gg']), mygen([1, 2, 5, 6])]
    # task1 = asyncio.create_task(mygen(['ss', 'dd', 'gg']))
    # task2 = asyncio.create_task(mygen([1, 2, 5, 6]))
    # tasks = [task1, task2]
    await asyncio.gather(*tasks, return_exceptions=True)
    # When coroutines are passed to asyncio.gather(), they are automatically
    # wrapped in tasks, so no need to do it manually.


asyncio.run(print_list_demo())

# Output:
# dd
# 6
# ss
# 5
# gg
# 2
# 1
# {<Task finished coro=<mygen() done, defined at async_and_await.py:40> result=None>, <Task finished coro=<mygen() done, defined at async_and_await.py:40> result=None>}
# set()
