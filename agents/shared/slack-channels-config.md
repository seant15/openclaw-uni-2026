# Slack Channel 自动加入配置

## 已配置 Channels

| Channel ID | 名称 | Agent | 状态 |
|------------|------|-------|------|
| C067HPUPUQ2 | (Private) | Clover | ✅ Active |
| Cxxxxxxxxx | #kimi-test | Kimi | ✅ Active |
| Cxxxxxxxxx | #marketing | Writer | ✅ Active |

## 添加新 Channel

### 方式 1：Slack 内邀请（即时生效）
在任意 channel 输入：
```
/invite @OpenClaw
```

### 方式 2：配置自动加入（永久）
提供 Channel ID（格式：Cxxxxxxxx），我添加到 `autoJoinChannels` 列表。

**获取 Channel ID 方法：**
1. 在 Slack 中右键 channel 名称
2. 选择 "Copy link"
3. 链接最后部分就是 ID
   - 例：`https://uni-agency.slack.com/archives/C067HPUPUQ2`
   - ID: `C067HPUPUQ2`

### 方式 3：Private Channel
Private channel 必须使用 **方式 1**（邀请），无法自动加入。

## 配置更新流程

1. 提供 Channel ID
2. 选择默认 Agent（clover/kimi/writer/atlas/openclaw）
3. 我更新配置并重启
4. 30 秒内生效
