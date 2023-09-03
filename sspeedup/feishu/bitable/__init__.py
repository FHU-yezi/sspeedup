from typing import Any, AsyncGenerator, Dict, Generic, Optional, Sequence, TypeVar

from httpx import AsyncClient
from msgspec import Struct, convert, to_builtins

from sspeedup.feishu.auth import FeishuAuthToken
from sspeedup.feishu.bitable.structs import _BitableRecord

_T = TypeVar("_T")


class Bitable(Generic[_T]):
    def __init__(
        self,
        *,
        auth_token: FeishuAuthToken,
        app_id: str,
        table_id: str,
        table_struct: _T,
        network_client: Optional[AsyncClient] = None,
    ) -> None:
        self._auth_token = auth_token
        self._app_id = app_id
        self._table_id = table_id
        self._table_struct = table_struct
        self._network_client = network_client if network_client else AsyncClient()

    async def iter_records(
        self,
        view_id: Optional[str] = None,
        fliter: Optional[str] = None,
        sort: Optional[str] = None,
        field_names: Optional[Sequence[str]] = None,
    ) -> AsyncGenerator[_BitableRecord[_T], None]:
        headers = {"Authorization": f"Bearer {await self._auth_token.get_token()}"}
        params = {
            "view_id": view_id,
            "fliter": fliter,
            "sort": sort,
            # 示例：["a", "b"]
            "field_names": "".join(("[", ",".join(f'"{x}"' for x in field_names), "]"))
            if field_names
            else None,
        }

        has_more: Optional[bool] = None
        page_token: Optional[str] = None

        while True:
            # 如果有更多数据，则在新的请求中携带 page_token
            if has_more:
                params.update({"page_token": page_token})

            response = await self._network_client.get(
                f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
                f"{self._app_id}/tables/{self._table_id}/records",
                params=params,
                headers=headers,
            )
            response_json = response.json()

            if response_json["code"] != 0:
                raise Exception(
                    f"获取表格记录数据失败（{response_json['code']}）：{response_json['msg']}"
                )

            has_more = response_json["data"]["has_more"]
            page_token = response_json["data"]["page_token"] if has_more else None

            # 避免无数据时报错
            if response_json["data"].get("items"):
                for item in response_json["data"]["items"]:
                    yield convert(
                        item,
                        type=_BitableRecord[self._table_struct],  # type: ignore
                    )

            if not has_more:
                return

    async def add_record(self, record: Struct) -> None:
        headers = {"Authorization": f"Bearer {await self._auth_token.get_token()}"}
        data = {
            "fields": to_builtins(record),
        }
        response = await self._network_client.post(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{self._app_id}/tables/{self._table_id}/records",
            json=data,
            headers=headers,
        )

        response_json = response.json()

        if response_json["code"] != 0:
            raise Exception(
                f"添加表格记录数据失败（{response_json['code']}）：{response_json['msg']}"
            )

    async def update_record(self, record_id: str, fields: Dict[str, Any]) -> None:
        headers = {"Authorization": f"Bearer {await self._auth_token.get_token()}"}
        data = {
            "fields": fields,
        }
        response = await self._network_client.put(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{self._app_id}/tables/{self._table_id}/records/{record_id}",
            json=data,
            headers=headers,
        )

        response_json = response.json()

        if response_json["code"] != 0:
            raise Exception(
                f"更新表格记录数据失败（{response_json['code']}）：{response_json['msg']}"
            )
