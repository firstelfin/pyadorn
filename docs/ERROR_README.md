# pyadorn.error_factory

python错误管理工具, 保护接口异常中断, 实现错误的监管与分类.

当发生错误时，支持以下三种方式回传错误:

| 类型   | 装饰器生成范例                                                                                                     | 描述                               |
| ------ | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------- |
| 方案一 | `error_factory(error_debug=False, error_response=error_status)`                                                  | 追加到指定的全局变量               |
| 方案二 | `error_factory(error_debug=False, error_key="error", response_factory=ResponseData)`                             | 追加错误对象到返回体的指定字段     |
| 方案三 | `error_factory(error_debug=False, error_attrs=["error_code", None, "error_msg"], response_factory=ResponseData)` | 追加错误属性内容到返回体的指定字段 |

`error_factory`生成的装饰器，即可装饰类与函数，也可以装饰异步与同步函数。

## 装饰工厂参数说明

错误管理使用工厂进行了装饰器的封装。工厂(`error_factory`)对以下功能进行了构建：

| 功能                             | 参数名               | 类型                        |
| -------------------------------- | -------------------- | --------------------------- |
| 是否打印错误堆栈信息             | `error_debug`      | `bool`                    |
| 全局错误记录                     | `error_response`   | `Optional[list]`          |
| 在返回体字段上追加错误对象       | `error_key`        | `Optional[str]`           |
| 在返回体对象指定字段记录错误属性 | `error_attrs`      | `Optional[list[str]]`     |
| 错误信息堆栈记录最后一条或全栈   | `traceback_mode`   | `Literal['full', 'last']` |
| 返回结构体的生成对象             | `response_factory` | `Callable`                |
| 待装饰的类方法                   | `methods`          | `Optional[List[str]]`     |
| 不装饰的类方法                   | `filters`          | `Optional[List[str]]`     |

## 方案一、错误装饰器打印错误日志信息

```python
from pyadorn.errDecorator import error_factory
error_decorator0 = error_factory(error_debug=True, error_response=None, error_key="pyadorn", response_factory=dict)

@error_decorator0
class PyAdornErrorPrint:

    def map(self, names: list[str], numbers: list[int]):
        return {name: number for name, number in zip(names, numbers)}

def test_error_logger():
    from pprint import pprint
    py_adorn_error = PyAdornErrorPrint()
    outputs = py_adorn_error.map(["name", "age"], 2)
    print("Outputs:(装饰器设置打印错误信息, 并将错误对象注册到字典的pyadorn键中)")
    pprint(outputs)
```

输出信息如下:

```python
2026-07-05 16:25:42.817 | ERROR    | pyadorn.errDecorator:sync_wrapper:145 - 捕获异常:
Traceback (most recent call last):

  File "/Users/elfindan/project/pyadorn/test/test_error.py", line 98, in <module>
    test_error_logger()
    └ <function test_error_logger at 0x106506a20>

  File "/Users/elfindan/project/pyadorn/test/test_error.py", line 30, in test_error_logger
    outputs = py_adorn_error.map(["name", "age"], 2)
              │              └ <function PyAdornErrorPrint.map at 0x105f5b1a0>
              └ <__main__.PyAdornErrorPrint object at 0x1064ef110>

> File "/Users/elfindan/project/pyadorn/.venv/lib/python3.12/site-packages/pyadorn/errDecorator.py", line 142, in sync_wrapper
    res = func(*args, **kwargs)
          │     │       └ {}
          │     └ (<__main__.PyAdornErrorPrint object at 0x1064ef110>, ['name', 'age'], 2)
          └ <function PyAdornErrorPrint.map at 0x106506980>

  File "/Users/elfindan/project/pyadorn/test/test_error.py", line 25, in map
    return {name: number for name, number in zip(names, numbers)}
                                                 │      └ 2
                                                 └ ['name', 'age']

TypeError: 'int' object is not iterable
Outputs:(装饰器设置打印错误信息, 并将错误对象注册到字典的pyadorn键中)
{'pyadorn': [ErrorInfo(code=599,
                       msg="'int' object is not iterable",
                       traceback='  File '
                                 '"/Users/elfindan/project/pyadorn/test/test_error.py", '
                                 'line 25, in map\n'
                                 '    return {name: number for name, number in '
                                 'zip(names, numbers)}',
                       timestamp='2026-07-05 16:25:42')]}
```

