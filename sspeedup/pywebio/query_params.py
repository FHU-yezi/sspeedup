from typing import Dict

from pywebio.session import eval_js


def get_query_params() -> Dict[str, str]:
    params_str: str = eval_js("window.location.search.substr(1)")  # type: ignore
    return dict([x.split("=") for x in params_str.split("&")])
