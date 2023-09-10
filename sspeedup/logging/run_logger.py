from asyncio import run as asyncio_run
from atexit import register as atexit_register
from datetime import datetime
from enum import Enum
from os import path as os_path
from queue import Queue
from sys import _getframe
from sys import argv as sys_argv
from threading import Thread
from threading import current_thread as get_current_thread
from time import sleep
from traceback import format_exception
from typing import Any, Dict, List, Optional, Union

from msgspec import Struct
from msgspec import to_builtins as convert_obj_to_dict

from sspeedup.colorful_print import BackgroundColor, ForegroundColor, with_color

_RECORD_STRUCT_CONFIG: Dict[str, Any] = {
    "forbid_unknown_fields": True,
    "frozen": True,
    "kw_only": True,
    "gc": False,
}


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


_LOGLEVEL_TO_NUMBER: Dict[LogLevel, int] = {
    LogLevel.DEBUG: 1,
    LogLevel.INFO: 2,
    LogLevel.WARNING: 3,
    LogLevel.ERROR: 4,
    LogLevel.CRITICAL: 5,
}


def _is_greater_than(obj: LogLevel, target: LogLevel) -> bool:
    return _LOGLEVEL_TO_NUMBER[obj] >= _LOGLEVEL_TO_NUMBER[target]


_LOG_LEVEL_TO_COLOR: Dict[LogLevel, Union[str, ForegroundColor, BackgroundColor]] = {
    LogLevel.DEBUG: "",
    LogLevel.INFO: ForegroundColor.CYAN.value,
    LogLevel.WARNING: ForegroundColor.YELLOW.value,
    LogLevel.ERROR: ForegroundColor.RED.value,
    LogLevel.CRITICAL: BackgroundColor.RED.value,
}

_ExtraType = Union[
    str,
    int,
    float,
    List[Union[str, int, float]],
    Dict[str, Union[str, int, float]],
    None,
]


class _RecordStackInfo(Struct, **_RECORD_STRUCT_CONFIG):
    thread_name: str
    file_name: str
    line: int
    caller_name: str


class _RecordExceptionInfo(Struct, **_RECORD_STRUCT_CONFIG):
    name: str
    desc: Optional[str]
    traceback: str


class _LogRecord(Struct, **_RECORD_STRUCT_CONFIG):
    time: datetime
    level: LogLevel
    msg: str
    stack: _RecordStackInfo
    exception: Optional[_RecordExceptionInfo] = None
    extra: Optional[Dict[str, _ExtraType]] = None


def _get_base_dir() -> str:
    """获取应用根目录"""
    return os_path.dirname(os_path.realpath(sys_argv[0])) + "/"


_BASE_DIR = _get_base_dir()


def _get_stack_info() -> _RecordStackInfo:
    frame_obj = _getframe(3)  # 获取调用者堆栈信息

    return _RecordStackInfo(
        thread_name=get_current_thread().name,
        file_name=frame_obj.f_code.co_filename.replace(_BASE_DIR, ""),
        line=frame_obj.f_lineno,
        caller_name=frame_obj.f_code.co_name,
    )


def _get_exception_info(e: Exception) -> _RecordExceptionInfo:
    return _RecordExceptionInfo(
        name=type(e).__name__,
        desc=e.args[0] if len(e.args) != 0 else None,
        traceback="".join(format_exception(e)).replace(_BASE_DIR, ""),
    )


