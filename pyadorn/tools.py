#!/usr/bin/env python3
# encoding: utf-8
# @author: firstelfin
# @time: 2026/05/31 11:37:15

import functools
import inspect
import traceback
from datetime import datetime
from traceback import FrameSummary
from types import TracebackType
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Union, Literal


def is_async_function(func):
    return func.__code__.co_flags & 0x80  # 检查CO_ASYNC标志


def set_key_or_attr(obj, key, value):
    """安全地给字典或对象赋值"""
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)


def traceback_info(e: Union[Exception, TracebackType]):
    """根据TracebackType或Exception对象获取异常信息

    traceback.print_exception()会直接打印完整异常信息到标准输出

    Args:
        e (Union[Exception, TracebackType]): 报错信息对象或者主动通过sys获取的调用栈对象

    Returns:
        list[FrameSummary]: 异常信息列表,每个元素是一个FrameSummary对象,包含文件名、行号、函数名和代码片段
    
    Example:
        >>> import traceback
        >>> trace_info = traceback_info(e)
        ... [<FrameSummary file /Users/elfindan/project/errguard/test.py, line 21 in <module>>, <FrameSummary file /Users/elfindan/project/errguard/test.py, line 16 in __call__>]
        >>> traceback.print_exception(type(e), e, e.__traceback__, file=sys.stdout)
        ... Traceback (most recent call last):
        ... File "/Users/elfindan/project/errguard/test.py", line 23, in <module>
        ...     elfin(25)
        ... File "/Users/elfindan/project/errguard/test.py", line 18, in __call__
        ...     raise KeyError(f"Num: {num} should be less than 10.")
        ... KeyError: 'Num: 25 should be less than 10.'
    """
    tb_obj = e.__traceback__ if isinstance(e, Exception) else e
    results: list[FrameSummary] = traceback.extract_tb(tb_obj)
    return results


def format_frame_summary(fs) -> str:
    s = f'  File "{fs.filename}", line {fs.lineno}, in {fs.name}'
    if fs.line:
        s += f'\n    {fs.line.strip()}'
    return s


def get_last_traceback_info(e: Union[Exception, TracebackType]) -> str:
    """获取最后一个异常信息的字符串表示"""
    tb_info = traceback_info(e)
    last_tb = tb_info[-1]
    res_str = format_frame_summary(last_tb)
    return res_str


def get_full_traceback_info(e: Union[Exception, TracebackType]) -> str:
    """获取完整的异常信息的字符串表示"""
    tb_info = traceback_info(e)
    res_str = '\n'.join([format_frame_summary(fs) for fs in tb_info])
    return res_str


@dataclass
class ErrorInfo:

    code: int            # 错误编码
    msg: str             # 错误信息
    traceback: str       # 调用栈（字符串格式）
    timestamp: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def error_handler(
        e: Exception,
        error_response: Optional[list] = None,
        res_obj= None,
        error_key: Optional[str] = None,
        res_attrs: Optional[list[Union[str, None]]] = None,
        traceback_mode: Literal['full', 'last'] = 'last',
    ):
    """错误处理函数

    Args:
        e (BaseException): 错误对象
        error_response (list, optional): 错误响应列表, 指定列表时, 会向列表追加错误对象, 默认为None.
        res_obj (object, optional): 返回结构体实例. Defaults to None.
        error_key (str, optional): 将错误对象追加到`res_obj`的指定关键字`error_key`中. Defaults to None.
        res_attrs (list[str], optional): 错误对象属性['code', 'msg', 'traceback', 'timestamp']在`res_obj`
            中对应的键. Defaults to None.
        traceback_mode (Literal['full', 'last'], optional): 异常信息的获取方式, 'full'表示获取完整的调用栈,
            'last'表示获取最后一个异常信息. Defaults to 'last'.
    """

    traceback_msg = get_last_traceback_info(e) if traceback_mode == 'last' else get_full_traceback_info(e)
    error_item = ErrorInfo(
        code=int(getattr(e, 'code', 599)),
        msg=str(e),
        traceback=traceback_msg,
    )
    error_standard_attrs = ['code', 'msg', 'traceback', 'timestamp']
    if error_response is not None:
        # 将错误对象传入指定对象error_response中
        error_response.append(error_item)
    elif res_obj is not None and error_key is not None:
        # 将错误分配给指定的对象关键字error_key中
        res_obj_err_list = getattr(res_obj, error_key, [])  # type: ignore
        res_obj_err_list.append(error_item)
        set_key_or_attr(res_obj, error_key, res_obj_err_list)  # type: ignore
    elif res_obj is not None and res_attrs is not None:
        # 将错误属性直接注入到返回体中
        for i, attr in enumerate(res_attrs):
            if attr is None:
                continue
            set_key_or_attr(res_obj, attr, getattr(error_item, error_standard_attrs[i]))  # type: ignore
    else:
        raise ValueError("pyadorn: Expected to provide the following three parameter calling methods:\n" +
                         "    1. The error response is not None and requires a list;\n" +
                         "    2. res_obj is a dictionary or custom data class, and err_key specifies the key for the error record;\n" +
                         "    3. res_obj is a dictionary or custom data class, where res_ottrs specifies incorrect 'code', 'msg'," +
                         "    'traceback', 'timestamp' attribute key names in sequence. The attributes can be incompletely specified," +
                         "    and None defaults to skipping the setting.")
