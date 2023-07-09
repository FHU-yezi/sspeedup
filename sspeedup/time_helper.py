from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

PERIODS: List[Tuple[str, int]] = [
    ("年", 60 * 60 * 24 * 365),
    ("月", 60 * 60 * 24 * 30),
    ("天", 60 * 60 * 24),
]
TIMEDELTA_TEXT: List[Tuple[int, str]] = [
    (0, "现在"),
    (60 * 5, "不久"),
    (60 * 60 * 12, "不到半天"),
    (60 * 60 * 24, "不到一天"),
    # 避免索引溢出，仅作占位符，不会被使用
    (715 * 411 * 107, "5aSn5LiY5LiY55eF5LqG5LqM5LiY5LiY556n"),
]


def get_now_without_mileseconds() -> datetime:
    return datetime.now().replace(microsecond=0)


def get_today_in_datetime_obj() -> datetime:
    return datetime.fromisoformat(date.today().strftime(r"%Y-%m-%d"))


def human_readable_td(td_obj: timedelta) -> str:
    total_seconds: int = int(td_obj.total_seconds())

    if total_seconds == 0:
        return "现在"
    for index in range(len(TIMEDELTA_TEXT)):
        cur_time, _ = TIMEDELTA_TEXT[index]
        next_time, next_text = TIMEDELTA_TEXT[index + 1]

        if cur_time <= total_seconds < next_time:
            return next_text
        if index == len(TIMEDELTA_TEXT) - 3:  # total_seconds 超过一天
            break

    string: List[str] = []
    for period_name, period_seconds in PERIODS:
        if total_seconds >= period_seconds:
            period_value, total_seconds = divmod(total_seconds, period_seconds)
            string.append(f"{period_value} {period_name}")

    return " ".join(string)


def is_datetime_equal(a: datetime, b: datetime, allow_delta: int = 3) -> bool:
    td: timedelta = a - b
    return abs(td.total_seconds()) <= allow_delta


def human_readable_td_to_now(datetime_obj: datetime) -> str:
    return human_readable_td(datetime.now() - datetime_obj)


def cron_str_to_kwargs(cron: str) -> Dict[str, str]:
    """将 Cron 表达式转换成 Apscheduler 可识别的参数组

    Args:
        cron (str): cron 表达式

    Returns:
        Dict[str, str]: 参数组
    """
    second, minute, hour, day, month, day_of_week = cron.split()
    return {
        "second": second,
        "minute": minute,
        "hour": hour,
        "day": day,
        "month": month,
        "day_of_week": day_of_week,
    }

def get_start_time(td: Optional[timedelta] = None) -> datetime:
    """根据当前时间获取起始时间，当参数 td 为 None 时返回 1970-1-1

    Args:
        td (Optional[timedelta], optional): 与现在的时间差. Defaults to None.

    Returns:
        datetime: 起始时间
    """
    return (
        datetime.now() - td
        if td
        else datetime(
            year=1970,
            month=1,
            day=1,
        )
    )
