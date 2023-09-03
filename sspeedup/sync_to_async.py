from asyncio import Future, get_running_loop
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Callable, TypeVar

_T = TypeVar("_T")

POOL = ThreadPoolExecutor(max_workers=8)


def sync_to_async(func: Callable[..., _T], *args: Any, **kwargs: Any) -> Future[_T]:
    return get_running_loop().run_in_executor(POOL, partial(func, *args, **kwargs))
