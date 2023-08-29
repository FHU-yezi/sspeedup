from enum import Enum, IntEnum


class Code(IntEnum):
    # 0：请求成功
    SUCCESS = 0

    # 1：请求成功，有额外信息
    DEPRECATED = 101
    UPCOMING_MAINTENANCE = 102

    # 2：数据异常
    UNKNOWN_DATA_ERROR = 200
    DESERIALIZE_FAILED = 201
    SERIALIZE_FAILED = 202
    BAD_ARGUMENTS = 203
    CONFLICT = 204

    # 3：鉴权异常
    UNKNOWN_AUTH_ERROR = 300
    MISSING_TOKEN = 301
    BAD_TOKEN = 302
    PERMISSION_DENIED = 303
    BANNED = 304

    # 4：限流
    UNKNOWN_RATE_LIMIT = 400
    RATE_LIMIT_GLOBAL = 401
    RATE_LIMIT_BY_USER = 402
    RATE_LIMIT_BY_IP = 403

    # 5：服务端异常
    UNKNOWN_SERVER_ERROR = 500
    OVERLOAD = 501
    UPSTREAM_ERROR = 503
    SCHEDULED_OUTAGE = 504
    UNSCHEDULED_OUTAGE = 505


class Msg(Enum):
    # 0：请求成功
    SUCCESS = ""

    # 1：请求成功，有额外信息
    DEPRECATED = "该接口已被弃用"
    UPCOMING_MAINTENANCE = "即将进行计划维护"

    # 2：数据异常
    UNKNOWN_DATA_ERROR = "未知数据异常"
    DESERIALIZE_FAILED = "反序列化失败"
    SERIALIZE_FAILED = "序列化失败"
    BAD_ARGUMENTS = "参数异常"
    CONFLICT = "数据冲突"

    # 3：鉴权异常
    UNKNOWN_AUTH_ERROR = "未知鉴权异常"
    MISSING_TOKEN = "缺少鉴权信息"  # noqa: S105
    BAD_TOKEN = "鉴权信息无效"  # noqa: S105
    PERMISSION_DENIED = "权限不足"
    BANNED = "您已被禁止执行此操作"

    # 4：限流
    UNKNOWN_RATE_LIMIT = "触发未知限流"
    RATE_LIMIT_GLOBAL = "触发全局限流"
    RATE_LIMIT_BY_USER = "触发用户限流"
    RATE_LIMIT_BY_IP = "触发 IP 限流"

    # 5：服务端异常
    UNKNOWN_SERVER_ERROR = "未知服务端异常"
    OVERLOAD = "服务过载"
    UPSTREAM_ERROR = "上游服务异常"
    SCHEDULED_OUTAGE = "计划内停机"
    UNSCHEDULED_OUTAGE = "计划外停机"


def is_ok(code: Code) -> bool:
    return code == 0 or 100 <= code <= 199


def get_default_msg(code: Code) -> str:
    return Msg[code.name].value
