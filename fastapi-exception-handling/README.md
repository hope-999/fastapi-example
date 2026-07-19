# fastapi-exception-handling

FastAPI 全局异常处理完整示例，包含自定义异常、统一响应模型、日志与返回分离、pytest 测试。

## 快速开始

```bash
cd fastapi-exception-handling
pip install -r requirements.txt
uvicorn main:app --reload
```

## 测试

```bash
pytest test_main.py -v
```

## 结构

```
fastapi-exception-handling/
├── exceptions.py       # 自定义业务异常
├── schemas.py          # 统一错误响应模型
├── handlers.py         # 全局异常处理器
├── logging_config.py   # 日志配置
├── main.py             # 主应用
└── test_main.py        # 测试用例
```
