from typing import Generic, List, TypeVar

from msgspec import Struct

_BITABLE_STRUCT_CONFIG = {
    "frozen": True,
    "kw_only": True,
}

_T = TypeVar("_T")


class _BitableRecord(Struct, Generic[_T], **_BITABLE_STRUCT_CONFIG):
    record_id: str
    fields: _T


class BitableLink(Struct, **_BITABLE_STRUCT_CONFIG):
    text: str
    link: str


class _BitableFormulaInner(Struct, **_BITABLE_STRUCT_CONFIG):
    type: str  # noqa: A003
    text: str


BitableFormula = List[_BitableFormulaInner]
