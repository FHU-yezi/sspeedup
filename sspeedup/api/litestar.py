from typing import Any, Dict, Generic, List, Optional, TypeVar, cast

from litestar import Request, Response
from litestar.exceptions import ValidationException
from litestar.exceptions.http_exceptions import (
    MethodNotAllowedException,
    NotFoundException,
)
from litestar.types import ExceptionHandlersMap
from msgspec import Struct

from sspeedup.api.code import Code, get_default_msg, is_ok

_T = TypeVar("_T")


class RequestBase(Struct, kw_only=True, forbid_unknown_fields=True, rename="camel"):
    pass


class ResponseBase(Struct, kw_only=True, rename="camel"):
    pass


class ResponseStruct(Struct, Generic[_T], frozen=True, kw_only=True):
    ok: bool
    code: int
    msg: str
    data: Optional[_T] = None


def get_response_struct(
    *, code: Code, msg: Optional[str] = None, data: Optional[_T] = None
) -> ResponseStruct[_T]:
    return ResponseStruct(
        ok=is_ok(code),
        code=code,
        msg=msg if msg else get_default_msg(code),
        data=data,
    )


SWAGGER_OPENAPI_CONFIG = {
    "root_schema_site": "swagger",
    "enabled_endpoints": {"swagger"},
}


def _format_validation_errors(
    detail: str, extra: Optional[List[Dict[str, Any]]]
) -> str:
    if not extra:
        return detail

    result: List[str] = ["数据校验失败："]
    for item in extra:
        result.append(f"{item['key']}（{item['source'].value}）：{item['message']}")

    return "\n".join(result)


def validation_exception_handler(
    _: Request, exception: Exception
) -> Response[ResponseStruct]:
    exception = cast(ValidationException, exception)

    return Response(
        get_response_struct(
            code=Code.BAD_ARGUMENTS,
            msg=_format_validation_errors(exception.detail, exception.extra),  # type: ignore
        ),
        status_code=400,
    )


def not_found_exception_handler(_: Request, exception: Exception) -> Response[None]:
    return Response(None, status_code=404)


def method_not_allowd_exception_handler(
    _: Request, exception: Exception
) -> Response[None]:
    return Response(None, status_code=405)


_DESERIALIZE_FAILED_ARGS_STRING = {
    "400: Input data was truncated",
    "400: JSON is malformed",
}


def internal_server_exception_handler(
    _: Request, exception: Exception
) -> Response[ResponseStruct]:
    if len(exception.args) == 1:
        for item in _DESERIALIZE_FAILED_ARGS_STRING:
            if item in exception.args[0]:
                # 反序列化失败
                return Response(
                    get_response_struct(code=Code.DESERIALIZE_FAILED), status_code=400
                )

    return Response(
        get_response_struct(
            code=Code.UNKNOWN_SERVER_ERROR,
        ),
        status_code=500,
    )


EXCEPTION_HANDLERS: ExceptionHandlersMap = {
    ValidationException: validation_exception_handler,
    NotFoundException: not_found_exception_handler,
    MethodNotAllowedException: method_not_allowd_exception_handler,
    Exception: internal_server_exception_handler,
}
