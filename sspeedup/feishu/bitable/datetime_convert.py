from datetime import datetime


def to_feishu_datetime(python_datetime: datetime) -> int:
    return int(python_datetime.timestamp() * 1000)


def to_python_datetime(feishu_datetime: int) -> datetime:
    return datetime.fromtimestamp(feishu_datetime / 1000)
