from typing import Any, Dict

from msgspec import Struct

from sspeedup.logging.run_logger import LogLevel

CONFIG_STRUCT_CONFIG: Dict[str, Any] = {
    "forbid_unknown_fields": True,
    "frozen": True,
    "kw_only": True,
}


class MongoDBConfig(Struct, **CONFIG_STRUCT_CONFIG):
    host: str = "localhost"
    port: int = 27017
    database: str = ""


class DeployConfig(Struct, **CONFIG_STRUCT_CONFIG):
    version: str = "v0.1.0"
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 1
    reload: bool = False
    access_log: bool = False


class LoggingConfig(Struct, **CONFIG_STRUCT_CONFIG):
    save_level: LogLevel = LogLevel.DEBUG
    print_level: LogLevel = LogLevel.DEBUG


class FeishuAuthConfig(Struct, **CONFIG_STRUCT_CONFIG):
    app_id: str = ""
    app_secret: str = ""


class FeishuBitableConfig(Struct, **CONFIG_STRUCT_CONFIG):
    app_id: str = ""
    table_id: str = ""


class FeishuMessageConfig(Struct, **CONFIG_STRUCT_CONFIG):
    target_user_email: str = ""


class AbilityWordSplitConfig(Struct, **CONFIG_STRUCT_CONFIG):
    host: str = "localhost"
    port: int = 6001
