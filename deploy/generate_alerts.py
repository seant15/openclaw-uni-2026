"""
Alert Generation Script v2 — Mission Control
=============================================
Rule engine driven by alert_rules table in DB.
Replaces v1 hard-coded rules (under_pacing, over_pacing, zero_spend).

v2 Rules (sourced from alert_rules table):

  Rule 1: roas_above_target   — ROAS > target_roas, spend >= $100   [ecommerce]
  Rule 2: roas_below_target   — ROAS < target_roas, spend >= $100   [ecommerce]
  Rule 3: roas_critical_drop  — ROAS < target_roas × 0.5, spend >= $50  [ecommerce]
  Rule 4: cpa_above_target    — CPA > target_cpa, conversions >= 3  [lead_gen]
  Rule 5: zero_spend_technical — $0 spend for 6+ consecutive hours 8AM-8PM, avg_daily >= $20
  Rule 6: metrics_anomaly     — CTR/CPC/CPM deviate >30-50% from 7d avg

Dedup: one alert per (client_id, platform, ad_account_id, alert_type) per cooldown_hours window
Cooldown: per-rule cooldown_hours from conditions JSON

Run options:
  python generate_alerts.py
  python generate_alerts.py --dry-run
  python generate_alerts.py --client "Lumiere"
  python generate_alerts.py --date 2026-04-05 --hour 14

Cron (runs 10 min after hourly sync):
  10 * * * *  python generate_alerts.py

Author: OpenClaw Team
Updated: 2026-04-05
"""

import os
import sys
import argparse
from datetime import datetime, date, timezone, timedelta
from typing import List, Dict, Optional, Any

from supabase import create_client
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# ── Env ───────────────────────────────────────────────────────────────────────
_local_env = os.path.join(os.path.dirname(__file__), ".env")
_dev_env   = os.path.join(os.path.dirname(__file__), "..", "Concept 032026", "uni-mission-control", ".env")
load_dotenv(_local_env if os.path.exists(_local_env) else _dev_env)

