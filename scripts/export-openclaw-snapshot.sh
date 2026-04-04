#!/usr/bin/env bash
set -euo pipefail

SNAP_DATE="${1:-$(date -u +%F)}"
SRC_BASE="/data/.openclaw"
DST_BASE="/data/workspace/snapshots/openclaw/${SNAP_DATE}"

mkdir -p "${DST_BASE}/openclaw/agents" "${DST_BASE}/openclaw/cron"

# Copy core config
install -m 600 "${SRC_BASE}/openclaw.json" "${DST_BASE}/openclaw/openclaw.json"

# Copy cron job definitions
install -m 600 "${SRC_BASE}/cron/jobs.json" "${DST_BASE}/openclaw/cron/jobs.json"

# Copy agent configs (agent/* only)
for a in clover datie kimi; do
  if [[ -d "${SRC_BASE}/agents/${a}/agent" ]]; then
    mkdir -p "${DST_BASE}/openclaw/agents/${a}"
    # rsync may be unavailable in minimal containers; use cp instead.
    rm -rf "${DST_BASE}/openclaw/agents/${a}/agent"
    mkdir -p "${DST_BASE}/openclaw/agents/${a}/agent"
    cp -a "${SRC_BASE}/agents/${a}/agent/." "${DST_BASE}/openclaw/agents/${a}/agent/"
  fi
done

# Manifest for auditability
{
  echo "snapshot_date=${SNAP_DATE}"
  echo "src_base=${SRC_BASE}"
  echo "dst_base=${DST_BASE}"
  echo "included: openclaw.json, cron/jobs.json, agents/{clover,datie,kimi}/agent/**"
  echo
  echo "files:"
  find "${DST_BASE}" -type f -print0 | sort -z | xargs -0 -I{} sh -c 'printf "%s\t" "{}"; sha256sum "{}" | awk "{print \$1}"'
} > "${DST_BASE}/MANIFEST.txt"

echo "OK: exported snapshot to ${DST_BASE}"
