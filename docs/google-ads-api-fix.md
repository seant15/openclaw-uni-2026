# Google Ads API Access Fix

## Problem Identified

The OAuth refresh token was generated **without the Google Ads API scope** (`https://www.googleapis.com/auth/adwords`).

**Symptoms:**
- Token refresh works ✓
- API returns 404 for all accounts ✗
- Cannot access MCC or client accounts

## Solution Overview

You need to re-authorize with the **correct Google Ads API scope**. This requires:

1. **Google Cloud Project** with Google Ads API enabled
2. **OAuth 2.0 credentials** (Desktop app type recommended)
3. **New refresh token** with the adwords scope

---

## Step-by-Step Fix

### Step 1: Verify Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Select your project (or create one)
3. Navigate to **"APIs & Services" → "Library"**
4. Search for **"Google Ads API"**
5. Click **"Enable"** if not already enabled

### Step 2: Create OAuth 2.0 Credentials

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"+ Create Credentials" → "OAuth client ID"**
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: "UNI Google Ads Reports"
   - User support email: your email
   - Developer contact: your email
   - Scopes: Add `https://www.googleapis.com/auth/adwords`
   - Test users: Add your email
4. Create OAuth client ID:
   - Application type: **Desktop app** (recommended)
   - Name: "UNI Reports Desktop"
5. **Copy the Client ID and Client Secret**

### Step 3: Generate New Refresh Token

**Option A: Using the script on your local machine**

```bash
# On your local machine (Mac/PC), not the VPS
export GOOGLE_ADS_CLIENT_ID='your-client-id.apps.googleusercontent.com'
export GOOGLE_ADS_CLIENT_SECRET='your-client-secret'
./generate_google_ads_token.sh
```

**Option B: Manual process**

1. **Open this URL in your browser** (replace YOUR_CLIENT_ID):
   ```
   https://accounts.google.com/o/oauth2/v2/auth?
     client_id=YOUR_CLIENT_ID
     &redirect_uri=urn:ietf:wg:oauth:2.0:oob
     &scope=https://www.googleapis.com/auth/adwords
     &response_type=code
     &access_type=offline
     &prompt=consent
   ```

2. **Sign in with your Google Ads MCC account** (2823334378)

3. **Grant permissions** when prompted

4. **Copy the authorization code**

5. **Exchange for refresh token:**
   ```bash
   curl -X POST https://oauth2.googleapis.com/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code" \
     -d "code=YOUR_AUTH_CODE" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "redirect_uri=urn:ietf:wg:oauth:2.0:oob"
   ```

6. **Save the `refresh_token`** from the response

### Step 4: Update VPS Environment

SSH into your VPS and update the environment:

```bash
# Update the refresh token
export GOOGLE_ADS_REFRESH_TOKEN='YOUR_NEW_REFRESH_TOKEN'

# Update Coolify environment variables
# Go to: https://coolify.unippc24.com
# Navigate to your OpenClaw service
# Update environment variables:
#   GOOGLE_ADS_REFRESH_TOKEN = your-new-token
#   GOOGLE_ADS_CLIENT_ID = your-client-id
#   GOOGLE_ADS_CLIENT_SECRET = your-client-secret

# Restart the service to apply changes
```

### Step 5: Test the Connection

```bash
/data/workspace/scripts/troubleshoot_google_ads.sh
```

Expected output:
```
✓ MCC account accessible
✓ Dental Artistry account accessible  
✓ Lumiere Dental account accessible
✓ ALL CHECKS PASSED
```

---

## Alternative: Service Account (No Refresh Token)

If OAuth is problematic, use a **Service Account** with domain-wide delegation:

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Create service account: "uni-reports@your-project.iam.gserviceaccount.com"
3. Grant role: "Google Ads API User"
4. Create key → Download JSON
5. In Google Ads MCC: Add service account email with "Standard" access
6. Use service account credentials instead of OAuth

---

## Quick Checklist

- [ ] Google Ads API enabled in Google Cloud
- [ ] OAuth 2.0 Desktop app credentials created
- [ ] OAuth consent screen configured with adwords scope
- [ ] New refresh token generated with correct scope
- [ ] VPS environment variables updated
- [ ] Connection test passes

---

## Need Help?

If you get stuck:

1. **Check Google Ads API Center**: https://ads.google.com/aw/apicenter
2. **Verify MCC access**: https://ads.google.com/aw/accounts
3. **Test in OAuth Playground**: https://developers.google.com/oauthplayground
   - Select scope: `https://www.googleapis.com/auth/adwords`
   - Exchange for refresh token

Once this is fixed, the automated Thursday reports will work seamlessly.
