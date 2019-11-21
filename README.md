This repo talks about asynchronous IO and its solution in Python, which is called coroutines.

# Asynchronous IO

由于CPU的速度远远快于磁盘、网络等IO, 在一个thread中, CPU执行代码的速度极快, 然而一旦遇到IO操作, 如读写文件、发送网络数据时, 就需要等待IO操作才能完成, 才能继续进行下一步操作.

=> 同步IO

=> 在IO过程中, 当前thread被挂起, 而其他需要CPU执行的代码就无法被当前thread执行了

<br>

* 一种解决办法: 使用multi-processing / multi-threading模型来并发执行代码

  为多个用户服务, 每个用户都会分配一个thread, 如果遇到IO导致thread被挂起, 其他用户的thread不受影响

<br>

* 另一种解决办法: 异步IO

  当代码需要执行一个耗时的IO操作时, 它只发出IO请求, 并不等待IO结果, 然后就去执行其他代码了; 一段时间后, 当IO结果返回时, 再通知CPU进行处理
  
  *注意: 对于CPU密集型任务, 使用异步IO并不能加快程序运行, 因为CPU本身并没有在等待.*

<br>

### 同步、异步、阻塞、非阻塞之间的关系

同步 vs 异步:   *关注的是消息通信机制*

阻塞 vs 非阻塞:   *关注的是程序在等待调用结果时的状态*

|                                                              | 阻塞<br>调用结果返回之前, 当前thread会被挂起. *一件事完全结束才开始另一件事.* | 非阻塞<br>在不能立即得到结果之前, 该调用不会阻塞当前thread, 当前thread可以去做其他工作. *一个任务没做完, 没有必要停在那里等它结束就可以开始下一个任务, 保证一直在干活没有等待.* | 注释                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **同步**<br>在发出一个调用时, 在没有得到结果之前, 该调用就不返回; 但是一旦调用返回, 就得到返回值了. 即由caller主动等待这个调用的结果. | Check                                                        | Check<br>需要主程序不断地去poll调用是否已经完成<br>Multi-threading实现, 即开启一个新的thread来发出调用, 即使这个新的thread被挂起也不影响main thread | 在发出一个调用时, 在没有得到结果之前, 可以挂起当前thread, 即阻塞; 也可以不挂起当前thread去做其他工作, 但是需要主程序不断地去poll调用有没有返回结果, 即非阻塞 |
| **异步**<br>在调用发出之后, 这个调用就直接返回了 (没有返回结果). 而是在调用发出后, callee通过状态、通知来通知caller, 或者通过callback function来处理这个调用. |                                                              | Check<br>当调用已经做完的时候, 会自动通知主程序回来继续操作调用的结果<br>Coroutine实现 |                                                              |

<br>

# Coroutine

协程由同一个thread执行

协程看上去也是子程序, 但执行过程中, 在子程序 (协程) 内部可中断, 然后转而执行别的子程序 (协程) , 在适当的时候再返回来接着执行

```python
def A():
    print('1')
    print('2')
    print('3')

def B():
    print('x')
    print('y')
    print('z')

# 假设由协程执行, 在执行A()的过程中, 可以随时中断, 去执行B(), B()也可能在执行过程中中断再去执行A(), 结果可能是:
# 1
# 2
# x
# 3
# y
# z
```

*thread的上下文切换是由操作系统来完成, 而协程的上下文切换是由应用程序本身来完成*

**具体例子参见以下Python module:**

* `simple_yield.py`

* `yield_from.py`

* `yield_from_and_asyncio.py`

  用``asyncio``提供的``@asyncio.coroutine``可以把一个generator标记为coroutine类型, 然后在coroutine内部``yield from``调用另一个coroutine实现异步操作
  
  ***
  
  用这种方式实现的coroutine本质上是一个"generator-based coroutine", 二者的实现看起来很相似, 而其区别在于:
  
  * Generators produce data for iteration;
  * Coroutines tend to consume value, i.e., coroutines are not related to iteration.
  
  ***
  
