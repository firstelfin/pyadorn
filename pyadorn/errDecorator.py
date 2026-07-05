#!/usr/bin/env python3
# encoding: utf-8
# @author: firstelfin
# @time: 2026/05/23 11:43:15

import inspect
import warnings
import functools
from loguru import logger
from typing import List, Optional, Callable, Union, Literal
from .tools import error_handler


def error_factory(
    error_debug: bool,
    error_response: Optional[list] = None,
    error_key: Optional[str] = None,
    error_attrs: Optional[List[Union[str, None]]] = None,
    traceback_mode: Literal['full', 'last'] = 'last',
    response_factory: Callable = dict,
    *,
    methods: Optional[List[str]] = None,
    filters: Optional[List[str]] = None,
):
    """装饰器工厂

    Args:
        error_debug (bool): 是否是debug模式, 用于调试时打印详细错误信息。
        error_response (list, optional): 错误响应列表. Defaults to None.
        error_key (str, optional): 返回体存放错误的关键字. Defaults to None.
        error_attrs (List[Union[str, None]], optional): 错误对象属性['code','msg','traceback','timestamp']在返回体
            中对应的键. Defaults to None.
        traceback_mode (Literal['full', 'last'], optional): 获取错误堆栈信息的方式, 分别表示全部、最后一个. Defaults to 'last'.
        response_factory (Callable, optional): 返回体工厂函数. Defaults to Dict.
        methods (List[str], optional): 需要封装的类方法. Defaults to None.
        filters (List[str], optional): 不需要封装的类方法. Defaults to None.

    Returns:
        Callable: 装饰器对象

    Examples:
        >>> # 打印错误详情, 并将错误信息使用字典返回, 指定字典的键为pyadorn
        >>> error_decorator0 = error_factory(error_debug=True, error_response=None, error_key="pyadorn", response_factory=dict)
        >>> @error_decorator0
        ... class PyAdornErrorPrint:
        >>>     def map(self, names: list[str], numbers: list[int]):
        >>>         return {name: number for name, number in zip(names, numbers)}
        >>> def test_error_logger():
        >>>     from pprint import pprint
        >>>     py_adorn_error = PyAdornErrorPrint()
        >>>     outputs = py_adorn_error.map(["name", "age"], 2)
        >>>     print("Outputs:(装饰器设置打印错误信息, 并将错误对象注册到字典的pyadorn键中)")
        >>>     pprint(outputs)
        >>> test_error_logger()
        ... Outputs:(装饰器设置打印错误信息, 并将错误对象注册到字典的pyadorn键中)
        ... {'pyadorn': [ErrorInfo(code=599,
        ...                     msg="'int' object is not iterable",
        ...                     traceback='  File '
        ...                                 '"/Users/elfindan/project/errguard/test/test_error.py", '
        ...                                 'line 24, in map\\n'
        ...                                 '    return {name: number for name, number in '
        ...                                 'zip(names, numbers)}',
        ...                     timestamp='2026-07-05 14:35:08')]}
    """

    def decorator(target):
        # 判断是类还是函数, target是装饰对象本身
        if inspect.isclass(target):
            return _decorate_class(
                target, methods, filters, error_debug, error_response, error_key,
                error_attrs, traceback_mode, response_factory)
        else:
            # 普通函数或方法（实际上如果直接装饰方法, target 已经是函数）
            return _wrap_function(
                target, error_debug, error_response, error_key,
                error_attrs, traceback_mode, response_factory
            )

    return decorator


def _decorate_class(
        cls, methods, filters, error_debug, error_response, error_key,
        error_attrs, traceback_mode, response_factory: Callable
    ):
    """装饰类的所有符合条件的方法"""
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        # 如果指定了 methods 列表, 只处理列表中的方法
        if methods is not None and name not in methods:
            continue
        # 如果指定了 filters 列表, 排除列表中的方法
        if filters is not None and name in filters:
            continue
        # 包装该方法
        wrapped = _wrap_function(method, error_debug, error_response, error_key, error_attrs, traceback_mode, response_factory)
        setattr(cls, name, wrapped)
    return cls


def _wrap_function(
        func,
        error_debug=False,
        error_response: Optional[list] = None,
        error_key: Optional[str] = None,
        error_attrs: Optional[List[Union[str, None]]] = None,
        traceback_mode: Literal['full', 'last'] = 'last',
        response_factory: Callable = dict,
    ):
    """包装单个函数, 自动适配同步/异步

    Args:
        func (Callable): 需要包装的函数
        error_debug (bool): 是否是debug模式, 用于调试时打印详细错误信息。
        error_response (list, optional): 错误响应列表. Defaults to None.
        error_key (str, optional): 将错误对象追加到返回体的指定关键字`error_key`中. Defaults to None.
        error_attrs (list, optional): 错误对象属性['code','msg','traceback','timestamp']在返回体
            中对应的键. Defaults to None.
        traceback_mode (Literal['full', 'last'], optional): 获取错误堆栈信息的方式, 分别表示全部、最后一个. Defaults to 'last'.
        response_factory (Callable, optional): 返回体工厂函数. Defaults to Dict.
    """

    if error_response is None:
        assert error_key is not None or error_attrs is not None, \
            "When the error response is None, both the error key and error attrs cannot be None at the same time."
    
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                res = await func(*args, **kwargs)
            except Exception as e:
                if error_debug:
                    logger.exception("捕获异常:")
                res = response_factory()  # type: ignore
                error_handler(e, error_response, res, error_key, error_attrs, traceback_mode)
            return res
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except Exception as e:
                if error_debug:
                    logger.exception("捕获异常:")
                res = response_factory()  # type: ignore
                error_handler(e, error_response, res, error_key, error_attrs, traceback_mode)
            return res
        return sync_wrapper
