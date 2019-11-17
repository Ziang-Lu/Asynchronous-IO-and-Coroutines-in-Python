#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An example showing how to spawn new subprocesses within a coroutine.
The calling process and the new subprocess communicate via a pipe.

Basically, this can be done in both higher-level API (using asyncio module
functions) and lower-level API (using the event loop directly).
"""

__author__ = 'Ziang Lu'

import asyncio
import sys


async def get_date() -> str:
    """
    Coroutine to spawn a new subprocess,
    :return: str
    """
    code = 'from datetime import datetime; print(datetime.now())'
    process = await asyncio.create_subprocess_exec(
        sys.executable, '-c', code, stdout=asyncio.subprocess.PIPE
    )

    data = await process.stdout.readline()
    line = data.decode('utf-8').rstrip()

    await process.wait()
    return line


date = asyncio.run(get_date())
print(f'Current date: {date}')

# Output:
# Current date: 2019-11-15 14:34:36.622387