* `async_and_await.py`

  本质上是一个语法糖, 用`async def / await`来代替之前的`@asyncio.coroutine / yield from`

* 注意, `asyncio`中也提供了各种`Queue`的实现来帮助在coroutine之间通信, 参见:

  `comm_via_queue.py`

<br>

## Practical Applications

### 1. Pipeline Processing

Coroutines can be used to set up pipes.

* You just chain coroutines together and push data through the pipe with ``send()`` operation.
* If you built a collection of simple data processing components, you can glue them together into complex arrangemenets of pipes, branches, merging, etc.

The pipeline needs:

* A source (producer)

  The source drives the entire pipeline

  ```python
  def source(target):
      while not done:
          item = produce_an_item()
          ...
          target.send(item)
          ...
      target.close()
  ```

  It is typically **not** a coroutine.

* Intermediate coroutines

  ```python
  @coroutine
  def filter(target):
      try:
          while True:
              item = yield
              # Data filtering/processing
              ...
              target.send(item)
      except GeneratorExit as e:
          target.throw(e)
  ```

* A sink (consumer)

  Collects all data sent to it and process

  ```python
  @coroutine
  def sink():
      try:
          while True:
              item = yield
              ...
      except GeneratorExit:  # Handle close() operation
          # Done
          ...
  ```

具体例子参见 Curious Course on Coroutines and Concurrency文件夹中:

* `copipe.py`
* `cobroadcast.py`

<br>

### 2. Event Dispatching

Coroutines can be used to write various components that process event streams.

具体例子参见Curious Course on Coroutines and Concurrency文件夹中:

* `basicsax.py` & `cosax.py`
* `cosax_bus.py`

*One interesting thing about coroutines is that you can push the initial data source as low-level as you want to make it without rewriting all of the processing stages.*

* `coexpat_bus.py`

<br>

## Comparison between Multi-threading, Multi-processing, and Asynchronous IO in Python

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

* 参见`asyncio_subprocess.py`  [由`asyncio`模块控制]

<br>

#### Coroutine -> Thread

<u>从coroutine中fire new thread</u>

* 同时参考`cothread.py`  [由`asyncio`模块控制]

<br>

#### Subprocess [Coroutine]

<u>把coroutine包在subprocess之中</u>

*(创建一个process pool (subprocesses), 在其中放入async的task (coroutine))*

* 参见https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/Multi-processing%20and%20Multi-threading%20in%20Python/Multi-processing/multiprocessing_async.py  [两种实现方式, 分别由`concurrent.futures`模块和`multiprocessing`模块控制]

* 同时参考`coprocess.py` & `coprocess_bus.py`  [由`asyncio`模块控制]

**适用情况: 如果有很多CPU计算密集型任务, 可以把它们放入一个process pool, 充分利用多核的计算能力, 提高计算效率**

<br>

#### Thread [Coroutine]

把coroutine包在thread之中

*(创建一个thread pool, 在其中放入async的task (coroutine))*

* 参见https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/Multi-processing%20and%20Multi-threading%20in%20Python/Multi-threading/multithreading_async.py  [由`concurrent.futures`模块控制]
* 另一种实现方式: 参见`multithreading_async.py`  [由`concurrent.futures`模块和`asyncio`模块共同控制]

**适用情况: 如果有很多IO密集型任务, 可以把他们放入thread pool**

<br>

**本质上:**

**With coroutines, you can separate the implementation of a task from its execution environment:**

* **The coroutine is the implementation.**
* **The environment is whatever you choose (subprocesses, threads, network, etc.).**

<br>

# License

This repo is distributed under the <a href="https://github.com/Ziang-Lu/Asynchronous-IO-and-Coroutines-in-Python/blob/master/LICENSE">MIT license</a>.
