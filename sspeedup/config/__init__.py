from signal import SIG_DFL, SIGHUP, signal
from typing import Callable, Optional, Type, TypeVar

from msgspec import Struct
from msgspec.yaml import decode as decode_yaml
from msgspec.yaml import encode as encode_yaml

_T = TypeVar("_T")


def _save_default_config(
    config_class: Type[Struct], *, file_name: str = "config.yaml"
) -> None:
    with open(file_name, "wb") as f:
        f.write(encode_yaml(config_class()))


def _load_config(config_class: Type[_T], *, file_name: str = "config.yaml") -> _T:
    with open(file_name, "rb") as f:
        return decode_yaml(f.read(), type=config_class)


def load_or_save_default_config(
    config_class: Type[_T], *, file_name: str = "config.yaml"
) -> _T:
    try:
        return _load_config(config_class, file_name=file_name)
    except FileNotFoundError:
        _save_default_config(config_class, file_name=file_name)
        print("已自动创建配置文件，请完成配置后重新运行...")
        exit()


def set_reload_on_sighup(
    config_class: Type[_T],
    *,
    file_name: str = "config.yaml",
    success_callback: Optional[Callable[[_T], None]] = None,
    failed_callback: Optional[Callable[[Exception], None]] = None,
) -> None:
    def handler(_, __) -> None:  # noqa: ANN001
        try:
            new_config = _load_config(config_class, file_name=file_name)
        except Exception as e:
            if failed_callback:
                failed_callback(e)
        else:
            if success_callback:
                success_callback(new_config)

    signal(SIGHUP, handler)


def unset_reload_on_sighup() -> None:
    signal(SIGHUP, SIG_DFL)
