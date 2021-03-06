#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An example showing how to wrap coroutines within a subprocess.
The calling process and the new subprocess communicate via a pipe.
"""

import pickle
import subprocess
import xml.sax

from coroutine import coroutine
from cosax import EventHandler
from cosax_bus import buses_to_dicts


@coroutine
def send_to(f):
    """
    A coroutine that receives items and pickles them to the given file (pipe).
    :param f: file
    :return: coroutine
    """
    try:
        while True:
            item = yield
            pickle.dump(item, f)
            f.flush()
    except StopIteration:
        f.close()


def main():
    # Start a new subprocess, which wraps some connected coroutines, and
    # listening on a pipe.
    p = subprocess.Popen(['python3', 'coprocess_bus.py'], stdin=subprocess.PIPE)

    # Set a sender coroutine to send data to the pipe that the new subprocess is
    # listening on
    sender = send_to(p.stdin)
    xml.sax.parse(
        source='allroutes.xml',
        handler=EventHandler(target=buses_to_dicts(target=sender))
    )


if __name__ == '__main__':
    main()
