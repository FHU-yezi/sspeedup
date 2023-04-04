from enum import Enum
from sys import stdout

COLOR_RESET = "\033[0m"


class Color(Enum):
    pass


class ForegroundColor(Color):
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class BackgroundColor(Color):
    BLACK = "\033[0;37;40m"
    RED = "\033[0;37;41m"
    GREEN = "\033[0;37;42m"
    YELLOW = "\033[0;37;43m"
    BLUE = "\033[0;37;44m"
    MAGENTA = "\033[0;37;45m"
    CYAN = "\033[0;37;46m"
    WHITE = "\033[0;37;47m"


def colorful_print(
    *values: object, color: Color, sep: str = "", end: str = "\n"
) -> None:
    stdout.write(color.value)
    print(*values, sep=sep, end="")
    stdout.write(COLOR_RESET)
    stdout.write(end)


def print_black(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=ForegroundColor.BLACK, sep=sep, end=end)


def print_red(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=ForegroundColor.RED, sep=sep, end=end)


def print_green(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=ForegroundColor.GREEN, sep=sep, end=end)


def print_yellow(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=ForegroundColor.YELLOW, sep=sep, end=end)


def print_blue(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=ForegroundColor.BLUE, sep=sep, end=end)


def print_magenta(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=ForegroundColor.MAGENTA, sep=sep, end=end)


def print_cyan(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=ForegroundColor.CYAN, sep=sep, end=end)


def print_white(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=ForegroundColor.WHITE, sep=sep, end=end)


def print_bg_black(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=BackgroundColor.BLACK, sep=sep, end=end)


def print_bg_red(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=BackgroundColor.RED, sep=sep, end=end)


def print_bg_green(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=BackgroundColor.GREEN, sep=sep, end=end)


def print_bg_yellow(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=BackgroundColor.YELLOW, sep=sep, end=end)


def print_bg_blue(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=BackgroundColor.BLUE, sep=sep, end=end)


def print_bg_magenta(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=BackgroundColor.MAGENTA, sep=sep, end=end)


def print_bg_cyan(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=BackgroundColor.CYAN, sep=sep, end=end)


def print_bg_white(*values: object, sep: str = "", end: str = "\n") -> None:
    colorful_print(*values, color=BackgroundColor.WHITE, sep=sep, end=end)
