#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo for the usage of "yield from".
"""

__author__ = 'Ziang Lu'

from typing import Coroutine, Generator


def fib(limit: int) -> Generator:
    """
    Fibonacci sequence generator.
    :param limit: int
    :return: Generator object
    """
    count = 0
    a, b = 0, 1
    while count < limit:
        yield b
        a, b = b, a + b
        count += 1


def fib_wrapper(func_iterable: Generator) -> Generator:
    """
    Wrapper function for the given generator object (iterable) by yielding by
    iterating the given generator object.
    :param func_iterable: Generator object
    :return: Generator object
    """
    print('start')
    for item in func_iterable:
        yield item
    print('end')


def fib_wrapper_2(func_iterable: Generator) -> Generator:
    """
    Wrapper function for the given generator object (iterable) by simply
    "yield from" the given generator object.
    :param func_iterable: Generator object
    :return: Generator object
    """
    print('start')
    yield from func_iterable
    print('end')


def fib_demo() -> None:
    for i in fib(5):
        print(i)

    # Output:
    # 1
    # 1
    # 2
    # 3
    # 5

    wrap = fib_wrapper(fib(5))
    for i in wrap:
        print(i)

    # Output:
    # start
    # 1
    # 1
    # 2
    # 3
    # 5
    # end

    wrap_2 = fib_wrapper_2(fib(5))
    for i in wrap_2:
        print(i)

    # Output:
    # start
    # 1
    # 1
    # 2
    # 3
    # 5
    # end


class SpamException(Exception):
    pass


def writer() -> Generator:
    """
    A generator that echoes and prints the input.
    :return: Generator object
    """
    while True:
        try:
            w = yield  # 接收数据
        except SpamException:
            # 若是SpamException, 则打印***
            print('***')
        else:
            # 否则打印数据
            print(f'>> {w}')


def writer_wrapper(coro: Coroutine) -> Coroutine:
    """
    Wrapper function for the given coroutine.
    :param coro: coroutine
    :return: coroutine
    """
    coro.send(None)  # 启动协程
    while True:
        try:
            try:
                x = yield  # 接收数据
            except Exception as e:
                # 若是Exception, 将Exception传递给协程
                coro.throw(e)
            else:
                # 否则将数据传递给协程
                coro.send(x)
        except StopIteration:
            pass


def writer_wrapper_2(coro: Coroutine) -> Coroutine:
    """
    Wrapper function for the given coroutine by simply "yield from" the given
    coroutine.
    :param coro: coroutine
    :return: coroutine
    """
    yield from coro


def write_demo():
    wrap = writer_wrapper(writer())
    wrap.send(None)  # 启动协程
    for i in [0, 1, 2, 'spam', 4]:
        if i == 'spam':
            wrap.throw(SpamException)
        else:
            wrap.send(i)

    # Output:
    # >> 0
    # >> 1
    # >> 2
    # ***
    # >> 4


fib_demo()
write_demo()
