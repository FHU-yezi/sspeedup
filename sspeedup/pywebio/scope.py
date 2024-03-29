from functools import partial
from typing import Callable

from pywebio.output import use_scope

use_clear_scope: Callable = partial(
    use_scope,
    clear=True,
)
