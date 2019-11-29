# Comparison between Concurrent Strategies

After studying asynchronous IO in Python, we are able to compare these three concurrent strategies:

|                                         | Multi-processing                                             | Multi-threading                                              | Asynchronous IO                                              |
| --------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Use blocking standard library functions | **YES**                                                      | **YES**                                                      | NO                                                           |
| Optimize waiting periods                | YES<br>Preemptive, because the OS handles subprocess scheduling | YES<br>Preemptive, because the OS handles thread scheduling  | YES<br>Cooperative, because the Python interpreter itself handles coroutine scheduling |
| Use all CPU cores                       | **YES**<br>=> 可以把thread/coroutine包在subprocess之中, 达到充分利用多核CPU的目的<br>e.g., 把coroutine包在subprocess之中: https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/Multi-processing%20and%20Multi-threading%20in%20Python/Multi-processing/multiprocessing_async.py<br>同时参考`coprocess.py`和`coprocess_bus.py` | NO                                                           | NO                                                           |
| GIL interference                        | **NO**                                                       | Some<br>(对于IO密集型程序, 由于CPU可以在thread等待期间执行其他thread, NO)<br>(对于CPU计算密集型程序, YES) | **NO**                                                       |
| Scalability<br>(本质上, 与开销有关)     | Low                                                          | Medium                                                       | **High**<br>=> 对于真正需要巨大scalability时, 才考虑使用async<br>i.e., server需要处理大量requests时 |

### 协程的优势

1. 极高的执行效率

   因为子程序 (协程) 切换不是thread切换, 而是由程序自身控制, 因此没有thread切换的开销

2. 不需要multi-threading的锁机制

   因为只有一个thread, 不需要对共享资源进行控制

   *-> 在一个子程序 (协程) 两次`await` call之间, 共享资源不会被其他子程序 (协程) 更改*

3. 高可扩展性 (High scalability)

   (详见表格中描述)

4. 协程之间可以彼此"链接"起来

   对比thread, 操作系统是没有提供方式将不同的thread链接起来的

   (=> 前面的pipeline processing应用模式)

<br>

## Async + Multi-threading / Multi-processing

#### Coroutine -> Subprocesses

<u>从coroutine中spawn new subprocess</u>

* 由`asyncio`模块控制

  ```python
  import asyncio
  import sys
  
  
  async def get_date() -> str:
      # Spawn a new subprocess, execute some code, and setting the new subprocess
      # communicates back to the calling process via a pipe
      code = 'from datetime import datetime; print(datetime.now())'
      p = await asyncio.create_subprocess_exec(
          sys.executable, '-c', code, stdout=asyncio.subprocess.PIPE
      )
  
      # Read output from the new subprocess via the pipe
      data = await p.stdout.readline()
      line = data.decode('utf-8').rstrip()
  
      # Wait for the new subprocess to terminate
      await p.wait()
      return line
  
      # Note that this can also be done in lower-level API (using the event loop
      # directly)
  
  
  date = asyncio.run(get_date())
  print(f'Current date: {date}')
  
  # Output:
  # Current date: 2019-11-15 14:34:36.622387
  
  ```

<br>

#### Coroutine -> Thread

<u>从coroutine中fire new thread</u>

* 同时参考`cothread.py`  [由`asyncio`模块控制]

<br>

#### Subprocess [Coroutine]

<u>把coroutine包在subprocess之中</u>

*(创建一个process pool (subprocesses), 在其中放入async的task (coroutine))*

