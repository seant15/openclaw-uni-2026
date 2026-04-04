# Agents Handbook (Reference)

Moved out of `AGENTS.md` to keep fixed context thin. This is still authoritative, but should be loaded on-demand.

## Heartbeats vs Cron
Use heartbeat when:
- Multiple checks can be batched together
- Timing can drift (every ~30 min is fine)
- You want fewer API calls by combining periodic checks

Use cron when:
- Exact timing matters
- Task needs isolation from main session history
- Output should deliver directly to a channel without main session involvement

## Reactions etiquette
Use a single emoji reaction to acknowledge when a full reply is unnecessary.

## Memory maintenance
Periodically review recent daily logs and distill durable items into MEMORY.md.

## Platform formatting notes
- Discord/WhatsApp: avoid markdown tables; use bullet lists
- Discord links: wrap with <> to suppress embeds
