from dataclasses import dataclass
from typing import Callable


@dataclass
class RetryEvent:
    func: Callable
    exception: Exception
    tries: int
    wait: float
