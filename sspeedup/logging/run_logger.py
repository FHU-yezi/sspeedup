from atexit import register as atexit_register
from collections import deque
from datetime import datetime
from enum import Enum
from os import path as os_path
from sys import _getframe
from sys import argv as sys_argv
from threading import Thread
from threading import current_thread as threading_get_current
from time import sleep
from traceback import format_exception
from types import FrameType
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    TypedDict,
    Union,
)

from sspeedup.colorful_print import COLOR_RESET, BackgroundColor, ForegroundColor

if TYPE_CHECKING:
    from pymongo.collection import Collection


ExtraType = Union[
    str,
    int,
    float,
    List[Union[str, int, float]],
    Dict[str, Union[str, int, float]],
    None,
]


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


_LOG_LEVEL_TO_NUM: Dict[LogLevel, int] = {
    LogLevel.DEBUG: 0,
    LogLevel.INFO: 1,
    LogLevel.WARNING: 2,
    LogLevel.ERROR: 3,
    LogLevel.CRITICAL: 4,
}

_LOG_LEVEL_TO_COLOR: Dict[str, str] = {
    LogLevel.DEBUG.name: "",
    LogLevel.INFO.name: ForegroundColor.CYAN.value,
    LogLevel.WARNING.name: ForegroundColor.YELLOW.value,
    LogLevel.ERROR.name: ForegroundColor.RED.value,
    LogLevel.CRITICAL.name: BackgroundColor.RED.value,
}


class _StackInfo(TypedDict):
    file_name: str
    caller_name: str
    line_number: int
    thread_name: str


class _ExceptionInfo(TypedDict):
    name: str
    description: str
    traceback: str


class _LogRecord(TypedDict):
    time: datetime
    level: str
    content: str
    stack_info: Optional[_StackInfo]
    exception_info: Optional[_ExceptionInfo]
    extra: Dict[str, ExtraType]  # type: ignore


def _greater_or_equal_than(log_level: LogLevel) -> Sequence[LogLevel]:
    return tuple(
        k for k, v in _LOG_LEVEL_TO_NUM.items() if v >= _LOG_LEVEL_TO_NUM[log_level]
    )


def _get_base_dir() -> str:
    """获取应用根目录"""
    return os_path.dirname(os_path.realpath(sys_argv[0])) + "/"


_BASE_DIR = _get_base_dir()


def _get_caller_frame_obj() -> FrameType:
    return _getframe(4)


def _get_caller_filename(frame_obj: FrameType) -> str:
    """获取调用者文件名，使用相对路径"""
    return frame_obj.f_code.co_filename.replace(_BASE_DIR, "")


def _get_caller_line_number(frame_obj: FrameType) -> int:
    """获取调用者行号"""
    return frame_obj.f_lineno


def _get_caller_name(frame_obj: FrameType) -> str:
    """获取调用者名称"""
    return frame_obj.f_code.co_name


def _get_exception_name(exception: Exception) -> str:
    """获取错误名称"""
    return type(exception).__name__


def _get_exception_description(exception: Exception) -> str:
    """获取错误描述"""
    return exception.args[0]


def _get_exception_traceback(exception: Exception) -> str:
    """获取错误堆栈，自动替换相对路径"""
    return "".join(format_exception(exception)).replace(_BASE_DIR, "")


def _get_current_thread_name() -> str:
    """获取当前线程名"""
    return threading_get_current().name


