---
name: uni-reporting
description: |
  Generate weekly and monthly performance reports for Google Ads and Meta Ads accounts.
  Use when Sean needs to create client reports, performance summaries, or KPI presentations.
  Supports lead generation and e-commerce business types.
  Formats reports in plain English (no markdown) for client communication.
triggers:
  - "create a weekly report for [client]"
  - "generate monthly report for [account]"
  - "show performance summary"
  - "create KPI report"
  - "google ads report"
  - "facebook ads report"
  - "meta ads report"
---

# UNI Reporting System

Generate clear, client-friendly weekly and monthly performance reports for Google Ads and Meta Ads accounts.
All reports use plain English formatting - no markdown symbols like ### or **.

## Workflow Decision Tree

```
START
│
├─ What platform?
│   ├─ Google Ads → Google Ads Report Structure
│   ├─ Facebook/Meta Ads → Facebook Ads Report Structure
│   └─ Both → Combined Report (separate sections)
│
├─ What business type?
│   ├─ Lead Generation → Lead Gen Report Format
│   └─ E-commerce → E-commerce Report Format
│
└─ What timeframe?
    ├─ Weekly → Weekly Report Format
    └─ Monthly → Monthly Report Format
```

## Phase 1: Information Gathering

Required Information:
- Client Name: [name]
- Account Name: [account name]
- Account ID: [account ID]
- Platform: [google | meta | both]
- Report Type: [weekly | monthly]
- Reporting Period: [start date] - [end date]
- Business Type: [lead-gen | ecom]
- Primary Goal: [leads | sales | ROAS]
- Report Recipient: [name/email for personalization]

Performance Data Needed:
- Account-Level Metrics: Impressions, Clicks, CTR, Spend, CPC, CPM, Conversions, CPA, Conversion Value, ROAS
- Campaign-Level Metrics: Top performing, Underperforming, Budget allocation, Key changes
- For Meta Ads: Adset-level (targeting), Ad-level (creative) performance

## Phase 2: Report Structure

CRITICAL FORMATTING RULE: Use plain English only. NO markdown formatting symbols.

DO NOT USE:
- ### for headings
- ** for bold
- Markdown tables with pipes |
- Any markdown symbols

DO USE:
- Plain text headings in ALL CAPS or Title Case
- Simple tables using spaces and dashes
- Clear section breaks with blank lines
- Capitalize important words

### Executive Summary Format

EXECUTIVE SUMMARY

Account Overview
Account Name: [name]
Business: [business name]
Account Status: [Active/Paused/etc]
Reporting Period: [dates]
Total Spend: $[amount]

Performance Highlights ([Timeframe])
Total Impressions: [number]
Total Clicks: [number]
Click-Through Rate (CTR): [X]%
Total Ad Spend: $[amount]
Average Daily Spend: $[amount]
Cost Per Click (CPC): $[amount]
[Conversions/Leads]: [number]
Cost Per [Conversion/Lead] (CPA): $[amount]
[ROAS]: [X]x (e-commerce only)

## Phase 3: Google Ads Campaign Structure

For each major campaign:

Campaign: [Campaign Name]
Campaign ID: [ID]
Status: [Active/Paused]
Daily Budget: $[amount]
Launch Date: [date]

Performance Metrics ([Timeframe])
Impressions: [number]
Clicks: [number]
CTR: [X]%
Spend: $[amount]
CPC: $[amount]
Conversions: [number]
CPA: $[amount]
Conversion Rate: [X]%

Performance Analysis
[2-3 sentence analysis in plain English]

## Phase 4: Meta Ads Structure

Campaign: [Campaign Name]
Campaign ID: [ID]
Status: [Active/Paused]
Daily Budget: $[amount]
Launch Date: [date]
Objective: [OBJECTIVE_TYPE]

Campaign-Level Performance Metrics ([Timeframe])
Impressions: [number]
Clicks: [number]
CTR: [X]%
Spend: $[amount]
CPM: $[amount]
CPC: $[amount]
Reach: [number]
Frequency: [X]
[Conversions/Purchases]: [number]
[Purchase Value]: $[amount]
CPA: $[amount]
ROAS: [X]x

Campaign Performance Analysis
[2-3 sentence analysis]

Top Performing Adsets (Targeting Performance)

Adset 1: [Adset Name / Targeting Description]
- Impressions: [number]
- Clicks: [number]
- CTR: [X]%
- Spend: $[amount]
- Conversions: [number]
- CPA: $[amount]
- ROAS: [X]x
- Targeting: [brief description]

Top Performing Ads (Creative Performance)

