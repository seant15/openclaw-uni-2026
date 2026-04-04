#!/bin/bash
# protect-critical-files.sh
# 保护关键文件不被误删/误改（容器友好版本）

set -e

echo "[$(date -Iseconds)] Applying critical file protection..."

# 创建只读用户组（如果不存在）
if ! getent group openclaw-ro >/dev/null 2>&1; then
    groupadd openclaw-ro 2>/dev/null || echo "  (groupadd not available, using chmod only)"
fi

# 关键文件列表
CRITICAL_FILES=(
    "/data/workspace/SOUL.md"
    "/data/workspace/USER.md"
    "/data/workspace/IDENTITY.md"
    "/data/workspace/AGENTS.md"
    "/data/workspace/MEMORY.md"
    "/data/workspace/HEARTBEAT.md"
    "/data/workspace/TOOLS.md"
)

# 关键脚本
CRITICAL_SCRIPTS=(
    "/data/workspace/security/scripts/context_auditor.js"
    "/data/workspace/security/scripts/context-hook-server.js"
    "/data/workspace/security/scripts/init-security-hooks.sh"
    "/data/workspace/security/scripts/security-context-audit-trigger.sh"
    "/data/workspace/security/scripts/protect-critical-files.sh"
)

# 关键目录
CRITICAL_DIRS=(
    "/data/workspace/security"
    "/data/workspace/security/scripts"
    "/data/workspace/security/proposals"
    "/data/workspace/security/reference"
    "/data/workspace/snapshots"
)

# 保护关键文件：444（只读）
echo "  Protecting core context files..."
for file in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        chmod 444 "$file" 2>/dev/null && echo "    444 $file" || echo "    ! $file"
    fi
done

# 保护关键脚本：555（只读+可执行）
echo "  Protecting security scripts..."
for file in "${CRITICAL_SCRIPTS[@]}"; do
    if [[ -f "$file" ]]; then
        chmod 555 "$file" 2>/dev/null && echo "    555 $file" || echo "    ! $file"
    fi
done

# 保护关键目录：755 + sticky bit
echo "  Protecting critical directories..."
for dir in "${CRITICAL_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        chmod 755 "$dir" 2>/dev/null || true
        chmod +t "$dir" 2>/dev/null && echo "    +t $dir" || echo "    ! $dir"
    fi
done

# 创建恢复脚本
cat > /data/workspace/security/scripts/unprotect-for-edit.sh << 'EOF'
#!/bin/bash
# 临时解除保护用于编辑
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

echo "Unprotecting files for editing..."
chmod 644 /data/workspace/SOUL.md /data/workspace/USER.md /data/workspace/IDENTITY.md /data/workspace/AGENTS.md /data/workspace/MEMORY.md /data/workspace/HEARTBEAT.md /data/workspace/TOOLS.md 2>/dev/null || true
chmod 755 /data/workspace/security/scripts/*.js /data/workspace/security/scripts/*.sh 2>/dev/null || true
echo "Done. Remember to re-run protect-critical-files.sh after editing!"
EOF
chmod +x /data/workspace/security/scripts/unprotect-for-edit.sh

echo ""
echo "[$(date -Iseconds)] Protection applied."
echo ""
echo "To edit protected files: sudo /data/workspace/security/scripts/unprotect-for-edit.sh"
echo "After editing:         sudo /data/workspace/security/scripts/protect-critical-files.sh"
