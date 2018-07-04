#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo for the usage of "yield from" with asyncio module.
"""

__author__ = 'Ziang Lu'

import asyncio
import threading


@asyncio.coroutine  # 把hello()变成一个协程
def hello():
    print('Hello, world! (%s)' % threading.current_thread())
    yield from asyncio.sleep(delay=1)  # asyncio.sleep()也是一个coroutine object
    # 所以线程不会等待asyncio.sleep(), 而是直接挂起并执行下一个消息循环
    # 即可以把asyncio.sleep(1)看成一个耗时1秒的IO操作, 在此期间, 主线程并未等待, 而是去执行EventLoop中其他可以执行的
    # coroutine了, 从而实现并发
    print('Hello again! (%s)' % threading.current_thread())


def hello_demo() -> None:
    # asyncio的编程模型就是一个事件循环
    # 一方面, 它类似于CPU, 顺序执行协程的代码; 另一方面, 它相当于操作系统, 完成协程的调度

    # 从asyncio模块中直接获取一个EventLoop的引用
    loop = asyncio.get_event_loop()
    # 把需要执行的协程扔到EventLoop中执行, 顺序执行某个协程, 遇到yield from就挂起, 去执行另一个协程, 再遇到yield from
    # 再挂起, 再执行下一个协程, 如此循环; 直到某个协程得到了yield from的返回值, 便继续从该yield from语句向下执行, 直到所有的
    # 协程执行完毕退出, 这就实现了异步IO
    tasks = [hello(), hello()]
    loop.run_until_complete(future=asyncio.wait(tasks))

    # Output:
    # Hello, world! (<_MainThread(MainThread, started 4320760640)>)
    # Hello, world! (<_MainThread(MainThread, started 4320760640)>)
    # (Will be pending here for around 1 second)
    # Hello again! (<_MainThread(MainThread, started 4320760640)>)
    # Hello again! (<_MainThread(MainThread, started 4320760640)>)

    # From the printed thread information, the two coroutines are run by the
    # same thread concurrently.


@asyncio.coroutine
def wget(host):
    print('wget %s...' % host)
    reader, writer = yield from asyncio.open_connection(host=host, port=80)
    header = 'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % host
    writer.write(header.encode('utf-8'))
    yield from writer.drain()
    while True:
        line = yield from reader.readline()
        # Only read the header by checking against the first blank line
        if line == b'\r\n':
            break
        print('%s header > %s' % (host, line.decode('utf-8').rstrip()))
    writer.close()


def wget_demo() -> None:
    loop = asyncio.get_event_loop()
    tasks = [wget(host)
             for host in ['www.sina.com.cn', 'www.sohu.com', 'www.163.com']]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    # Output:
    # wget www.163.com...
    # wget www.sina.com.cn
    # wget www.sohu.com...
    # www.sina.com.cn header > HTTP/1.1 200 OK
    # www.sina.com.cn header > Date: Fri, 9 Feb 2018 02:21:45 GMT
    # ...
    # www.sina.com.cn header > Connection: close
    # www.163.com header > HTTP/1.0 302 Moved Temporarily
    # www.163.com header > Server: Cdn Cache Server V2.0
    # ...
    # www.163.com header > Connection: close
    # www.sohu.com header > HTTP/1.1 200 OK
    # www.sohu.com header > Content-Type: text/html;charset=UTF-8
    # ...
    # www.sohu.com header > FSS-Proxy: Powered by 9863722.11239988.17665343


def main():
    hello_demo()
    wget_demo()


if __name__ == '__main__':
    main()
