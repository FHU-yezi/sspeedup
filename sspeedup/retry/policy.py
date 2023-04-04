from typing import Callable, Generator, Optional

PolicyReturn = Callable[[], Generator[float, None, None]]
PolicyInnerReturn = Generator[float, None, None]


def constant_backoff_policy(value: float) -> PolicyReturn:
    def inner() -> PolicyInnerReturn:
        while True:
            yield value

    return inner


def exponential_backoff_policy(
    base: float = 2, max_value: Optional[float] = None
) -> PolicyReturn:
    def inner() -> PolicyInnerReturn:
        factor = 1
        while True:
            yield min(base**factor, max_value if max_value else float("inf"))
            factor += 1

    return inner
