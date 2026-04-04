# Known Mistakes Checklist (Don't Repeat)

## Format
- **场景**: 发生了什么
- **后果**: 造成了什么问题
- **解决方案/未来约束**: 如何避免重复

## Entries

- **场景**: OpenClaw 配置中 `agents.defaults.model.primary` 设置为 `opencode/kimi-k2.5`，但 `models.providers` 中只有 `kimi` 和 `kimi-coding` 两个 provider，导致引用不存在的 provider。
- **后果**: 未显式配置 model 的 agent 无法找到对应的 provider，模型调用失败。
- **解决方案/未来约束**: 
  - 修改 model 配置时，必须以 `models.providers` 中定义的 provider ID 为基准
  - Model ref 格式: `{provider}/{model-id}`，必须与 `models.providers.{provider}.models[].id` 匹配
  - 修改后执行 `/model status` 验证当前 session 使用的模型
  - 添加新 provider 时，同步更新所有 agent 的 model 引用

- [占位] 等待填充...
