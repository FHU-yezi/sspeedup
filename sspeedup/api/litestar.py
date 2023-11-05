from enum import Enum
from traceback import print_exception
from typing import Any, Dict, Generic, List, Optional, TypeVar, cast

from litestar import Request, Response
from litestar.exceptions import ValidationException
from litestar.exceptions.http_exceptions import (
    MethodNotAllowedException,
    NotFoundException,
)
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.types import ExceptionHandlersMap
from msgspec import Struct

from sspeedup.api.code import Code, get_default_msg, is_ok

_T = TypeVar("_T")

REQUEST_STRUCT_CONFIG: Dict[str, Any] = {
    "frozen": True,
    "kw_only": True,
    "forbid_unknown_fields": True,
    "rename": "camel",
}

RESPONSE_STRUCT_CONFIG: Dict[str, Any] = {
    "kw_only": True,
    "rename": "camel",
}


class ResponseStruct(Struct, Generic[_T], frozen=True, kw_only=True):
    ok: bool
    code: int
    msg: str
    data: _T


def success(
    *,
    http_code: int = HTTP_200_OK,
    code: Code = Code.SUCCESS,
    msg: Optional[str] = None,
    data: _T = None,
) -> Response[ResponseStruct[_T]]:
    return Response(
        ResponseStruct(
            ok=is_ok(code),
            code=code,
            msg=msg if msg else get_default_msg(code),
            data=data,
        ),
        status_code=http_code,
    )


def fail(
    *,
    http_code: int = HTTP_500_INTERNAL_SERVER_ERROR,
    code: Code = Code.UNKNOWN_SERVER_ERROR,
    msg: Optional[str] = None,
    data: _T = None,
) -> Response[ResponseStruct[_T]]:
    return Response(
        ResponseStruct(
            ok=is_ok(code),
            code=code,
            msg=msg if msg else get_default_msg(code),
            data=data,
        ),
        status_code=http_code,
    )


def _format_validation_errors(
    detail: str, extra: Optional[List[Dict[str, Any]]]
) -> str:
    if not extra:
        return detail

    result: List[str] = ["数据校验失败："]
    for item in extra:
        result.append(
            f"{item['key']}"
            f"（{item['source'].value if isinstance(item['source'], Enum) else item['source']}）："
            f"{item['message']}"
        )

    return "\n".join(result)


def validation_exception_handler(
    _: Request, exception: Exception
) -> Response[ResponseStruct]:
    exception = cast(ValidationException, exception)

    return fail(
        http_code=HTTP_400_BAD_REQUEST,
        code=Code.BAD_ARGUMENTS,
        msg=_format_validation_errors(exception.detail, exception.extra),  # type: ignore
    )


def not_found_exception_handler(_: Request, exception: Exception) -> Response[bytes]:
    return Response(b"", status_code=HTTP_404_NOT_FOUND)


def method_not_allowd_exception_handler(
    _: Request, exception: Exception
) -> Response[bytes]:
    return Response(b"", status_code=HTTP_405_METHOD_NOT_ALLOWED)


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
                return fail(
                    http_code=HTTP_400_BAD_REQUEST,
                    code=Code.DESERIALIZE_FAILED,
                )

    print_exception(exception)

    return fail(
        http_code=HTTP_500_INTERNAL_SERVER_ERROR,
        code=Code.UNKNOWN_SERVER_ERROR,
    )


EXCEPTION_HANDLERS: ExceptionHandlersMap = {
    ValidationException: validation_exception_handler,
    NotFoundException: not_found_exception_handler,
    MethodNotAllowedException: method_not_allowd_exception_handler,
    Exception: internal_server_exception_handler,
}
