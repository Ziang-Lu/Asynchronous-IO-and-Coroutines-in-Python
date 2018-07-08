#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo for the usage of "async" and "await" keywords.

From Python 3.5, Python provides "async" and "await" keywords to support
asynchronous IO and coroutine, and to simplify the code:
Simply replace the previous "@asyncio.coroutine" with "async" in the function
declaration, and replace the previous "yield from" with "await".
"""

__author__ = 'Ziang Lu'

import asyncio
import random

from typing import Coroutine


async def hello() -> Coroutine:
    print('Hello, world!')
    await asyncio.sleep(delay=1)
    print('Hello again!')


def hello_demo() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future=hello())

    # Output:
    # Hello, world!
    # (Will be pending here for around 1 second)
    # Hello again!


async def mygen(L: list) -> Coroutine:
    while len(L):
        i = random.randint(0, len(L) - 1)
        print(L.pop(i))
        await asyncio.sleep(delay=1)


def print_list_demo() -> None:
    loop = asyncio.get_event_loop()
    tasks = [mygen(['ss', 'dd', 'gg']), mygen([1, 2, 5, 6])]
    loop.run_until_complete(future=asyncio.wait(tasks))
    loop.close()

    # Output:
    # dd
    # 6
    # ss
    # 5
    # gg
    # 2
    # 1


def main():
    hello_demo()
    print_list_demo()


if __name__ == '__main__':
    main()
