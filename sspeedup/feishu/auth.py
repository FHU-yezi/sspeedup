from datetime import datetime, timedelta
from typing import Optional

from httpx import AsyncClient


class FeishuAuthToken:
    def __init__(
        self,
        *,
        app_id: str,
        app_secret: str,
        network_client: Optional[AsyncClient] = None,
    ) -> None:
        self._app_id = app_id
        self._app_secret = app_secret
        self._network_client = network_client if network_client else AsyncClient()

        self._token: Optional[str] = None
        self._token_expire_time: Optional[datetime] = None

    async def get_token(self) -> str:
        # 如果缓存了 Token，且 Token 距离过期还有半个小时以上
        # 此时再次请求会返回相同的 Token，故直接从缓存中返回
        if (
            self._token
            and self._token_expire_time
            and self._token_expire_time - datetime.now() > timedelta(minutes=30)
        ):
            return self._token

        data = {
            "app_id": self._app_id,
            "app_secret": self._app_secret,
        }
        response = await self._network_client.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json=data,
        )

        response_json = response.json()
        if response_json["code"] != 0:
            raise Exception(f"获取鉴权信息失败（{response_json['code']}）：{response_json['msg']}")

        self._token = response_json["tenant_access_token"]
        self._token_expire_time = datetime.now() + timedelta(
            seconds=response_json["expire"]
        )

        return response_json["tenant_access_token"]
