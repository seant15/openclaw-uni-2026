# Local machine paths

Canonical sandbox: `D:\AI SPACE SANDBOX`

| What | Path |
|------|------|
| This repo | `workspaces\openclaw-ops\repos\openclaw-uni-2026` |
| VPS mirror | `workspaces\openclaw-ops\mirrors\vps-openclaw` |
| Marketing / ads | `workspaces\marketing-stack\repos\ads-data-sync` |
| Mission Control UI | `workspaces\marketing-stack\repos\mission-control` |
| Media buyer training (GHL HTML + quizzes) | `052026 AI AGENTIC OS\AIS-UNI-OS\training\` |
| Media buyer docs / webhook setup | `052026 AI AGENTIC OS\AIS-UNI-OS\docs\` |
| PPC OS training memory (canonical) | `052026 AI AGENTIC OS\memory\reference_uni-ppc-os-training-system.md` |
| Git repo for above | `052026 AI AGENTIC OS` → `github.com/seant15/ai-agentic-os` (`main`) |

## Media buyer training sync (canonical)

Edit and commit from `D:\AI SPACE SANDBOX\052026 AI AGENTIC OS` — not OPENCLAW mirrors.

| GHL path | Source file |
|----------|-------------|
| `/media-buyer` | `AIS-UNI-OS/training/ppc-os-portal.html` |
| `/media-buyer/meta` | `AIS-UNI-OS/training/ppc-os-portal-meta.html` |
| `/media-buyer/google` | `AIS-UNI-OS/training/ppc-os-portal-google.html` |
| `/media-buyer/meta/quiz` | `AIS-UNI-OS/training/media-buyer-quiz-meta.html` |
| `/media-buyer/google/quiz` | `AIS-UNI-OS/training/media-buyer-quiz-google.html` |

Publish checklist: `AIS-UNI-OS/docs/GHL-Media-Buyer-Publish-20260705.md`. Webhook: `AIS-UNI-OS/docs/Interactive-Quiz-GHL-Webhook-Setup.md`.

## Mission Control sync (canonical)

Edit, commit, and push **only** from the D: path above — not from `mirrors/vps-openclaw/.../mission-control`.

| Item | Value |
|------|-------|
| GitHub | `seant15/uni-mission-control` |
| Branch | **`master`** (production + Vercel) |
| Deploy | Vercel auto-deploy on push to `master` |
| VPS mirror | `mirrors/vps-openclaw/volumes/workspace/mission-control` — stale snapshot; do not edit for product work |

Full checklist: `D:\AI SPACE SANDBOX\MIGRATION_STATUS.md`
