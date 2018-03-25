# Asynchronous IO

由于CPU的速度远远快于磁盘、网络等IO, 在一个线程中, CPU执行代码的速度极快, 然而一旦遇到IO操作, 如读写文件、发送网络数据时, 就需要等待IO操作才能完成, 才能继续进行下一步操作

=> 同步IO

=> 在IO过程中, 当前线程被挂起, 而其他需要CPU执行的代码就无法被当前线程执行了

<br>

* 一种解决办法: 使用多进程/多线程模型来并发执行代码

  为多个用户服务, 每个用户都会分配一个线程, 如果遇到IO导致线程被挂起, 其他用户的线程不受影响

<br>

* 另一种解决办法: 异步IO

  当代码需要执行一个耗时的IO操作时, 它只发出IO请求, 并不等待IO结果, 然后就去执行其他代码了; 一段时间后, 当IO结果返回时, 再通知CPU进行处理

<br>

# Coroutine

协程由同一个线程执行

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
# y
# 3
# z
```

*线程的上下文切换是由操作系统来完成, 而协程的上下文切换是由应用程序本身来完成*

**具体例子参见以下Python module:**

* **simple_yield.py**

* **yield_from.py**

* **yield_from_and_asyncio.py**

  用``asyncio``提供的``@asyncio.coroutine``可以把一个generator标记为coroutine类型, 然后在coroutine内部``yield from``调用另一个coroutine实现异步操作

<br>

## Coroutines vs Generators

* Generators produce data for iteration.

* Coroutines tend to consume value.

  *Coroutines are not related to iteration.*

<br>

## 协程的优势

1. 协程之间可以彼此"链接"起来

   对比线程, 操作系统是没有提供方式将不同的线程链接起来的

2. 极高的执行效率

   因为子程序 (协程) 切换不是线程切换, 而是由程序自身控制, 因此没有线程切换的开销

3. 不需要多线程的锁机制

   因为只有一个线程, 不需要对共享资源进行控制

<br>

## Practical Applications

### 1. Pipelines Processing

Coroutines can be used to set up pipes.

* You just chain coroutines together and push data through the pip with ``send()`` operation.
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

  Collects all data sent to it and process.

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

* copipe.py
* cobroadcast.py

### 2. Event Dispatching

Coroutines can be used to write various components that process event streams.

具体例子参见Curious Course on Coroutines and Concurrency文件夹中:

* basicsax.py & cosax.py
* cosax_bus.py

*One interesting thing about coroutines is that you can push the initial data source as low-level as you want to make it without rewriting all of the processing stages.*

* coexpat_bus.py

<br>

## Coroutines + Multi-threading / Multi-processing

You can package coroutines inside threads or subprocesses by adding extra layers.

具体例子参见Curious Course on Coroutines and Concurrency文件夹中:

* cothread.py
* coprocess.py & coprocess_bus.py

**本质上:**

**With coroutines, you can separate the implementation of a task from its execution environment:**

* **The coroutine is the implementation.**
* **The environment is whatever you choose (threads, subprocesses, network, etc.).**