## 方案二、错误装饰器将错误对象追加全局变量

```python
error_status = []
error_decorator1 = error_factory(error_debug=False, error_response=error_status)
@error_decorator1
class PyAdornErrorPrint1:

    def map(self, names: list[str], numbers: list[int]):
        return {name: number for name, number in zip(names, numbers)}

def test_error_status():
    from pprint import pprint
    py_adorn_error = PyAdornErrorPrint1()
    outputs = py_adorn_error.map(["name", "age"], 2)
    print("Outputs:(装饰器设置不打印错误信息, 并将错误对象注册到列表中)")
    pprint(outputs)
    print("全局错误列表error_status:")
    pprint(error_status)
```

输出信息如下:

```python
Outputs:(装饰器设置不打印错误信息, 并将错误对象注册到列表中)
{}
全局错误列表error_status:
[ErrorInfo(code=599,
           msg="'int' object is not iterable",
           traceback='  File '
                     '"/Users/elfindan/project/errguard/test/test_error.py", '
                     'line 39, in map\n'
                     '    return {name: number for name, number in zip(names, '
                     'numbers)}',
           timestamp='2026-07-05 16:30:48')]
```

## 方案三、错误装饰器将错误对象追加到返回体的指定字段

```python
error_decorator2 = error_factory(error_debug=False, error_key="error", response_factory=ResponseData)

@error_decorator2
class PyAdornErrorPrint2:

    def map(self, names: list[str], numbers: list[int]):
        return {name: number for name, number in zip(names, numbers)}

def test_error_response_object():
    from pprint import pprint
    py_adorn_error = PyAdornErrorPrint2()
    outputs = py_adorn_error.map(["name", "age"], 2)
    print("Outputs:")
    pprint(outputs)
```

输出信息如下:

```python
Outputs:
ResponseData(code=0,
             msg='success',
             name='pyadorn',
             bbox=[],
             error=[ErrorInfo(code=599,
                              msg="'int' object is not iterable",
                              traceback='  File '
                                        '"/Users/elfindan/project/errguard/test/test_error.py", '
                                        'line 71, in map\n'
                                        '    return {name: number for name, '
                                        'number in zip(names, numbers)}',
                              timestamp='2026-07-05 16:36:11')],
             error_code=0,
             error_msg='success')
```

## 方案四、错误装饰器将错误属性内容指定到返回体的指定字段

```python
error_decorator3 = error_factory(error_debug=False, error_attrs=["error_code", None, "error_msg"], response_factory=ResponseData)
@error_decorator3
class PyAdornErrorPrint3:

    def map(self, names: list[str], numbers: list[int]):
        return {name: number for name, number in zip(names, numbers)}
    
def test_error_response_object2():
    from pprint import pprint
    py_adorn_error = PyAdornErrorPrint3()
    outputs = py_adorn_error.map(["name", "age"], 2)
    print("Outputs:")
    pprint(outputs)
```

输出信息如下:

```python
Outputs:
ResponseData(code=0,
             msg='success',
             name='pyadorn',
             bbox=[],
             error=[],
             error_code=599,
             error_msg='  File '
                       '"/Users/elfindan/project/errguard/test/test_error.py", '
                       'line 87, in map\n'
                       '    return {name: number for name, number in '
                       'zip(names, numbers)}')
```

## 方案五、异步错误装饰器

```python
# 异步函数测试
@error_decorator3
async def async_error_func():
    await asyncio.sleep(10)
    raise ValueError("网络错误")


def test_async_error_func():
    from pprint import pprint
    result = asyncio.run(async_error_func())
    print("Outputs:")
    pprint(result)
```

输出信息如下:

```python
Outputs:
ResponseData(code=0,
             msg='success',
             name='pyadorn',
             bbox=[],
             error=[],
             error_code=599,
             error_msg='  File '
                       '"/Users/elfindan/project/errguard/test/test_error.py", '
                       'line 101, in async_error_func\n'
                       '    raise ValueError("网络错误")')
```

这里的异步函数使用`asyncio.run`来运行，因为`async_error_func`是一个异步函数，需要通过`asyncio.run`来执行, 实际这一行是阻塞执行的, 所以要等10秒再打印输出信息。什么时候使用异步函数, 建议IO操作密集的时候, 计算密集任务千万别使用异步函数.