class RunLogger:
    def __init__(
        self,
        mongo_collection: Optional["Collection"] = None,
        *,
        auto_save_interval: int = 60,
        auto_save_queue_max_size: Optional[int] = None,
        stack_info_enabled: bool = True,
        color_enabled: bool = True,
        traceback_print_enabled: bool = True,
        thread_name_print_enabled: Union[bool, Literal["except_main"]] = "except_main",
        save_when_exit: bool = True,
        print_level: LogLevel = LogLevel.DEBUG,
        save_level: LogLevel = LogLevel.INFO,
    ) -> None:
        """运行日志记录器

        Args:
            mongo_collection (Optional[&quot;Collection&quot;], optional): 保存日志信息的 MongoDB 集合，为空则禁用数据库存储. Defaults to None.
            auto_save_interval (int, optional): 自动保存间隔，如禁用数据库存储将忽略此值. Defaults to 60.
            auto_save_queue_max_size (int, optional): 自动保存队列长度，超出将删除最旧的未记录数据，None 为不限制. Defaults to None.
            stack_info_enabled (bool, optional): 是否记录堆栈信息. Defaults to True.
            color_enabled (bool, optional): 是否启用彩色输出. Defaults to True.
            traceback_print_enabled (bool, optional): 是否输出错误堆栈. Defaults to True.
            thread_name_print_enabled (Union[bool, Literal["except_main"]], optional): 是否输出线程名. Defaults to "except_main".
            save_when_exit (bool, optional): 注册退出处理程序，在退出时将日志信息保存到数据库，如禁用数据库存储将忽略此值. Defaults to True.
            print_level (LogLevel, optional): 输出日志等级. Defaults to LogLevel.DEBUG.
            save_level (LogLevel, optional): 记录日志等级. Defaults to LogLevel.INFO.
        """
        self.mongo_collection = mongo_collection
        self.db_save_enabled: bool = mongo_collection is not None

        self.auto_save_interval = auto_save_interval
        # 如不开启数据库存储，则不启用自动保存
        self.auto_save_enabled: bool = (
            auto_save_interval > 0 if self.db_save_enabled else False
        )

        self.save_level = save_level
        self.print_level = print_level

        self.stack_info_enabled = stack_info_enabled
        self.color_enabled = color_enabled
        self.traceback_print_enabled = traceback_print_enabled
        self.thread_name_print_enabled = thread_name_print_enabled

        if self.auto_save_enabled:
            self.save_queue: deque[_LogRecord] = deque(maxlen=auto_save_queue_max_size)
            self.auto_save_thread = Thread(
                target=self._auto_save,
                name="run-logger-auto-save",
                daemon=True,
            )
            self.auto_save_thread.start()

        if save_when_exit and self.db_save_enabled:
            atexit_register(self.save)

    def _auto_save(self) -> None:
        """自动保存线程"""
        while True:
            sleep(self.auto_save_interval)
            self._save_many(self._get_all())

    def save(self) -> None:
        """立刻将数据保存到数据库，如果没有待保存的数据，此函数直接返回

        Raises:
            ValueError: 数据库保存未开启
        """
        if not self.db_save_enabled:
            raise ValueError("数据库保存未开启")

        if not len(self.save_queue):
            return  # 没有待保存的数据，直接返回

        self._save_many(self._get_all())

    def _save_one(self, log: _LogRecord) -> None:
        """保存一条数据到数据库"""
        assert self.mongo_collection is not None
        self.mongo_collection.insert_one(log)

    def _save_many(self, logs: Sequence[_LogRecord]) -> None:
        """保存一批数据到数据库"""
        if not logs:
            return  # 序列为空，直接返回

        assert self.mongo_collection is not None
        self.mongo_collection.insert_many(logs)

    def _get_one(self) -> Optional[_LogRecord]:
        """获取一条待保存的数据，如果没有，返回 None"""
        try:
            return self.save_queue.popleft()
        except IndexError:
            return None

    def _get_all(self) -> List[_LogRecord]:
        """获取所有待保存的数据，如果没有，返回空列表"""
        result: List[_LogRecord] = []
        try:
            while True:
                result.append(self.save_queue.popleft())
        except IndexError:
            return result

    def _need_print(self, level: LogLevel) -> bool:
        return level in _greater_or_equal_than(self.print_level)

    def _need_save(self, level: LogLevel) -> bool:
        return self.db_save_enabled and level in _greater_or_equal_than(self.save_level)

    def _build_log_obj(
        self,
        level: LogLevel,
        content: str,
        exception: Optional[Exception],
        **extra: ExtraType,
    ) -> _LogRecord:
        result: _LogRecord = {
            "time": datetime.now(),
            "level": level.value,
            "content": content,
            "stack_info": None,
            "exception_info": None,
            "extra": extra,
        }
        if self.stack_info_enabled:
            frame_obj = _get_caller_frame_obj()
            result["stack_info"] = {
                "file_name": _get_caller_filename(frame_obj),
                "caller_name": _get_caller_name(frame_obj),
                "line_number": _get_caller_line_number(frame_obj),
                "thread_name": _get_current_thread_name(),
            }
        if exception:
            result["exception_info"] = {
                "name": _get_exception_name(exception),
                "description": _get_exception_description(exception),
                "traceback": _get_exception_traceback(exception),
            }

        return result

    def _print_log_obj(self, log: _LogRecord) -> None:
        if self.color_enabled:
            time_str = f"{ForegroundColor.CYAN.value}[{datetime.now().strftime(r'%Y-%m-%d %H:%M:%S')}]{COLOR_RESET}"
            stack_str = (
                f"{ForegroundColor.MAGENTA.value}[{log['stack_info']['file_name']}:{log['stack_info']['line_number']} ({log['stack_info']['caller_name']})]{COLOR_RESET}"  # type: ignore
                if self.stack_info_enabled
                else None
            )
            if (
                self.thread_name_print_enabled == "except_main"
                and log["stack_info"]["thread_name"] != "MainThread"  # type: ignore
            ) or self.thread_name_print_enabled is True:
                thread_str = f"{ForegroundColor.MAGENTA.value}[{log['stack_info']['thread_name']}]{COLOR_RESET}"  # type: ignore
            else:
                thread_str = ""
            level_str = f"{_LOG_LEVEL_TO_COLOR[log['level']]}[{log['level']}]"
            content_str = f"{log['content']}{COLOR_RESET}"
        else:
            time_str = f"[{datetime.now().strftime(r'%Y-%m-%d %H:%M:%S')}]"
            stack_str = (
                f"[{log['stack_info']['file_name']}:{log['stack_info']['line_number']}]"  # type: ignore
                if self.stack_info_enabled
                else None
            )
            if (
                self.thread_name_print_enabled == "except_main"
                and log["stack_info"]["thread_name"] != "MainThread"  # type: ignore
            ) or self.thread_name_print_enabled is True:
                thread_str = f"[{log['stack_info']['thread_name']}]"  # type: ignore
            else:
                thread_str = ""
            level_str = f"[{log['level']}]"
            content_str = log["content"]

        print(
            *filter(None, [time_str, stack_str, thread_str, level_str, content_str]),
            sep=" ",
        )

        if extra := log.get("extra"):
            print(
                "    Extra：", "，".join([f"{k}={v}" for k, v in extra.items()]), sep=""
            )

        if exception_info := log.get("exception_info"):
            print(
                f"    Exception：{exception_info['name']}: {exception_info['description']}"
            )
            if self.traceback_print_enabled:
                print(
                    "        " + exception_info["traceback"].replace("\n", "\n        ")
                )

    def _save_log_obj(self, log: _LogRecord) -> None:
        self.save_queue.append(log)

    def _log(
        self,
        level: LogLevel,
        content: str,
        exception: Optional[Exception] = None,
        **extra: ExtraType,
    ) -> None:
        need_print = self._need_print(level)
        need_save = self._need_save(level)

        if not need_print and not need_save:
            return  # 无需输出也无需记录，直接返回

        log_obj = self._build_log_obj(level, content, exception, **extra)

        if need_print:
            self._print_log_obj(log_obj)
        if need_save:
            self._save_log_obj(log_obj)

    def debug(self, content: str, **extra: ExtraType) -> None:
        self._log(LogLevel.DEBUG, content, **extra)

    def info(self, content: str, **extra: ExtraType) -> None:
        self._log(LogLevel.INFO, content, **extra)

    def warning(
        self, content: str, exception: Optional[Exception] = None, **extra: ExtraType
    ) -> None:
        self._log(LogLevel.WARNING, content, exception, **extra)

    def error(
        self, content: str, exception: Optional[Exception] = None, **extra: ExtraType
    ) -> None:
        self._log(LogLevel.ERROR, content, exception, **extra)

    def critical(
        self, content: str, exception: Optional[Exception] = None, **extra: ExtraType
    ) -> None:
        self._log(LogLevel.CRITICAL, content, exception, **extra)
