# sspeedup

开发工具箱。

支持调用 [CutUp](https://github.com/FHU-yezi/CutUp) 分词能力进行分词。

包含 API 错误码与默认错误信息定义，面向 Sanic 和 Litestar 提供部分功能封装。

支持使用 Sanic + Pydantic / Litestar + Msgspec 实现依赖注入。

`sspeedup.cache.timeout` 包含一个过期缓存装饰器。

支持记录运行日志。

对 PyWwebIO 操作进行了封装和扩展。

包含指数退避装饰器。

支持终端彩色输出。

支持通过 `qrcode` 库生成二维码。

对字典和 `datetime` 库的常用操作进行了封装。