Ad 1: [Ad Name / Creative Description]
- Impressions: [number]
- Clicks: [number]
- CTR: [X]%
- Spend: $[amount]
- Conversions: [number]
- CPA: $[amount]
- ROAS: [X]x
- Creative Type: [Static Image/Video/Carousel/etc]
- Creative Notes: [what makes this work]

## Phase 5: Key Metrics Presentation

KEY PERFORMANCE INDICATORS (KPIs)

Primary KPIs
[Main Goal Metric]: [value]
Cost Per [Goal]: $[amount]
[ROAS/ROI]: [X]x (e-commerce)
Conversion Rate: [X]%

Secondary KPIs
Click-Through Rate: [X]%
Cost Per Click: $[amount]
[Other relevant metrics]

Campaign Comparison Table

Metric                Campaign 1    Campaign 2    Campaign 3    Account Avg
Impressions           [X]           [X]           [X]           [X]
CTR                   [X]%          [X]%          [X]%          [X]%
CPC                   $[X]          $[X]          $[X]          $[X]
Conversions           [X]           [X]           [X]           [X]
CPA                   $[X]          $[X]          $[X]          $[X]
ROAS                  [X]x          [X]x          [X]x          [X]x

## Phase 6: Recommendations

RECOMMENDATIONS

Immediate Actions (Week 1)
1. [Action Item]
   Current Situation: [brief description]
   Action Items:
   - [Specific step 1]
   - [Specific step 2]
   - [Specific step 3]

Short-Term Optimizations (Weeks 2-4)
3. [Action Item]
   [Details]

Long-Term Strategic Recommendations
5. [Strategic item]
   [Details]

## Business Type Specifics

### Lead Generation Reports Focus On:
- Lead volume and quality
- Cost per lead (CPL)
- Cost per qualified lead
- Lead source performance
- Form completion rates
- Landing page performance
- Conversion funnel analysis
- Call vs form conversion breakdown

### E-commerce Reports Focus On:
- Return on Ad Spend (ROAS)
- Revenue and purchase value
- Average Order Value (AOV)
- Cost per purchase (CPA)
- Purchase conversion rate
- Cart abandonment metrics
- Product performance
- Shopping vs Search performance
- Funnel metrics

## Meta Ads Hierarchy Understanding

Campaign Level: Budget allocation, objective, overall strategy
Adset Level: Targeting (audiences, demographics, interests, lookalikes)
Ad Level: Creative (images, videos, copy, formats)

Reporting Requirements:
- Always report at Campaign level first
- Then break down top performing Adsets (targeting performance)
- Then break down top performing Ads (creative performance)
- Analyze which targeting strategies work best
- Analyze which creative formats/messages work best

## Quality Checklist

Before Delivery:
- [ ] Report uses plain English only (no markdown symbols)
- [ ] Executive summary clearly states key findings
- [ ] All metrics are accurate and match data source
- [ ] Campaign breakdown includes top 3-5 campaigns
- [ ] For Meta Ads: Includes adset-level and ad-level breakdowns
- [ ] Report format matches business type (lead gen vs e-commerce)
- [ ] Recommendations are specific and actionable
- [ ] Comparison to previous period included
- [ ] Clear spacing makes report scannable
- [ ] Client name and account details correct
- [ ] Reporting period clearly stated
- [ ] Next steps or action items included
- [ ] No unexplained acronyms or technical terms

## Tone Rules

DO:
- Use clear, simple language
- Write in plain English (no markdown formatting)
- Highlight wins prominently
- Be transparent about challenges
- Provide actionable recommendations
- Use clear spacing and section breaks
- Include context (vs previous period)
- Capitalize important words instead of using bold

DON'T:
- Use markdown formatting symbols (###, **, etc.)
- Overwhelm with too many metrics
- Use jargon without explanation
- Hide problems or underperformance
- Make vague recommendations
- Mix weekly and monthly data without clarity
- Use markdown tables (use plain text tables)

## Client Database

Pre-configured client profiles for automated reporting:

### Lumiere Dental
- Account ID: 7145222813
- Platform: Google Ads
- Business Type: Lead Generation
- Brand Owner: Dr. Zukaey
- Report Recipient: Dr. Zukaey
- Report Schedule: Weekly, Thursday 5:00 AM Arizona
- Slack Channel: #kimi-test

### Dental Artistry
- Account ID: 6329354566
- Platform: Google Ads
- Business Type: Lead Generation
- Brand Owner: Riya
- Report Recipient: Riya
- Report Schedule: Weekly, Thursday 5:00 AM Arizona
- Slack Channel: #kimi-test

---
_Last updated: 2026-02-27_
