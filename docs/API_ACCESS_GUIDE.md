# Meta & Google Ads API Access Guide

## Meta Marketing API

### Authentication Methods

#### Option 1: User Access Token (Current, Requires Regular Refresh)
```bash
# Get from: https://developers.facebook.com/tools/explorer
# Pros: Quick to generate
# Cons: Expires when user logs out (current issue)
META_ACCESS_TOKEN=EAA...
```

#### Option 2: System User Token (Recommended for Production)
```bash
# 1. Create System User in Business Manager
#    Business Settings → Users → System Users → Add
# 2. Generate Token with ads_read permission
# 3. Token doesn't expire unless revoked
# Pros: Never expires, designed for automation
# Cons: Requires Business Manager setup
```

#### Option 3: App Access Token (Server-to-Server)
```bash
# Format: {app_id}|{app_secret}
# Limited permissions, good for public data
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_ACCESS_TOKEN=${META_APP_ID}|${META_APP_SECRET}
```

### Recommended Approach for UNI
**Use System User Token** - Set up once in Business Manager, never expires

**Steps:**
1. Go to business.facebook.com
2. Settings → Users → System Users
3. Create "UNI Data Sync" system user
4. Assign ad accounts to system user
5. Generate token with `ads_read` permission
6. Store in environment (never expires)

---

## Google Ads API

### Authentication Methods

#### Option 1: OAuth 2.0 Refresh Token (Current)
```python
# Stored in .env:
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_DEVELOPER_TOKEN=

# Refresh token is long-lived but can expire
# Requires re-authentication if revoked
```

#### Option 2: Service Account (Recommended for Server Apps)
```python
# 1. Create service account in Google Cloud Console
# 2. Download JSON key
# 3. Delegate domain-wide authority (if G Suite)
# 4. Use for server-to-server calls

# More reliable, no refresh needed
# Requires: Google Cloud IAM setup
```

### Recommended Approach for UNI
**Keep OAuth 2.0 with Refresh Token** but add token refresh automation

**Why:**
- Already working for dental accounts
- No G Suite requirement
- Well-documented refresh flow

**Improvement:** Add token health check to hourly sync

---

## API Access Comparison

| Method | Setup Complexity | Reliability | Expiration | Best For |
|--------|------------------|-------------|------------|----------|
| **Meta User Token** | Low | Low (logout kills it) | Hours-days | Quick testing |
| **Meta System User** | Medium | High | Never | Production automation |
| **Meta App Token** | Low | Medium | Never | Public data only |
| **Google OAuth** | Medium | Medium | 6 months | Current setup |
| **Google Service** | High | High | Never | Enterprise/G Suite |

---

## Immediate Actions Required

### For Meta (Fix Current Issue)
```bash
# Option A: Quick fix (will expire again)
# 1. Go to https://developers.facebook.com/tools/explorer
# 2. Select UNI app
# 3. Get User Access Token
# 4. Select 'ads_read' permission
# 5. Update .env

# Option B: Permanent fix (recommended)
# 1. Go to business.facebook.com
# 2. Create System User
# 3. Generate permanent token
# 4. Update .env
```

### For Google (Verify Current Setup)
```bash
# Test current tokens
python3 scripts/test_google_token.py

# If expired, regenerate:
# 1. Run scripts/generate_google_ads_token.sh
# 2. Follow OAuth flow
# 3. Copy new refresh token to .env
```

---

## Security Best Practices

### 1. Token Storage
```bash
# NEVER commit tokens to git
.env
.env.local
.env.production

# Use environment variables or secret manager
```

### 2. Token Rotation
```python
# Check token age in sync script
if token_age > 30_days:
    alert("Token expiring soon, refresh needed")
```

### 3. Scope Limitations
```bash
# Meta: Only request needed permissions
ads_read          # Read ad data (sufficient)
ads_management    # Only if modifying campaigns

# Google: Use read-only scopes
https://www.googleapis.com/auth/adwords.readonly
```

### 4. Rate Limiting
```python
# Meta: 200 calls/hour per user
# Google: 10,000 operations/day per account

# Implement backoff
import time
time.sleep(1)  # Between requests
```

---

## Implementation Plan

### Phase 1: Fix Meta (Today)
1. Generate System User token
2. Update .env
3. Test with LEIVIP account
4. Verify data flow

### Phase 2: Verify Google (Today)
1. Test current refresh tokens
2. If expired, regenerate
3. Test with LEIVIP & PROD accounts

### Phase 3: Automation (This Week)
1. Add token health checks to sync
2. Alert on token expiration (7 days warning)
3. Document rotation process

---

## Testing Commands

```bash
# Test Meta token
curl -s "https://graph.facebook.com/v18.0/me?access_token=$META_ACCESS_TOKEN"

# Test Meta ad account access
curl -s "https://graph.facebook.com/v18.0/me/adaccounts?access_token=$META_ACCESS_TOKEN&fields=account_id,name"

# Test Google token
curl -s "https://googleads.googleapis.com/v14/customers:listAccessibleCustomers" \
  -H "Authorization: Bearer $GOOGLE_ADS_ACCESS_TOKEN" \
  -H "developer-token: $GOOGLE_ADS_DEVELOPER_TOKEN"
```

---

## References

- Meta Marketing API: https://developers.facebook.com/docs/marketing-apis
- Google Ads API: https://developers.google.com/google-ads/api/docs/start
- Meta System Users: https://www.facebook.com/business/help/503306463479099
- Google OAuth 2.0: https://developers.google.com/identity/protocols/oauth2
