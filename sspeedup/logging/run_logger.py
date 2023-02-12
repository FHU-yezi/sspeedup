from datetime import datetime
from enum import Enum
from inspect import currentframe
from os import path as os_path
from queue import Empty, Queue
from sys import argv as sys_argv
from threading import Thread
from time import sleep
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Sequence,
    TypedDict,
    TypeVar,
)

if TYPE_CHECKING:
    from pymongo.collection import Collection


ExtraType = TypeVar("ExtraType", str, int, float, None)


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


_LOG_LEVEL_TO_NUM = {
    LogLevel.DEBUG: 0,
    LogLevel.INFO: 1,
    LogLevel.WARNING: 2,
    LogLevel.ERROR: 3,
    LogLevel.CRITICAL: 4,
}


class StackInfo(TypedDict):
    file_name: str
    line_number: int


class ExceptionInfo(TypedDict):
    name: str
    description: str


class Log(TypedDict, total=False):
    time: datetime
    level: str
    content: str
    stack_info: StackInfo
    exception_info: ExceptionInfo
    extra: Dict[str, ExtraType]  # type: ignore


def _greater_or_equal_than(log_level: LogLevel) -> Sequence[LogLevel]:
    return tuple(
        k for k, v in _LOG_LEVEL_TO_NUM.items() if v >= _LOG_LEVEL_TO_NUM[log_level]
    )


def _get_base_dir() -> str:
    """获取应用根目录"""
    return os_path.dirname(os_path.realpath(sys_argv[0])) + "/"


BASE_DIR = _get_base_dir()


def get_caller_filename() -> str:
    """获取调用者文件名，使用相对路径"""
    return currentframe().f_back.f_back.f_back.f_back.f_code.co_filename.replace(BASE_DIR, "")  # type: ignore [union-attr]


def get_caller_line_number() -> int:
    """获取调用者行号"""
    return currentframe().f_back.f_back.f_back.f_back.f_lineno  # type: ignore [union-attr]


def get_exception_name(exception: Exception) -> str:
    return type(exception).__name__


def get_exception_description(exception: Exception) -> str:
    return exception.args[0]


class RunLogger:
    def __init__(
        self,
        mongo_collection: Optional["Collection"] = None,
        auto_save_interval: int = 60,
        auto_save_queue_max_size: int = 0,
        stack_info_enabled: bool = True,
        print_level: LogLevel = LogLevel.DEBUG,
        save_level: LogLevel = LogLevel.INFO,
    ) -> None:
        self.mongo_collection = mongo_collection
        self.db_save_enabled: bool = mongo_collection is not None

        self.auto_save_interval = auto_save_interval
        # 如不开启数据库存储，则不启用自动保存
        self.auto_save_enabled: bool = auto_save_interval > 0 if self.db_save_enabled else False

        self.save_level = save_level
        self.print_level = print_level

        self.stack_info_enabled = stack_info_enabled

        if self.auto_save_enabled:
            self.save_queue: Queue[Log] = Queue(auto_save_queue_max_size)
            self.auto_save_thread = Thread(
                target=self._auto_save,
                name="run-logger-auto-save",
                daemon=True,
            )
            self.auto_save_thread.start()

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

        if self.save_queue.empty():
            return  # 没有待保存的数据，直接返回

        self._save_many(self._get_all())

    def _save_one(self, log: Log) -> None:
        """保存一条数据到数据库"""
        assert self.mongo_collection
        self.mongo_collection.insert_one(log)

    def _save_many(self, logs: Sequence[Log]) -> None:
        """保存一批数据到数据库"""
        if not logs:
            return  # 序列为空，直接返回

        assert self.mongo_collection
        self.mongo_collection.insert_many(logs)

    def _get_one(self) -> Optional[Log]:
        """获取一条待保存的数据，如果没有，返回 None"""
        try:
            return self.save_queue.get_nowait()
        except Empty:
            return None

    def _get_all(self) -> List[Log]:
        """获取所有待保存的数据，如果没有，返回空列表"""
        result: List[Log] = []
        while self.save_queue.not_empty:
            result.append(self.save_queue.get())
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
    ) -> Log:
        result: Log = {
            "time": datetime.now(),
            "level": level.value,
            "content": content,
        }
        if self.stack_info_enabled:
            result["stack_info"] = {
                "file_name": get_caller_filename(),
                "line_number": get_caller_line_number(),
            }
        if exception:
            result["exception_info"] = {
                "name": get_exception_name(exception),
                "description": get_exception_description(exception),
            }
        if extra:
            result["extra"] = extra

        return result

    def _print_log_obj(self, log: Log) -> None:
        if self.stack_info_enabled:
            print(
                f"[{datetime.now().strftime(r'%Y-%m-%d %H:%M:%S')}]",
                f"[{log['stack_info']['file_name']}:{log['stack_info']['line_number']}]",  # type: ignore
                f"[{log['level']}]",  # type: ignore
                log["content"],  # type: ignore
                sep=" ",
            )
        else:
            print(
                f"[{datetime.now().strftime(r'%Y-%m-%d %H:%M:%S')}]",
                f"[{log['level']}]",  # type: ignore
                log["content"],  # type: ignore
                sep=" ",
            )

        if extra := log.get("extra"):
            print("\tExtra：", "，".join([f"{k}={v}" for k, v in extra.items()]), sep="")

        if exception_info := log.get("exception_info"):
            print(
                f"\tException：{exception_info['name']}: {exception_info['description']}"
            )

    def _save_log_obj(self, log: Log) -> None:
        self.save_queue.put(log)

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
