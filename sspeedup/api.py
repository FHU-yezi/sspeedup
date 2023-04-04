from enum import Enum, IntEnum
from typing import Any, Dict, Optional

from sspeedup.require import require


class CODE(IntEnum):
    SUCCESS = 0

    DEPRECATED = 101
    CLOSE_TO_QUOTA_LIMIT = 102
    UPCOMING_MAINTENANCE = 103

    MISSED_ARGUMENTS_OR_BAD_TYPES = 401
    ARGUMENTS_CHECK_FAILED = 402

    SERVER_OVERLOAD = 501
    RATE_LIMIT = 502
    SCHEDULED_OUTAGE = 503
    UNSCHEDULED_OUTAGE = 504
    BAD_TOKEN = 505
    API_QUOTA_REACHED = 506
    BANNED = 507
    PERMISSION_DENIED = 508


class MESSAGE(Enum):
    SUCCESS = ""

    DEPRECATED = "该接口已被弃用，请尽快进行迁移"
    CLOSE_TO_QUOTA_LIMIT = "即将达到配额限制"
    UPCOMING_MAINTENANCE = "即将进行维护"

    MISSED_ARGUMENTS_OR_BAD_TYPES = "缺少参数或参数类型错误"
    ARGUMENTS_CHECK_FAILED = "参数校验失败"

    SERVER_OVERLOAD = "服务过载"
    RATE_LIMIT = "限流"
    SCHEDULED_OUTAGE = "计划内停机"
    UNSCHEDULED_OUTAGE = "计划外停机"
    BAD_TOKEN = "鉴权信息无效"  # noqa: S105
    API_QUOTA_REACHED = "达到配额限制"
    BANNED = "服务禁用"
    PERMISSION_DENIED = "权限不足"


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
