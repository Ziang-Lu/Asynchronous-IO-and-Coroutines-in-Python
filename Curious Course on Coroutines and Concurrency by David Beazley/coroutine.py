#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A module that defines a decorator that takes care of automatically priming a
coroutine on call.
"""


def coroutine(func):
    """
    Decorator that takes care of automatically priming the given coroutine on
    call.
    :param func: coroutine
    :return: coroutine
    """
    def auto_start_func(*args, **kwargs):
        coro = func(*args, **kwargs)
        coro.send(None)  # Automatically prime the coroutine
        return coro
    return auto_start_func


@coroutine
def grep(pattern):
    """
    A coroutine that searches for the given pattern (like Unix command "grep").
    Note that this coroutine also catches the close() operation
    :param pattern: str
    :return: coroutine
    """
    print('Looking for %s' % pattern)
    try:
        while True:
            line = yield
            if pattern in line:
                print(line)
    except GeneratorExit:
        print('Going away. Goodbye!')


def main():
    g = grep('python')
    # Notice how you don't need a send(None) call here
    g.send('Yeah, but no, but yeah, but no')
    g.send('A series of tubes')
    g.send('python generators rock!')
    g.close()


if __name__ == '__main__':
    main()


# Output:
# Looking for python
# python generators rock!
# Going away. Goodbye!