class RunLogger:
    def __init__(
        self,
        *,
        save_level: LogLevel = LogLevel.DEBUG,
        print_level: LogLevel = LogLevel.DEBUG,
        mongo_collection: Any = None,
        auto_save_interval: int = 120,
        save_at_exit: bool = True,
    ) -> None:
        self._save_level = save_level
        self._print_level = print_level

        self._mongo_collection = mongo_collection
        self._data_save_enabled = mongo_collection is not None

        self._queue: Queue[_LogRecord] = Queue()

        self._auto_save_interval = auto_save_interval
        self._auto_save_enabled = auto_save_interval > 0
        if self._auto_save_enabled and self._data_save_enabled:
            self._auto_save_thread = Thread(
                target=self._auto_save_func, name="run-logger-auto-save", daemon=True
            )

        if (
            save_at_exit
            and self._data_save_enabled
            # 异步模式下无法在退出时正常保存数据
            and self._mongo_collection.__class__.__name__ == "Collection"
        ):
            atexit_register(self._at_exit_handler)

    def _print_log(self, obj: _LogRecord) -> None:
        log_lines: List[str] = []

        # 时间
        log_lines.append(
            with_color(
                f"[{obj.time.strftime(r'%Y-%m-%d %H:%M:%S')}]",
                ForegroundColor.MAGENTA,
            )
        )

        # 文件名、调用者名、行号
        log_lines.append(
            with_color(
                f"[{obj.stack.file_name}:{obj.stack.caller_name}:{obj.stack.line}]",
                ForegroundColor.MAGENTA,
            )
        )

        # 线程
        if obj.stack.thread_name != "MainThread":
            log_lines.append(
                with_color(
                    f"[{obj.stack.thread_name}]",
                    ForegroundColor.MAGENTA,
                )
            )

        # 消息
        log_lines.append(with_color(obj.msg, _LOG_LEVEL_TO_COLOR[obj.level]))

        # 错误信息
        if obj.exception:
            log_lines.append(
                "\n    "
                + with_color(f"[{obj.exception.name}]", BackgroundColor.RED)
                + (
                    with_color(f" {obj.exception.desc}", ForegroundColor.RED)
                    if obj.exception.desc
                    else ""
                )
            )
            log_lines.append(
                "\n        " + "\n        ".join(obj.exception.traceback.split("\n"))
            )

        # 额外信息
        if obj.extra:
            log_lines.append(
                "\n    " + ", ".join(f"{k}={v}" for k, v in obj.extra.items())
            )

        print(" ".join(log_lines))

    def _log(
        self,
        *,
        level: LogLevel,
        msg: str,
        exception: Optional[Exception] = None,
        **extra: _ExtraType,
    ) -> None:
        if _is_greater_than(level, self._print_level) or _is_greater_than(
            level, self._save_level
        ):
            log_record_obj = _LogRecord(
                time=datetime.now(),
                level=level,
                msg=msg,
                stack=_get_stack_info(),
                exception=_get_exception_info(exception) if exception else None,
                extra=extra if len(extra.keys()) != 0 else None,
            )

        if _is_greater_than(level, self._print_level):
            self._print_log(log_record_obj)  # type: ignore

        if _is_greater_than(level, self._save_level):
            self._queue.put(log_record_obj)  # type: ignore

    def debug(self, msg: str, **extra: _ExtraType) -> None:
        self._log(level=LogLevel.DEBUG, msg=msg, exception=None, **extra)

    def info(self, msg: str, **extra: _ExtraType) -> None:
        self._log(level=LogLevel.INFO, msg=msg, exception=None, **extra)

    def warning(
        self,
        msg: str,
        *,
        exception: Optional[Exception] = None,
        **extra: _ExtraType,
    ) -> None:
        self._log(level=LogLevel.WARNING, msg=msg, exception=exception, **extra)

    def error(
        self,
        msg: str,
        *,
        exception: Optional[Exception] = None,
        **extra: _ExtraType,
    ) -> None:
        self._log(level=LogLevel.ERROR, msg=msg, exception=exception, **extra)

    def critical(
        self,
        msg: str,
        *,
        exception: Optional[Exception] = None,
        **extra: _ExtraType,
    ) -> None:
        self._log(level=LogLevel.CRITICAL, msg=msg, exception=exception, **extra)

    def _get_all_from_queue(self) -> List[_LogRecord]:
        result: List[_LogRecord] = []
        while not self._queue.empty():
            result.append(self._queue.get())

        return result

    def _convert_log_record_obj_to_dict(self, obj: _LogRecord) -> Dict[str, Any]:
        return convert_obj_to_dict(obj, builtin_types=[datetime])

    def save_all(self) -> None:
        if not self._data_save_enabled:
            return

        data_to_save: List[Dict[str, Any]] = [
            self._convert_log_record_obj_to_dict(x) for x in self._get_all_from_queue()
        ]
        if not data_to_save:
            return

        if self._mongo_collection.__class__.__name__ == "Collection":  # type: ignore
            # PyMongo
            self._mongo_collection.insert_many(data_to_save)  # type: ignore
        elif self._mongo_collection.__class__.__name__ == "AsyncIOMotorCollection":  # type: ignore
            # Motor
            async def _save() -> None:
                await self._mongo_collection.insert_many(data_to_save)

            asyncio_run(_save())

    def _auto_save_func(self) -> None:
        while True:
            self.save_all()
            sleep(self._auto_save_interval)

    def _at_exit_handler(self) -> None:
        self.save_all()
