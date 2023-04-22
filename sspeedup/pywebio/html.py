def _colored_text(text: str, color: str) -> str:
    return f'<font color="{color}">{text}</font>'


def green(text: str) -> str:
    return _colored_text(text, "#008700")


def orange(text: str) -> str:
    return _colored_text(text, "#FF8C00")


def red(text: str) -> str:
    return _colored_text(text, "#FF2D10")


def grey(text: str) -> str:
    return _colored_text(text, "#57606A")


def _colored_link(text: str, url: str, color: str, new_window: bool = False) -> str:
    if new_window:
        # 由于新打开的页面拥有对原页面的部分访问权限，这里需要进行处理
        return f'<a href="{url}" style="color: {color}" target="_blank" rel="noopener noreferrer">{text}</a>'

    return f'<a href="{url}" style="color: {color}" target="_self" >{text}</a>'


def link(text: str, url: str, color: str = "#0366d6", new_window: bool = False) -> str:
    return _colored_link(text, url, color, new_window)
