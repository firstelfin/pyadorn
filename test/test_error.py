import sys
sys.path.append('..') # Add the parent directory to the system path
from pyadorn.errDecorator import error_factory
from pyadorn.tools import traceback_info, ErrorInfo, get_last_traceback_info
import sys
import traceback
from loguru import logger


# 打印错误详情, 并将错误信息使用字典返回, 指定字典的键为pyadorn
error_decorator0 = error_factory(error_debug=True, error_response=None, error_key="pyadorn", response_factory=dict)
# 收集错误对象到指定列表, 不打印错误信息
error_status = []
error_decorator1 = error_factory(error_debug=False, error_response=error_status)

class MatchError(Exception):
    def __init__(self, msg, code=599):
        self.msg = msg
        self.code = code

@error_decorator0
class PyAdornErrorPrint:

    def map(self, names: list[str], numbers: list[int]):
        return {name: number for name, number in zip(names, numbers)}

def test_error_logger():
    from pprint import pprint
    py_adorn_error = PyAdornErrorPrint()
    outputs = py_adorn_error.map(["name", "age"], 2)  # type: ignore
    print("Outputs:(装饰器设置打印错误信息, 并将错误对象注册到字典的pyadorn键中)")
    pprint(outputs)


@error_decorator1
class PyAdornErrorPrint1:

    def map(self, names: list[str], numbers: list[int]):
        return {name: number for name, number in zip(names, numbers)}


def test_error_status():
    from pprint import pprint
    py_adorn_error = PyAdornErrorPrint1()
    outputs = py_adorn_error.map(["name", "age"], 2)  # type: ignore
    print("Outputs:(装饰器设置不打印错误信息, 并将错误对象注册到列表中)")
    pprint(outputs)
    print("全局错误列表error_status:")
    pprint(error_status)


# 测试指定返回体为数据类
from dataclasses import dataclass, field
@dataclass
class ResponseData:
    code: int = 0
    msg: str = "success"
    name: str = "pyadorn"
    bbox: list[float] = field(default_factory=list)
    error: list = field(default_factory=list)
    error_code: int = 0
    error_msg: str = "success"


error_decorator2 = error_factory(error_debug=False, error_key="error", response_factory=ResponseData)

@error_decorator2
class PyAdornErrorPrint2:

    def map(self, names: list[str], numbers: list[int]):
        return {name: number for name, number in zip(names, numbers)}


def test_error_response_object():
    from pprint import pprint
    py_adorn_error = PyAdornErrorPrint2()
    outputs = py_adorn_error.map(["name", "age"], 2)  # type: ignore
    print("Outputs:")
    pprint(outputs)


error_decorator3 = error_factory(error_debug=False, error_attrs=["error_code", None, "error_msg"], response_factory=ResponseData)
@error_decorator3
class PyAdornErrorPrint3:

    def map(self, names: list[str], numbers: list[int]):
        return {name: number for name, number in zip(names, numbers)}
    
def test_error_response_object2():
    from pprint import pprint
    py_adorn_error = PyAdornErrorPrint3()
    outputs = py_adorn_error.map(["name", "age"], 2)  # type: ignore
    print("Outputs:")
    pprint(outputs)


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



if __name__ == "__main__":
    import asyncio
    # 测试类装饰器打印错误信息, 并输出错误返回信息
    # test_error_logger()
    # test_error_status()
    # test_error_response_object()
    # test_error_response_object2()
    test_async_error_func()  # 异步函数测试
    
