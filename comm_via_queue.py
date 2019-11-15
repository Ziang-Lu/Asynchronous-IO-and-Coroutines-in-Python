#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo for coroutines to communicate via a queue.
"""

__author__ = 'Ziang Lu'

import asyncio
import random
import time
from asyncio import Queue
from typing import Coroutine


async def worker(name: str, q: Queue) -> Coroutine:
    """
    Worker coroutine.
    :param name: str
    :param q: Queue
    :return: coroutine
    """
    while True:
        sleep_for = await q.get()
        await asyncio.sleep(sleep_for)
        q.task_done()
        print(f'{name} has slept for {sleep_for:.2f} seconds')


async def main():
    q = Queue()
    # Generate some random timings and put them into the queue
    total_sleep_time = 0
    for _ in range(20):
        sleep_for = random.uniform(0.05, 1.0)
        total_sleep_time += sleep_for
        q.put_nowait(sleep_for)

    # Create 3 worker tasks to process the queue concurrently
    tasks = []
    for i in range(3):
        task = asyncio.create_task(worker(f'Worker-{i}', q))
        tasks.append(task)

    # Wait until the queue is fully processed
    started_at = time.monotonic()
    await q.join()
    total_slept_for = time.monotonic() - started_at

    # Since a worker task runs in an infinite loop, we need to cancel our worker
    # tasks.
    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    print('==========')
    print(f'3 workers slept in parallel for {total_slept_for:.2f} seconds')
    print(f'Total expected sleep time: {total_sleep_time:.2f} seconds')


asyncio.run(main())

# Output:
# Worker-0 has slept for 0.20 seconds
# Worker-1 has slept for 0.53 seconds
# Worker-2 has slept for 0.96 seconds
# Worker-1 has slept for 0.45 seconds
# Worker-0 has slept for 1.00 seconds
# Worker-2 has slept for 0.35 seconds
# Worker-2 has slept for 0.15 seconds
# Worker-2 has slept for 0.09 seconds
# Worker-1 has slept for 0.77 seconds
# Worker-0 has slept for 0.66 seconds
# Worker-2 has slept for 0.53 seconds
# Worker-1 has slept for 0.36 seconds
# Worker-1 has slept for 0.30 seconds
# Worker-0 has slept for 0.63 seconds
# Worker-2 has slept for 0.50 seconds
# Worker-1 has slept for 0.46 seconds
# Worker-0 has slept for 0.44 seconds
# Worker-2 has slept for 0.35 seconds
# Worker-1 has slept for 0.54 seconds
# Worker-0 has slept for 0.71 seconds
# =====
# 3 workers slept in parallel for 3.66 seconds
# Total expected sleep time: 9.97 seconds
