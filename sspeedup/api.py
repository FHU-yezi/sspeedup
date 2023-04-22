from enum import Enum, IntEnum
from typing import Any, Dict, Optional

from sspeedup.require import require


class CODE(IntEnum):
    """
    状态码规范：

    0：请求成功
    1xx：请求成功，但有额外信息需要注意
    4xx：客户端异常
    5xx：服务端异常

    第二位大类定义：

    1：参数
    2：响应
    3：鉴权
    4：配额
    5：接口维护状态
    6：流控
    7：上游服务
    8：服务器状态
    9：保留
    """

    SUCCESS = 0

    CLOSE_TO_QUOTA_LIMIT = 141
    DEPRECATED = 151
    UPCOMING_MAINTENANCE = 181

    UNKNOWN_DATA_FORMAT = 411
    BAD_ARGUMENTS = 412
    BAD_TOKEN = 431
    BANNED = 432
    PERMISSION_DENIED = 433
    API_QUOTA_REACHED = 441
    RATE_LIMIT_BY_USER = 461

    RATE_LIMIT_GLOBAL = 561
    SERVER_OVERLOAD = 581
    SCHEDULED_OUTAGE = 582
    UNSCHEDULED_OUTAGE = 583


class MESSAGE(Enum):
    SUCCESS = ""

    CLOSE_TO_QUOTA_LIMIT = "即将达到配额限制"
    DEPRECATED = "该接口已被弃用"
    UPCOMING_MAINTENANCE = "即将进行维护"

    UNKNOWN_DATA_FORMAT = "数据格式异常"
    BAD_ARGUMENTS = "参数异常"
    BAD_TOKEN = "鉴权信息无效"  # noqa: S105
    BANNED = "服务禁用"
    PERMISSION_DENIED = "权限不足"
    API_QUOTA_REACHED = "达到配额限制"
    RATE_LIMIT_BY_USER = "用户端限流"

    RATE_LIMIT_GLOBAL = "全局限流"
    SERVER_OVERLOAD = "服务过载"
    SCHEDULED_OUTAGE = "计划内停机"
    UNSCHEDULED_OUTAGE = "计划外停机"


def is_ok(code: CODE) -> bool:
    return code.value == 0 or 100 <= code.value <= 199


def get_default_message(code: CODE) -> str:
    return MESSAGE[code.name].value


def response_json(
    code: CODE, message: str = "", data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return {
        "ok": is_ok(code),
        "code": code.value,
        "message": message if message else get_default_message(code),
        "data": data if data else {},
    }


def sanic_response_json(  # noqa: ANN201
    code: CODE, message: str = "", data: Optional[Dict[str, Any]] = None
):
    require("sanic")
    from sanic.response import JSONResponse

    return JSONResponse(
        body=response_json(
            code=code,
            message=message,
            data=data,
        )
    )
