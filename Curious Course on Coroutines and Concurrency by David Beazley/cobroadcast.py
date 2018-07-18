#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A simple demo of processing pipelines using coroutine, and broadcasting a data
stream to multiple coroutines.
"""

import sys
from typing import Coroutine, List

from coroutine import coroutine


def source_read(filename: str, target: Coroutine) -> None:
    """
    Reads the given file line by line, and feeds each read line to the given
    target coroutine.
    :param filename: str
    :param target: coroutine
    :return: None
    """
    with open(filename, 'rt') as f:
        while True:
            line = f.readline()
            if not line:
                break
            target.send(line)
        target.close()


@coroutine
def broadcast(targets: List[Coroutine]):
    """
    A coroutine that broadcasts the read lines to the given targets.
    :param targets: list[coroutine]
    :return: coroutine
    """
    try:
        while True:
            line = yield
            for target in targets:
                target.send(line)
    except GeneratorExit as e:
        for target in targets:
            target.throw(e)


@coroutine
def grep(pattern: str, target: Coroutine):
    """
    A coroutine that searches for the given pattern, and feeds the filtered line
    to the given target coroutine.
    :param pattern: str
    :param target: coroutine
    :return: coroutine
    """
    try:
        while True:
            line = yield
            if pattern in line:
                target.send(line)
    except GeneratorExit as e:
        target.throw(e)


@coroutine
def printer():
    """
    A coroutine that prints the received line.
    :return: coroutine
    """
    try:
        while True:
            line = yield
            print(line, end='')
    except GeneratorExit:
        pass


def main(filename):
    p = printer()
    source_read(
        filename=filename,
        target=broadcast(
            targets=[
                grep(pattern='python', target=p),
                grep(pattern='swig', target=p),
                grep(pattern='ply', target=p)
            ]
        )
    )


if __name__ == '__main__':
    main(sys.argv[1])
