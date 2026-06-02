# fastapi-example

个人 FastAPI 示例项目集合。

## 项目列表

### fastapi-cos-example

FastAPI + 腾讯云 COS 批量上传下载的完整示例。

对应文章：No.181 - FastAPI批量上传COS总超时？异步+分片+并发控制，3招搞定

- 异步化 COS SDK（`asyncio.to_thread`）
- 批量上传并发控制（`asyncio.Semaphore`）
- 批量下载流式 ZIP（`StreamingResponse`）
- 生产级封装（`pydantic-settings`）

进入目录查看详情：
```bash
cd fastapi-cos-example
```
