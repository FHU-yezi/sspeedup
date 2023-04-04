from importlib import import_module


def require(name: str) -> None:
    """测试模块是否已经安装

    Args:
        name (str): 模块名

    Raises:
        ImportError: 模块未安装
    """
    try:
        import_module(name)
    except ImportError:
        raise ImportError(f"模块 {name} 未安装") from None
