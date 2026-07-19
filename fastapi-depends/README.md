# fastapi-depends

FastAPI 依赖注入 5 大高阶用法完整示例。

## 用法列表

| 文件 | 主题 | 关键词 |
|------|------|--------|
| `01_use_cache.py` | 依赖缓存控制 | `use_cache=False` |
| `02_nested.py` | 嵌套依赖 | `Depends(get_current_user)` |
| `03_factory.py` | 带参数的依赖工厂 | `functools.partial` / 闭包 |
| `04_class.py` | 类级别依赖 | `__call__()` 状态保持 |
| `05_optional.py` | 条件跳过依赖 | `Optional` 可选鉴权 |

## 快速开始

```bash
cd fastapi-depends
pip install -r requirements.txt
uvicorn 02_nested:app --reload
```

## 对应文章

「FastAPI 依赖注入只会 get_db？这 5 个高阶用法，90% 的人没用过」

完整文章和配图见仓库 `fastapi-depends-article/` 目录。
