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

  用`asyncio`提供的``@asyncio.coroutine``可以把一个generator标记为coroutine类型, 然后在coroutine内部``yield from``调用另一个coroutine实现异步操作
  
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

***

### Alternative to `asyncio` module: `gevent` module

* `Greenlet` is a light-weight cooperatively-scheduled execution unit.

  =>`Greenlet`就像一个coroutine

* 像`asyncio`一样, 在`gevent` (`greenlet`) 内部, 有一个event loop来执行`Greenlet`, 只不过使用了来自第三方的性能更好的event loop实现

***

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

# License

This repo is distributed under the <a href="https://github.com/Ziang-Lu/Asynchronous-IO-and-Coroutines-in-Python/blob/master/LICENSE">MIT license</a>.