* 参见https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/Multi-processing%20and%20Multi-threading%20in%20Python/Multi-processing/multiprocessing_async.py  [两种实现方式, 分别由`concurrent.futures`模块和`multiprocessing`模块控制]

  ```python
  import concurrent.futures as cf
  import os
  import random
  import time
  from multiprocessing import Pool
  
  
  def long_time_task(name: str) -> float:
      print(f"Running task '{name}' ({os.getpid()})...")
      start = time.time()
      time.sleep(random.random() * 3)
      end = time.time()
      time_elapsed = end - start
      print(f"Task '{name}' runs {time_elapsed:.2f} seconds.")
      return time_elapsed
  
  
  def demo1():
      # With "concurrent.futures" module
      print(f'Parent process {os.getpid()}')
      with cf.ProcessPoolExecutor(max_workers=4) as pool:  # 开启一个4个进程的进程池
          start = time.time()
          # 在进程池中执行多个任务, 但是在主进程中是async的
          futures = [pool.submit(long_time_task, f'Task-{i}') for i in range(5)]  # Will NOT block here
  
          # Since submit() method is asynchronous (non-blocking), by now the tasks
          # in the process pool are still executing, but in this main process, we
          # have successfully proceeded to here.
          total_running_time = 0
          for future in cf.as_completed(futures):
              total_running_time += future.result()
  
          print(f'Theoretical total running time: {total_running_time:.2f} '
                f'seconds.')
          end = time.time()
          print(f'Actual running time: {end - start:.2f} seconds.')
      print('All subprocesses done.')
  
  
  def demo2():
      # With "multiprocessing" module
      with Pool(4) as pool:  # 开启一个4个进程的进程池
          start = time.time()
          # 在进程池中执行多个任务, 但是在主进程中是async的
          results = [
              pool.apply_async(func=long_time_task, args=(f'Task-{i}',))
              for i in range(5)
          ]  # Will NOT block here
          pool.close()  # 调用close()之后就不能再添加新的任务了
  
          # Since apply_async() method is asynchronous (non-blocking), by now the
          # tasks in the process pool are still executing, but in this main
          # process, we have successfully proceeded to here.
          total_running_time = 0
          for result in results:  # AsyncResult
              total_running_time += result.get(timeout=10)  # Returns the result when it arrives
  
          print(f'Theoretical total running time: {total_running_time:.2f} '
                f'seconds.')
          end = time.time()
          print(f'Actual running time: {end - start:.2f} seconds.')
      print('All subprocesses done.')
  ```

* 同时参考`coprocess.py` & `coprocess_bus.py`  [由`asyncio`模块控制]

**适用情况: 如果有很多CPU计算密集型任务, 可以把它们放入一个process pool, 充分利用多核的计算能力, 提高计算效率**

<br>

#### Thread [Coroutine]

把coroutine包在thread之中

*(创建一个thread pool, 在其中放入async的task (coroutine))*

* 参见https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/Multi-processing%20and%20Multi-threading%20in%20Python/Multi-threading/multithreading_async.py  [由`concurrent.futures`模块控制]

  ```python
  import concurrent.futures as cf
  
  import requests
  
  sites = [
      'http://europe.wsj.com/',
      'http://some-made-up-domain.com/',
      'http://www.bbc.co.uk/',
      'http://www.cnn.com/',
      'http://www.foxnews.com/',
  ]
  
  
  def site_size(url: str) -> int:
      response = requests.get(url)
      return len(response.content)
  
  
  # Create a thread pool with 10 threads
  with cf.ThreadPoolExecutor(max_workers=10) as pool:
      # Submit tasks for execution
      future_to_url = {pool.submit(site_size, url): url for url in sites}  # Will NOT block here
  
      # Since submit() method is asynchronous (non-blocking), by now the tasks in
      # the thread pool are still executing, but in this main thread, we have
      # successfully proceeded to here.
      # Wait until all the submitted tasks have been completed
      for future in cf.as_completed(future_to_url):
          url = future_to_url[future]
          try:
              # Get the execution result
              page_size = future.result()
          except Exception as e:
              print(f'{url} generated an exception: {e}')
          else:
              print(f'{url} page is {page_size} bytes.')
  ```

* 第二种实现方式: 由`concurrent.futures`模块和`asyncio`模块共同控制

  ```python
  import asyncio
  import concurrent.futures as cf
  from typing import Tuple
  
  import requests
  
  
  def site_size(url: str) -> Tuple[str, int]:
      response = requests.get(url)
      return url, len(response.content)
  
  
  async def main():
      # Create a thread pool with 10 threads
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
  ```

* 第三种实现方式: 由`gevent`模块控制

  ```python
  import gevent
  import requests
  from gevent.threadpool import ThreadPool
  
  # Create a thread pool with 10 threads
  pool = ThreadPool(maxsize=10)
  # Schedule the tasks for execution
  results = [pool.spawn(site_size, url) for url in sites]
  # Wait until all the scheduled tasks have been finished
  for result in results:  # AsyncResult
      res = result.result()
      if not isinstance(res, Exception):
          url, page_size = res
          print(f'{url} page is {page_size} bytes.')
  ```

**适用情况: 如果有很多IO密集型任务, 可以把他们放入thread pool**

<br>

**本质上:**

**With coroutines, you can separate the implementation of a task from its execution environment:**

* **The coroutine is the implementation.**
* **The environment is whatever you choose (subprocesses, threads, network, etc.).**

