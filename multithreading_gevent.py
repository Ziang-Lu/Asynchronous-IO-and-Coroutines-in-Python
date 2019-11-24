#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
We can assign asynchronous tasks into a thread pool.

Third implementation:
This implementation is controlled by "gevent" module.
"""

__author__ = 'Ziang Lu'

import gevent
from gevent import monkey

# Patch all the IO operations
monkey.patch_all()
# From official documentation:
# When monkey patching, it is recommended to do so as early as possible in the
# lifetime of the program. If possible, monkey patching should be the first
# lines executed, ideally before any other imports.

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


greenlets = [gevent.spawn(site_size, url) for url in sites]
gevent.joinall(greenlets)
