# FastAPI COS Example

FastAPI + 腾讯云 COS 批量上传下载的完整示例代码。

对应文章：No.181 - FastAPI批量上传COS总超时？异步+分片+并发控制，3招搞定

## 项目结构

```
fastapi-cos-example/
├── cos_service/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── client.py          # COS 客户端封装
│   ├── upload.py          # 上传接口
│   ├── download.py        # 下载接口
│   └── exceptions.py      # 自定义异常
├── tests/
│   └── test_upload.py     # 测试用例
├── main.py                # 入口文件
├── requirements.txt       # 依赖
├── .env.example           # 环境变量示例
└── README.md              # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的腾讯云 COS 凭证
```

### 3. 启动服务

```bash
uvicorn main:app --reload
```

### 4. 测试接口

```bash
# 上传测试
curl -X POST "http://localhost:8000/upload/batch" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@test1.jpg" \
  -F "files=@test2.jpg"

# 下载测试
curl -X POST "http://localhost:8000/download/batch" \
  -H "Content-Type: application/json" \
  -d '{"keys": ["test1.jpg", "test2.jpg"]}' \
  -o download.zip
```

## 关键设计

- **异步化**：用 `asyncio.to_thread()` 包裹同步 COS SDK，不阻塞事件循环
- **并发控制**：`asyncio.Semaphore(5)` 限制并发，防止 COS 限流
- **流式下载**：`StreamingResponse` + 异步生成器，边下载边打包，不爆内存
- **配置管理**：`pydantic-settings` 集中管理环境变量，类型安全

## 进阶方案

对于大文件或高频场景，建议使用**预签名 URL**：

```python
# 后端生成临时上传 URL，前端直接上传到 COS
url = cos_client.get_presigned_url(
    Method="PUT",
    Bucket="mybucket",
    Key="uploads/photo.jpg",
    Expired=3600
)
# 前端直接 PUT 到 COS，不经过服务端中转
```

## 许可证

MIT
