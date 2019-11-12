#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A simple demo of processing pipelines using coroutine.
"""

import sys
from typing import Coroutine

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
    source_read(
        filename=filename, target=grep(pattern='python', target=printer())
    )


if __name__ == '__main__':
    main(sys.argv[1])
