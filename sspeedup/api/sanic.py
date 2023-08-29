from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict

from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, ValidationError
from pydantic._internal._model_construction import ModelMetaclass as _ModelMetaclass
from pydantic_core import ErrorDetails
from sanic import BadRequest, HTTPResponse, Request
from sanic.response import JSONResponse
from ujson import dumps as _dumps

from sspeedup.api.code import Code, get_default_msg, is_ok


def _json_dumps(x: Dict) -> str:
    return _dumps(x, ensure_ascii=False, allow_nan=False)


class BaseModel(_BaseModel):
    model_config = ConfigDict(
        str_max_length=50000,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class _ResponseType(TypedDict):
    ok: bool
    code: int
    msg: str
    data: Optional[Dict[str, Any]]


def get_response_json(
    *, code: Code, msg: Optional[str] = None, data: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    body: _ResponseType = {
        "ok": is_ok(code),
        "code": code.value,
        "msg": msg if msg else get_default_msg(code),
        "data": data,
    }
    return JSONResponse(
        body=body,
        dumps=_json_dumps,
    )


def _format_errors(errors: List[ErrorDetails]) -> str:
    result: List[str] = ["数据校验失败："]
    for error in errors:
        result.append(
            f"{' => '.join((str(x) for x in error['loc']))}（{error['type']}）：{error['msg']}"
        )
    return "\n".join(result)


def inject_pydantic_model(
    model: _ModelMetaclass, *, source: Literal["body", "query_args"] = "body"
) -> Callable:
    def outer(
        func: Callable[[Request, _BaseModel], HTTPResponse]
    ) -> Callable[[Request], HTTPResponse]:
        @wraps(func)
        def inner(request: Request) -> HTTPResponse:
            try:
                if source == "body":
                    data = model.model_validate_json(request.body)  # type: ignore
                else:
                    # 在 Query Args 规范中，每个 key 可以有多个 value
                    # 故 request.args 返回的是 Dict[str, List[Any]] 形式的数据
                    # 此处仅保留每个 key 的第一个 value
                    data = model.model_validate(  # type: ignore
                        {k: v[0] for k, v in request.args.items()}
                    )
            except BadRequest:
                return get_response_json(code=Code.DESERIALIZE_FAILED)
            except ValidationError as e:
                return get_response_json(
                    code=Code.BAD_ARGUMENTS,
                    msg=_format_errors(
                        e.errors(include_url=False, include_context=False)
                    ),
                )
            else:
                return func(request, data)

        return inner

    return outer
