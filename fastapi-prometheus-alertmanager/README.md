# FastAPI + Prometheus + Alertmanager 告警体系

> 对应公众号文章：「服务崩了还在刷朋友圈？Prometheus + Alertmanager 5 分钟让告警飞到你微信」

## 项目结构

```
fastapi-prometheus-alertmanager/
├── alert_rules.yml          # Prometheus 告警规则
├── alertmanager.yml          # Alertmanager 配置（路由/分组/抑制）
├── prometheus.yml            # Prometheus 采集配置
├── receiver.py               # FastAPI 企业微信 Webhook 接收器
├── docker-compose.yml        # 一键启动所有服务
├── requirements.txt          # Python 依赖
└── README.md                 # 本文档
```

## 快速启动

### 1. 配置企业微信机器人

在 `receiver.py` 中替换 `WECHAT_BOT_KEY`：

```python
WECHAT_BOT_KEY = "your-bot-key-here"
```

或在 `docker-compose.yml` 中设置环境变量：

```yaml
environment:
  - WECHAT_BOT_KEY=your-bot-key-here
```

### 2. 启动所有服务

```bash
docker-compose up -d
```

服务清单：
- FastAPI App: http://localhost:8000
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- Grafana: http://localhost:3000 (admin/admin)
- Webhook Receiver: http://localhost:8001

### 3. 验证告警流程

1. 访问 Prometheus → Status → Rules，确认告警规则已加载
2. 触发告警（如人为制造高错误率）
3. 查看 Alertmanager → Alerts，确认告警状态为 firing
4. 检查企业微信是否收到告警消息

## 告警规则说明

| 规则名 | 级别 | 条件 | 防抖时间 |
|--------|------|------|----------|
| HighErrorRate | critical | 5xx 错误率 > 1% | 2m |
| HighLatency | warning | P95 延迟 > 500ms | 3m |
| HighCPUUsage | critical | CPU 使用率 > 80% | 5m |
| HighMemoryUsage | warning | 内存使用率 > 85% | 5m |

## Alertmanager 核心配置

- `group_by: ['alertname', 'severity']` — 合并同类告警
- `group_wait: 10s` — 等待 10s 聚合同组告警
- `repeat_interval: 4h` — 同一告警 4 小时内不重复轰炸
- `send_resolved: true` — 告警恢复时发送通知

## 关键踩坑点

1. **for 字段不能省略**：防止接口抖动误报
2. **group_by 必须配置**：否则告警风暴直接炸穿企业微信频率限制（20 条/分钟）
3. **send_resolved 必须 true**：只发触发不发放恢复 = 不知道故障自己好了还是修好的
4. **Webhook 超时**：Alertmanager 默认 10 秒超时，receiver 必须用异步 httpx

## 更多配置

### 告警静默（维护窗口）

```bash
curl -X POST http://localhost:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "severity", "value": "warning", "isRegex": false}],
    "startsAt": "2026-07-14T02:00:00Z",
    "endsAt": "2026-07-14T04:00:00Z",
    "createdBy": "ops",
    "comment": "Scheduled maintenance"
  }'
```

## License

MIT
