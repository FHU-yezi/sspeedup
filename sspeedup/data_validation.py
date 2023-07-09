from functools import wraps
from typing import Callable, Literal

from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, ValidationError
from pydantic._internal._model_construction import ModelMetaclass
from sanic import BadRequest, HTTPResponse, Request

from sspeedup.api import CODE, sanic_response_json


class BaseModel(_BaseModel):
    model_config = ConfigDict(
        str_max_length=50000,
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


def format_validation_error_message(e: ValidationError) -> str:
    result = []
    for item in e.errors(include_url=False):
        if item["type"] == "missing":
            result.append(f"字段缺失：{item['loc'][0]}")
        elif item["type"] == "extra_forbidden":
            result.append(f"多余字段：{item['loc'][0]}")
        elif item["type"].endswith("_type"):
            result.append(
                f"字段类型错误：字段 {item['loc'][0]} "
                f"应为 {item['type'].replace('_type', '')}，实为 {type(item['input']).__name__}"
            )
        elif item["type"] == "greater_than":
            result.append(
                f"范围超限：字段 {item['loc'][0]} 必须大于 {item['ctx']['gt']}，实为 {item['input']}"
            )
        elif item["type"] == "greater_than_equal":
            result.append(
                f"范围超限：字段 {item['loc'][0]} 必须大于等于 {item['ctx']['ge']}，实为 {item['input']}"
            )
        elif item["type"] == "less_than":
            result.append(
                f"范围超限：字段 {item['loc'][0]} 必须小于 {item['ctx']['lt']}，实为 {item['input']}"
            )
        elif item["type"] == "less_than_equal":
            result.append(
                f"范围超限：字段 {item['loc'][0]} 必须小于等于 {item['ctx']['le']}，实为 {item['input']}"
            )
        else:
            result.append(
                f"参数校验失败（{item['type']}）：{item['msg']}, at {item['loc']}"
            )

    return "\n".join(result)


def sanic_inject_pydantic_model(
    model: ModelMetaclass, source: Literal["body", "query_args"] = "body"
) -> Callable:
    def outer(
        func: Callable[[Request, _BaseModel], HTTPResponse]
    ) -> Callable[[Request], HTTPResponse]:
        @wraps(func)
        def inner(request: Request) -> HTTPResponse:
            try:
                if source == "body":
                    data = model.model_validate_json(request.body)
                else:
                    # 在 Query Args 规范中，每个 key 可以有多个 value
                    # 故 request.args 返回的是 Dict[str, List[Any]] 形式的数据
                    # 此处仅保留每个 key 的第一个 value
                    data = model.model_validate(
                        {k: v[0] for k, v in request.args.items()}
                    )
            except BadRequest:
                return sanic_response_json(code=CODE.UNKNOWN_DATA_FORMAT)
            except ValidationError as e:
                return sanic_response_json(
                    code=CODE.BAD_ARGUMENTS, message=format_validation_error_message(e)
                )
            else:
                return func(request, data)

        return inner

    return outer
