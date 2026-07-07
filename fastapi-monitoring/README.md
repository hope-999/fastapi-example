# FastAPI + Prometheus + Grafana 监控示例

本文配套代码，对应公众号文章「服务崩了还不知道？Prometheus + Grafana 5 分钟让报警比用户先到」。

## 目录结构

```
fastapi-monitoring/
├── docker-compose.yml      # 七服务全栈配置
├── prometheus.yml          # Prometheus 抓取配置
├── alerts.yml              # 报警规则
├── alertmanager.yml        # 报警通知路由
└── app/
    ├── Dockerfile          # 多阶段构建
    ├── main.py             # FastAPI + Prometheus 指标
    └── requirements.txt    # 依赖
```

## 快速启动

```bash
cd fastapi-monitoring

docker-compose up -d --build
```

访问地址：
- FastAPI 服务：http://localhost:8000
- Prometheus：http://localhost:9090
- Grafana：http://localhost:3000（admin/admin）
- 指标端点：http://localhost:8000/metrics

## 验证清单

- [ ] `docker-compose ps` 七服务状态都是 `Up`
- [ ] `curl http://localhost:8000/health` 返回 `{"status":"ok"}`
- [ ] Prometheus Targets 页面看到 `fastapi` job 状态 UP
- [ ] Grafana 导入看板 ID `11159` 或自建面板
- [ ] 触发 `curl http://localhost:8000/orders/123` 后指标有变化

## 生产建议

1. 修改 `alerts.yml` 中的阈值，匹配你的 SLA
2. 替换 `alertmanager.yml` 中的 webhook URL 为你的钉钉/飞书机器人
3. Prometheus 数据长期存储建议接入 Thanos 或 VictoriaMetrics
4. `/metrics` 端点不要暴露给公网

---

配套文章系列：
- [Docker Compose 部署](https://github.com/hope-999/fastapi-example/tree/main/fastapi-deploy)
- [Redis 缓存预热](https://github.com/hope-999/fastapi-example/tree/main/fastapi-prewarm)
- [Redis 缓存](https://github.com/hope-999/fastapi-example/tree/main/fastapi-redis-cache)