URL         = os.getenv("VITE_SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
sb          = create_client(URL, SERVICE_KEY)

ACTIVE_HOURS_START = 8
ACTIVE_HOURS_END   = 20


# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


# ── Data Fetchers ─────────────────────────────────────────────────────────────

def get_active_clients() -> List[Dict]:
    """Fetch all clients with ad accounts, excluding Travorio."""
    result = sb.table("clients").select(
        "id, name, timezone, business_type, target_roas, target_cpa, "
        "google_ads_customer_id, meta_ad_account_id, meta_ad_account_id_2"
    ).execute()
    out = []
    for c in (result.data or []):
        if c.get("name") == "Travorio":
            continue
        if any([c.get("google_ads_customer_id"), c.get("meta_ad_account_id"),
                c.get("meta_ad_account_id_2")]):
            out.append(c)
    return out


def get_active_rules() -> List[Dict]:
    """Fetch all active alert rules from DB."""
    result = sb.table("alert_rules").select("*").eq("is_active", True).order("display_order").execute()
    return result.data or []


def get_baselines(client_id: str) -> List[Dict]:
    """Fetch account_daily_baselines view rows for this client."""
    result = sb.table("account_daily_baselines").select("*").eq("client_id", client_id).execute()
    return result.data or []


def get_today_hourly(client_id: str, target_date: date) -> List[Dict]:
    """Today's real hourly_performance rows (cost/impressions/clicks/conversions are hourly deltas)."""
    result = sb.table("hourly_performance") \
        .select("platform, ad_account_id, hour, account_local_hour, cost, impressions, "
                "clicks, link_clicks, conversions, revenue, ctr, link_ctr, roas, is_real_data") \
        .eq("client_id", client_id) \
        .eq("date", str(target_date)) \
        .order("hour", desc=False) \
        .execute()
    return result.data or []


def get_7day_metric_avg(client_id: str, platform: str, ad_account_id: str,
                         metric: str, target_date: date) -> Optional[float]:
    """
    Compute 7-day average of a daily metric from daily_performance.
    Used for metrics_anomaly rule. Returns None if column doesn't exist.
    """
    since = (target_date - timedelta(days=7)).isoformat()
    try:
        result = sb.table("daily_performance") \
            .select(f"{metric}") \
            .eq("client_id", client_id) \
            .eq("platform", platform) \
            .eq("ad_account_id", ad_account_id) \
            .gte("date", since) \
            .lt("date", str(target_date)) \
            .execute()
        vals = [float(r[metric]) for r in (result.data or []) if r.get(metric) is not None and float(r[metric]) > 0]
        return sum(vals) / len(vals) if vals else None
    except Exception:
        return None  # Column doesn't exist in this table — skip metric


def alert_exists_within_cooldown(client_id: str, ad_account_id: str,
                                  platform: str, alert_type: str,
                                  cooldown_hours: int) -> bool:
    """
    Check if an alert of this type was already fired within the cooldown window.
    Includes 'snoozed' status so we don't re-fire on snoozed alerts.
    """
    since = (datetime.now(timezone.utc) - timedelta(hours=cooldown_hours)).isoformat()
    result = sb.table("alerts") \
        .select("id") \
        .eq("client_id", client_id) \
        .eq("account_id", ad_account_id) \
        .eq("platform", platform) \
        .eq("alert_type", alert_type) \
        .in_("status", ["new", "in_progress", "snoozed"]) \
        .gte("created_at", since) \
        .execute()
    return bool(result.data)


# ── Alert Builder ─────────────────────────────────────────────────────────────

def build_alert(client: Dict, baseline: Dict, alert_type: str, severity: str,
                message: str, metric_name: str, metric_value: Any,
                threshold: Any, target_date: date,
                triggered_hour: Optional[int] = None) -> Dict:
    dedup_key = f"{client['id']}:{baseline['platform']}:{alert_type}:{target_date}"
    return {
        "client_id":      client["id"],
        "account_name":   client["name"],
        "account_id":     baseline["ad_account_id"],
        "platform":       baseline["platform"],
        "alert_type":     alert_type,
        "severity":       severity,
        "message":        message,
        "metric_name":    metric_name,
        "metric_value":   float(metric_value) if metric_value is not None else None,
        "metric_change":  None,
        "threshold":      float(threshold) if threshold is not None else None,
        "triggered_date": str(target_date),
        "triggered_hour": triggered_hour,
        "status":         "new",
        "dedup_key":      dedup_key,
        "is_read":        False,
        "resolved":       False,
        "source":         "rule_engine",
    }


# ── Rule Evaluators ───────────────────────────────────────────────────────────

def evaluate_roas_rules(client: Dict, baseline: Dict, hourly_rows: List[Dict],
                         rules: List[Dict], target_date: date,
                         current_local_hour: int) -> List[Dict]:
    """
    Rules: roas_above_target, roas_below_target, roas_critical_drop
    Only fires for ecommerce clients with target_roas set.
    Uses today's cumulative revenue/cost from hourly rows.
    """
    if client.get("business_type") != "ecommerce":
        return []
    target_roas = client.get("target_roas")
    if not target_roas or float(target_roas) <= 0:
        return []

    target_roas = float(target_roas)
    account_rows = [r for r in hourly_rows
                    if r["platform"] == baseline["platform"]
                    and r["ad_account_id"] == baseline["ad_account_id"]]

    today_cost    = sum(float(r.get("cost", 0) or 0) for r in account_rows)
    today_revenue = sum(float(r.get("revenue", 0) or 0) for r in account_rows)

    if today_cost <= 0:
        return []

    today_roas = today_revenue / today_cost
    results    = []

    roas_rules = {r["template_type"]: r for r in rules
                  if r["template_type"] in ("roas_above_target", "roas_below_target", "roas_critical_drop")}

    # roas_above_target
    if rule := roas_rules.get("roas_above_target"):
        cond = rule["conditions"]
        min_spend    = float(cond.get("min_spend", 100))
        cooldown     = int(cond.get("cooldown_hours", 24))
        if today_cost >= min_spend and today_roas > target_roas:
            if not alert_exists_within_cooldown(client["id"], baseline["ad_account_id"],
                                                baseline["platform"], "roas_above_target", cooldown):
                pct_above = (today_roas / target_roas - 1) * 100
                results.append(build_alert(
                    client, baseline,
                    alert_type   = "roas_above_target",
                    severity     = rule["severity"],
                    message      = (f"ROAS {today_roas:.2f}x vs target {target_roas:.1f}x "
                                    f"(+{pct_above:.0f}% above target). "
                                    f"Scale opportunity — consider +10-20% budget. "
                                    f"Spend today: ${today_cost:.0f}."),
                    metric_name  = "ROAS",
                    metric_value = round(today_roas, 2),
                    threshold    = target_roas,
                    target_date  = target_date,
                    triggered_hour = current_local_hour,
                ))

    # roas_critical_drop — check before roas_below_target (more severe, mutually exclusive)
    fired_critical = False
    if rule := roas_rules.get("roas_critical_drop"):
        cond = rule["conditions"]
        min_spend       = float(cond.get("min_spend", 50))
        threshold_ratio = float(cond.get("threshold_ratio", 0.5))
        cooldown        = int(cond.get("cooldown_hours", 6))
        critical_thresh = target_roas * threshold_ratio
        if today_cost >= min_spend and today_roas < critical_thresh:
            if not alert_exists_within_cooldown(client["id"], baseline["ad_account_id"],
                                                baseline["platform"], "roas_critical_drop", cooldown):
                pct_below = (1 - today_roas / target_roas) * 100
                results.append(build_alert(
                    client, baseline,
                    alert_type   = "roas_critical_drop",
                    severity     = rule["severity"],
                    message      = (f"ROAS CRITICAL {today_roas:.2f}x — "
                                    f"{pct_below:.0f}% below target {target_roas:.1f}x. "
                                    f"IMMEDIATE ACTION REQUIRED. "
                                    f"Check campaigns, offers, landing pages. Spend: ${today_cost:.0f}."),
                    metric_name  = "ROAS",
                    metric_value = round(today_roas, 2),
                    threshold    = target_roas,
                    target_date  = target_date,
                    triggered_hour = current_local_hour,
                ))
                fired_critical = True

    # roas_below_target — only if critical didn't fire (avoid double alerting)
    if not fired_critical:
        if rule := roas_rules.get("roas_below_target"):
            cond = rule["conditions"]
            min_spend = float(cond.get("min_spend", 100))
            cooldown  = int(cond.get("cooldown_hours", 12))
            if today_cost >= min_spend and today_roas < target_roas:
                if not alert_exists_within_cooldown(client["id"], baseline["ad_account_id"],
                                                    baseline["platform"], "roas_below_target", cooldown):
                    pct_below = (1 - today_roas / target_roas) * 100
                    results.append(build_alert(
                        client, baseline,
                        alert_type   = "roas_below_target",
                        severity     = rule["severity"],
                        message      = (f"ROAS {today_roas:.2f}x below target {target_roas:.1f}x "
                                        f"(-{pct_below:.0f}%). Do NOT increase budget. "
                                        f"Monitor closely. Spend: ${today_cost:.0f}."),
                        metric_name  = "ROAS",
                        metric_value = round(today_roas, 2),
                        threshold    = target_roas,
                        target_date  = target_date,
                        triggered_hour = current_local_hour,
                    ))

    return results


def evaluate_cpa_rule(client: Dict, baseline: Dict, hourly_rows: List[Dict],
                       rules: List[Dict], target_date: date,
                       current_local_hour: int) -> List[Dict]:
    """
    Rule: cpa_above_target
    Only fires for lead_gen clients with target_cpa set.
    """
    if client.get("business_type") != "lead_gen":
        return []
    target_cpa = client.get("target_cpa")
    if not target_cpa or float(target_cpa) <= 0:
        return []

    target_cpa = float(target_cpa)
    rule = next((r for r in rules if r["template_type"] == "cpa_above_target"), None)
    if not rule:
        return []

    cond = rule["conditions"]
    min_conversions = int(cond.get("min_conversions", 3))
    cooldown        = int(cond.get("cooldown_hours", 12))

    account_rows = [r for r in hourly_rows
                    if r["platform"] == baseline["platform"]
                    and r["ad_account_id"] == baseline["ad_account_id"]]

    today_cost = sum(float(r.get("cost", 0) or 0) for r in account_rows)
    today_conv = sum(float(r.get("conversions", 0) or 0) for r in account_rows)

    if today_conv < min_conversions or today_cost <= 0:
        return []

    today_cpa = today_cost / today_conv
    if today_cpa <= target_cpa:
        return []

    if alert_exists_within_cooldown(client["id"], baseline["ad_account_id"],
                                     baseline["platform"], "cpa_above_target", cooldown):
        return []

    pct_above = (today_cpa / target_cpa - 1) * 100
    return [build_alert(
        client, baseline,
        alert_type   = "cpa_above_target",
        severity     = rule["severity"],
        message      = (f"CPA ${today_cpa:.0f} is {pct_above:.0f}% above target ${target_cpa:.0f}. "
                        f"{int(today_conv)} conversions today at ${today_cost:.0f} spend. "
                        f"Review targeting and creative performance."),
        metric_name  = "CPA",
        metric_value = round(today_cpa, 2),
        threshold    = target_cpa,
        target_date  = target_date,
        triggered_hour = current_local_hour,
    )]


def evaluate_zero_spend_technical(client: Dict, baseline: Dict, hourly_rows: List[Dict],
                                   rules: List[Dict], target_date: date,
                                   current_local_hour: int) -> List[Dict]:
    """
    Rule: zero_spend_technical
    $0 spend for 6+ consecutive hours during business hours (8-20 local).
    Only fires if account's avg daily spend >= $20 (active account).
    """
    rule = next((r for r in rules if r["template_type"] == "zero_spend_technical"), None)
    if not rule:
        return []

    cond = rule["conditions"]
    duration_hours      = int(cond.get("duration_hours", 6))
    min_expected_daily  = float(cond.get("min_expected_daily_spend", 20))
    min_hour            = int(cond.get("time_constraints", {}).get("min_hour_of_day", 8))
    max_hour            = int(cond.get("time_constraints", {}).get("max_hour_of_day", 20))
    cooldown            = int(cond.get("cooldown_hours", 12))

    if current_local_hour < min_hour or current_local_hour > max_hour:
        return []

    avg_daily = float(baseline.get("avg_daily_cost") or 0)
    if avg_daily < min_expected_daily:
        return []  # Account normally doesn't spend much — not a technical issue

    account_rows = sorted(
        [r for r in hourly_rows
         if r["platform"] == baseline["platform"]
         and r["ad_account_id"] == baseline["ad_account_id"]],
        key=lambda r: r.get("account_local_hour", r.get("hour", 0))
    )

    if not account_rows:
        return []

    # Count consecutive zero-spend hours at the END of available data
    consecutive_zero = 0
    for row in reversed(account_rows):
        if float(row.get("cost", 0) or 0) == 0:
            consecutive_zero += 1
        else:
            break

    if consecutive_zero < duration_hours:
        return []

    if alert_exists_within_cooldown(client["id"], baseline["ad_account_id"],
                                     baseline["platform"], "zero_spend_technical", cooldown):
        return []

    return [build_alert(
        client, baseline,
        alert_type   = "zero_spend_technical",
        severity     = rule["severity"],
        message      = (f"Zero spend for {consecutive_zero} consecutive hours "
                        f"(avg ${avg_daily:.0f}/day account). "
                        f"Check account status, billing, and campaign status."),
        metric_name  = "Consecutive zero-spend hours",
        metric_value = consecutive_zero,
        threshold    = duration_hours,
        target_date  = target_date,
        triggered_hour = current_local_hour,
    )]


def evaluate_metrics_anomaly(client: Dict, baseline: Dict, hourly_rows: List[Dict],
                              rules: List[Dict], target_date: date,
                              current_local_hour: int) -> List[Dict]:
    """
    Rule: metrics_anomaly
    Fires when CTR, CPC, or CPM deviate significantly from 7-day average.
    Low severity — FYI for media buyers.
    """
    rule = next((r for r in rules if r["template_type"] == "metrics_anomaly"), None)
    if not rule:
        return []

    cond = rule["conditions"]
    metrics_config  = cond.get("metrics", [])
    min_impressions = int(cond.get("min_impressions", 1000))
    cooldown        = int(cond.get("cooldown_hours", 8))

    account_rows = [r for r in hourly_rows
                    if r["platform"] == baseline["platform"]
                    and r["ad_account_id"] == baseline["ad_account_id"]]

    today_impr   = sum(int(r.get("impressions", 0) or 0) for r in account_rows)
    today_clicks = sum(int(r.get("clicks", 0) or 0) for r in account_rows)
    today_cost   = sum(float(r.get("cost", 0) or 0) for r in account_rows)

    if today_impr < min_impressions:
        return []

    today_metrics = {
        "ctr": (today_clicks / today_impr) if today_impr > 0 else 0,
        "cpc": (today_cost / today_clicks) if today_clicks > 0 else 0,
        "cpm": (today_cost / today_impr * 1000) if today_impr > 0 else 0,
    }

    anomalies = []
    for mc in metrics_config:
        metric    = mc["metric"]
        threshold = float(mc["threshold"]) / 100  # threshold is a percent (e.g. 30 = 30%)
        direction = mc.get("direction", "under")   # "under" = drop, "over" = spike

        avg_val = get_7day_metric_avg(client["id"], baseline["platform"],
                                       baseline["ad_account_id"], metric, target_date)
        if not avg_val or avg_val <= 0:
            continue

        today_val = today_metrics.get(metric, 0)
        if today_val <= 0:
            continue

        ratio = today_val / avg_val
        if direction == "under" and ratio < (1 - threshold):
            pct = (1 - ratio) * 100
            anomalies.append(f"{metric.upper()} -{pct:.0f}% vs 7d avg ({today_val:.4f} vs {avg_val:.4f})")
        elif direction == "over" and ratio > (1 + threshold):
            pct = (ratio - 1) * 100
            anomalies.append(f"{metric.upper()} +{pct:.0f}% vs 7d avg ({today_val:.4f} vs {avg_val:.4f})")

    if not anomalies:
        return []

    if alert_exists_within_cooldown(client["id"], baseline["ad_account_id"],
                                     baseline["platform"], "metrics_anomaly", cooldown):
        return []

    return [build_alert(
        client, baseline,
        alert_type   = "metrics_anomaly",
        severity     = rule["severity"],
        message      = f"Metrics anomaly detected: {'; '.join(anomalies)}. Review for optimization opportunities.",
        metric_name  = "Metrics",
        metric_value = None,
        threshold    = None,
        target_date  = target_date,
        triggered_hour = current_local_hour,
    )]


# ── Orchestrator ──────────────────────────────────────────────────────────────

def process_client(client: Dict, rules: List[Dict], target_date: date,
                   current_utc_hour: int, dry_run: bool = False) -> Dict:
    result = {"client": client["name"], "alerts": [], "skipped": False, "reason": ""}

    baselines = get_baselines(client["id"])
    if not baselines:
        result["skipped"] = True
        result["reason"]  = "No baseline data"
        log(f"  SKIP {client['name']}: {result['reason']}", "WARNING")
        return result

    hourly_rows = get_today_hourly(client["id"], target_date)

    # Resolve local hour
    account_tz = client.get("timezone", "America/New_York")
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(account_tz)
        now_local         = datetime.now(timezone.utc).astimezone(tz)
        current_local_hour = now_local.hour
    except Exception:
        current_local_hour = current_utc_hour

    if current_local_hour < ACTIVE_HOURS_START or current_local_hour > ACTIVE_HOURS_END:
        result["skipped"] = True
        result["reason"]  = f"Outside active hours ({current_local_hour}:00 local)"
        log(f"  SKIP {client['name']}: {result['reason']}")
        return result

    all_alerts: List[Dict] = []

    for baseline in baselines:
        log(f"    [{baseline['platform']} / {baseline['ad_account_id']}] "
            f"avg ${float(baseline.get('avg_daily_cost', 0)):.0f}/day")

        all_alerts.extend(evaluate_roas_rules(
            client, baseline, hourly_rows, rules, target_date, current_local_hour))

        all_alerts.extend(evaluate_cpa_rule(
            client, baseline, hourly_rows, rules, target_date, current_local_hour))

        all_alerts.extend(evaluate_zero_spend_technical(
            client, baseline, hourly_rows, rules, target_date, current_local_hour))

        all_alerts.extend(evaluate_metrics_anomaly(
            client, baseline, hourly_rows, rules, target_date, current_local_hour))

    for alert in all_alerts:
        log(f"  [{alert['severity'].upper()}] {alert['alert_type']}: {alert['message'][:100]}…")
        if not dry_run:
            try:
                sb.table("alerts").insert(alert).execute()
                result["alerts"].append(alert)
            except Exception as e:
                log(f"  INSERT ERROR: {e}", "ERROR")
        else:
            result["alerts"].append(alert)

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print alerts without inserting")
    parser.add_argument("--date",    type=str,  help="Override date (YYYY-MM-DD)")
    parser.add_argument("--hour",    type=int,  help="Override UTC hour")
    parser.add_argument("--client",  type=str,  help="Filter to a single client name")
    args = parser.parse_args()

    target_date       = (datetime.strptime(args.date, "%Y-%m-%d").date()
                         if args.date else datetime.now(timezone.utc).date())
    current_utc_hour  = args.hour if args.hour is not None else datetime.now(timezone.utc).hour

    log("=" * 70)
    log(f"ALERT GENERATION v2 — {target_date} UTC hour={current_utc_hour}"
        + (" [DRY RUN]" if args.dry_run else ""))
    log("=" * 70)

    rules   = get_active_rules()
    clients = get_active_clients()

    log(f"Rules loaded: {len(rules)} active")
    log(f"Clients: {len(clients)}")

    if args.client:
        clients = [c for c in clients if args.client.lower() in c["name"].lower()]

    total = 0
    for i, client in enumerate(clients, 1):
        log(f"\n[{i}/{len(clients)}] {client['name']} "
            f"[{client.get('business_type', 'ecommerce')}]"
            f"{' ROAS target: ' + str(client.get('target_roas')) if client.get('target_roas') else ''}"
            f"{' CPA target: $' + str(client.get('target_cpa')) if client.get('target_cpa') else ''}")
        r = process_client(client, rules, target_date, current_utc_hour, args.dry_run)
        total += len(r["alerts"])

    log(f"\nDONE — {total} alerts {'(dry run, not inserted)' if args.dry_run else 'inserted'}")


if __name__ == "__main__":
    main()
