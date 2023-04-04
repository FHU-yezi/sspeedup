from functools import wraps
from time import sleep
from typing import Any, Callable, Optional, Sequence, Type, Union

from sspeedup.retry.event import RetryEvent
from sspeedup.retry.policy import PolicyReturn


def retry(
    policy: PolicyReturn,
    exceptions: Union[Type[Exception], Sequence[Type[Exception]]],
    *,
    max_tries: int,
    on_retry: Optional[Callable[[RetryEvent], None]] = None,
) -> Callable:
    def outer(func: Callable) -> Any:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            if max_tries <= 0:
                raise ValueError("max_tries 必须大于 0")
            if max_tries == 1:  # 只尝试一次，相当于不使用重试装饰器
                return func(*args, **kwargs)

            nonlocal exceptions

            if type(exceptions) == type(Exception):
                handle_exceptions = (exceptions,)
            else:
                handle_exceptions = exceptions

            tries = 1
            last_exception = None
            policy_obj = policy()
            while tries <= max_tries - 1:
                try:
                    return func(*args, **kwargs)
                except handle_exceptions as e:
                    last_exception = e
                    wait = next(policy_obj)
                    if on_retry:
                        on_retry(
                            RetryEvent(func=func, exception=e, tries=tries, wait=wait)
                        )
                    sleep(wait)
                    tries += 1

            if last_exception:
                raise last_exception

            return None

        return inner

    return outer
