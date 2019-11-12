#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo for coroutine by "yield".
"""

__author__ = 'Ziang Lu'

from typing import Coroutine


def consumer() -> Coroutine:
    """
    Consumer coroutine.
    :return: coroutine
    """
    print('[CONSUMER] Starting consumer...')
    r = ''
    while True:
        n = yield r  # 1. 协程运行至第一个yield, 并挂起
        # 2. 接收参数n, 继续执行
        # 3. 生成结果r传出, 并挂起
        # 4 -> 2
        if not n:
            return
        print(f'[CONSUMER] Consuming {n}...')
        r = '200 OK'


def produce(consumer: Coroutine) -> None:
    """
    Producer coroutine.
    :param consumer: coroutine
    :return: None
    """
    consumer.send(None)  # 1. 启动协程
    n = 1
    while n <= 5:
        print(f'[PRODUCER] Producing {n}...')
        r = consumer.send(n)  # 2. 通过send(n)将参数n传给协程, 并挂起当前执行, 等待协程执行结果
        # 3. 接收协程传回的结果r
        # 4 -> 2
        print(f'[PRODUCER] Consumer return: {r}')
        n += 1
    consumer.close()


c = consumer()
produce(c)

# Output:
# [CONSUMER] Starting consumer...
# [PRODUCER] Producing 1...
# [CONSUMER] Consuming 1...
# [PRODUCER] Consumer return: 200 OK
# [PRODUCER] Producing 2...
# [CONSUMER] Consuming 2...
# [PRODUCER] Consumer return: 200 OK
# [PRODUCER] Producing 3...
# [CONSUMER] Consuming 3...
# [PRODUCER] Consumer return: 200 OK
# [PRODUCER] Producing 4...
# [CONSUMER] Consuming 4...
# [PRODUCER] Consumer return: 200 OK
# [PRODUCER] Producing 5...
# [CONSUMER] Consuming 5...
# [PRODUCER] Consumer return: 200 OK
