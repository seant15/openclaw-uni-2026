# Paperclip × OpenClaw — 最少步骤

Agent 不能替你点 Paperclip 网页，也不能 SSH 进你的 VPS。本地仓库只提供 **一条命令**。

## 在 OpenClaw VPS 上（一条命令）

```bash
curl -fsSL https://raw.githubusercontent.com/seant15/openclaw-uni-2026/main/scripts/paperclip-onboard.sh -o /tmp/paperclip-onboard.sh
chmod +x /tmp/paperclip-onboard.sh
# 换新 invite 时：INVITE_ID=pcp_invite_xxxxx /tmp/paperclip-onboard.sh
/tmp/paperclip-onboard.sh
```

或仓库已 clone 时：

```bash
bash /path/to/openclaw-uni-2026/scripts/paperclip-onboard.sh
```

脚本会：读 `/opt/openclaw/data/.openclaw/openclaw.json` 里的 **真 token** → test-resolution → 提交 join。

## 你只用手做 2 件事

1. **Paperclip 网页** → 批准（Approve）agent `kimi`
2. 若仍报 **protocol mismatch** → 在 **Paperclip 那台 VPS** 升级 Paperclip（或 OpenClaw 暂时降到 `2026.5.10`）

批准前若 join 里 token 曾填错，重新跑一遍脚本即可（或 Paperclip 里改 agent 的 token）。

## 连通性（已验证可略过）

- `https://open.uni-agency.com` → test-resolution 用 **https**，不是 wss
- Agent 连 Gateway 用 **wss://open.uni-agency.com**
