from functools import lru_cache, wraps
from time import time
from typing import Any, Callable


def timeout_cache(seconds: int) -> Callable:
    def outer(func: Callable) -> Any:
        func = lru_cache()(func)
        func.lifetime = seconds  # type: ignore
        func.expire_time = time() + func.lifetime  # type: ignore

        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            if time() >= func.expire_time:  # type: ignore
                func.cache_clear()
                func.expire_time = time() + func.lifetime  # type: ignore

            return func(*args, **kwargs)

        return inner

    return outer
