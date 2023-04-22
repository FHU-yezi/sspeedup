from time import sleep

from pywebio.session import eval_js, run_js


def get_base_url() -> str:
    return eval_js("window.location.origin + window.location.pathname")  # type: ignore


def get_full_url() -> str:
    return eval_js("window.location.href")  # type: ignore


def jump_to(url: str, new_window: bool = False, delay: int = 0) -> None:
    if delay:
        sleep(delay)
    run_js(f'window.open("{url}", "{"_blank" if new_window else "_self"}")')


def reload(delay: int = 0) -> None:
    if delay:
        sleep(delay)
    run_js("location.reload()")
