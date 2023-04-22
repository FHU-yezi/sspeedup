from typing import Dict, Union

from pywebio.session import eval_js, run_js


def set_cookies(data: Dict[str, Union[str, int, float]]) -> None:
    cookies_str = ";".join([f"{key}={value}" for key, value in data.items()])
    run_js(f"document.cookie = '{cookies_str}'")


def get_cookies() -> Dict[str, str]:
    cookies_str: str = eval_js("document.cookie")  # type: ignore
    if not cookies_str:  # Cookie 字符串为空
        return {}

    return dict([x.split("=") for x in cookies_str.split("; ")])


def remove_cookies() -> None:
    run_js("document.cookie = ''")
