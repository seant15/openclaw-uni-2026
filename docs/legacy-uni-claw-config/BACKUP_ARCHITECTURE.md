# VPS 存储与备份架构文档

## 1. Repo ↔ 服务器路径映射

| GitHub Repo | 服务器路径 | 用途 | 大小(约) |
|-------------|-----------|------|---------|
| `seant15/openclaw` | `/data/workspace/openclaw-sean-fork` | OpenClaw 主仓库fork | ~200MB |
| `seant15/openclaw-uni-2026` | `/data/workspace/uni-openclaw-infra` | UNI专属基础设施 | ~150MB |
| `seant15/uni-mission-control` | `/data/workspace/mission-control` | Mission Control系统 | ~100MB |

**本地工作区**: `/data/workspace` (941MB总计，包含上述repo + agents/ memory/ skills/ 等)

**OpenClaw配置**: `/data/.openclaw` (620MB，包含agents配置、openclaw.json、工作区快照等)

---

## 2. 备份机制

### 2.1 主备份脚本
- **路径**: `/data/workspace/scripts/openclaw-full-backup.sh`
- **功能**: 
  - 备份 `/data/.openclaw` (配置 + agents)
  - 备份 `/data/workspace` (repos + 工作文件)
  - 压缩 (zstd) + 加密 (age) + 上传 (rclone)
- **目标**: Google Drive Shared Drive (`OpenClawBackups`)
- **频率**: 每天 02:15 UTC (cron)

### 2.2 Cron配置
```
15 2 * * * root /data/workspace/scripts/openclaw-full-backup.sh >> /data/.openclaw/logs/openclaw-backup-cron.log 2>&1
```

配置文件: `/data/workspace/cron/openclaw-backup.cron`

### 2.3 备份保留策略
- **云端**: 14天滚动删除
- **本地**: 7天滚动删除
- **日志**: 30天滚动删除

### 2.4 加密密钥
- **位置**: `/data/.openclaw/credentials/backup/`
- **文件**:
  - `age.key` - 私钥 (root-only, 600权限)
  - `age.recipient` - 公钥
- **⚠️ 重要**: 如果私钥丢失，备份将无法解密

---

## 3. 存储使用情况

```
Filesystem      Size  Used  Avail  Use%
/dev/sda1        97G   36G    62G   37%

关键目录:
/data/workspace              941MB  (repos + 工作文件)
/data/.openclaw              620MB  (OpenClaw配置)
/data/openclaw-control-center  59MB  (控制面板)
```

---

## 4. 恢复流程

### 4.1 从Google Drive恢复
```bash
# 1. 列出可用备份
rclone ls gdrive-backup:OpenClawBackups/{hostname}/ --config /data/.config/rclone/rclone.conf

# 2. 下载备份文件
rclone copy gdrive-backup:OpenClawBackups/{hostname}/{backup-file}.age /tmp/ --config /data/.config/rclone/rclone.conf

# 3. 解密
age -d -i /data/.openclaw/credentials/backup/age.key -o /tmp/backup.tar.zst /tmp/{backup-file}.age

# 4. 解压
zstd -d /tmp/backup.tar.zst -o /tmp/backup.tar
tar -xf /tmp/backup.tar -C /data/destination
```

### 4.2 从本地恢复
```bash
# 本地备份位置
/data/.openclaw/backups/

# 解密并解压
cd /data/.openclaw/backups
age -d -i /data/.openclaw/credentials/backup/age.key -o backup.tar.zst {backup-file}.age
zstd -d backup.tar.zst -o backup.tar
tar -xf backup.tar -C /data/destination
```

---

## 5. 监控与告警

- **成功通知**: Slack DM to Sean
- **失败通知**: Slack DM to Sean (带错误步骤)
- **日志位置**: `/data/.openclaw/logs/openclaw-backup-*.log`

---

## 6. 待办/改进项

- [ ] 验证cronjob是否正常运行（上次备份是3月29日，需检查）
- [ ] 考虑添加数据库备份（Supabase已有自动备份，但可导出schema）
- [ ] 考虑添加Docker volumes备份（如果有重要容器数据）

---

*最后更新: 2026-04-06*
