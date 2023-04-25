from typing import Dict, Optional, Union

from pywebio.session import eval_js, run_js


def set_cookie(
    key: str,
    value: Union[str, int, float],
    max_age: Optional[int] = None,
    secure: bool = False,
) -> None:
    code = f'document.cookie = "{key}={value}'
    if max_age:
        code += f";max-age={max_age}"
    if secure:
        code += ";secure"
    code += '"'
    run_js(code)


def get_cookies() -> Dict[str, str]:
    cookies_str: str = eval_js("document.cookie")  # type: ignore
    if not cookies_str:  # Cookie 字符串为空
        return {}

    return dict([x.split("=") for x in cookies_str.split("; ")])


def remove_cookie(key: str) -> None:
    run_js(f'document.cookie = "{key}=;expires=Thu, 01 Jan 1970 00:00:00 GMT"')
