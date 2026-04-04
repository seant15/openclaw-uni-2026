# Slack Channel → Agent 路由配置

## 当前映射

| Slack Channel | 默认 Agent | 用途 |
|--------------|-----------|------|
| #kimi-test | Kimi | 技术/代码测试 |
| #marketing | Writer | 内容创作 |
| #ops | Clover | 运营/管理 |
| #data | OpenClaw | 数据分析 |
| #general | Clover | 综合讨论 |

## 使用方法

### 方式 1：Channel 前缀（最灵活）
在任何 channel 中：
```
[writer] 帮我写一份广告文案
[kimi] 这个代码报错怎么办
```

### 方式 2：直接 @ 提及（如果配置了多 agent 支持）
```
@kimi 检查这个 API
@writer 优化这段文案
```

### 方式 3：让当前 agent 转交
```
帮我转给 Kimi，这是个技术问题
```

## 配置更新

如需添加新 channel 或修改映射，更新此文件并重启 Gateway。
