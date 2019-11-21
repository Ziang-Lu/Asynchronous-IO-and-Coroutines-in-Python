#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
We can assign asynchronous tasks into a thread pool.

First implementation:
https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/Multi-processing%20and%20Multi-threading%20in%20Python/Multi-threading/multithreading_async.py
(Controlled by "concurrent.futures" module)

This second implementation is controlled by "concurrent.futures" module and
"asyncio" module together.
"""

__author__ = 'Ziang Lu'

import asyncio
import concurrent.futures as cf
from typing import Tuple

import requests

sites = [
    'http://europe.wsj.com/',
    'http://some-made-up-domain.com/',
    'http://www.bbc.co.uk/',
    'http://www.cnn.com/',
    'http://www.foxnews.com/',
]


def site_size(url: str) -> Tuple[str, int]:
    """
    Returns the page size in bytes of the given URL.
    :param url: str
    :return: tuple
    """
    response = requests.get(url)
    return url, len(response.content)


async def main():
    # Create a thread pool with 10 thrads
    with cf.ThreadPoolExecutor(max_workers=10) as pool:
        loop = asyncio.get_event_loop()
        # Submit tasks for execution
        tasks = [loop.run_in_executor(pool, site_size, url) for url in sites]

        # Since run_in_executor() method is asynchronous (non-blocking), by now
        # the tasks the thread pool are still executing, but in this main
        # thread, we have successfully proceeded here.
        # Wait until all the submitted tasks have been completed
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if not isinstance(result, Exception):
                url, page_size = result
                print(f'{url} page is {page_size} bytes.')


asyncio.run(main())
