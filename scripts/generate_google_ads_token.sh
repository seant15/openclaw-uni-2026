#!/bin/bash
# Generate new Google Ads API refresh token with correct scopes
# Run this on your local machine (not the VPS)

echo "=========================================="
echo "GOOGLE ADS API TOKEN GENERATOR"
echo "=========================================="
echo ""
echo "This script will help you generate a new refresh token"
echo "with the correct Google Ads API scopes."
echo ""
echo "PREREQUISITES:"
echo "1. Google Cloud project with Google Ads API enabled"
echo "2. OAuth 2.0 credentials (Client ID and Secret)"
echo "3. Desktop app or Web app OAuth client configured"
echo ""
echo "STEPS:"
echo ""

# Configuration
CLIENT_ID="${GOOGLE_ADS_CLIENT_ID:-YOUR_CLIENT_ID}"
CLIENT_SECRET="${GOOGLE_ADS_CLIENT_SECRET:-YOUR_CLIENT_SECRET}"

# Google Ads API scope
SCOPE="https://www.googleapis.com/auth/adwords"

echo "1. VISIT THIS URL IN YOUR BROWSER:"
echo ""
echo "https://accounts.google.com/o/oauth2/v2/auth?"
echo "  client_id=${CLIENT_ID}&"
echo "  redirect_uri=urn:ietf:wg:oauth:2.0:oob&"
echo "  scope=${SCOPE}&"
echo "  response_type=code&"
echo "  access_type=offline&"
echo "  prompt=consent"
echo ""
echo "2. SIGN IN WITH YOUR GOOGLE ADS MCC ACCOUNT"
echo "   (the account that manages 6329354566 and 7145222813)"
echo ""
echo "3. COPY THE AUTHORIZATION CODE"
echo ""
echo "4. RUN THIS CURL COMMAND (replace YOUR_AUTH_CODE):"
echo ""
cat << 'EOF'
curl -X POST https://oauth2.googleapis.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=urn:ietf:wg:oauth:2.0:oob"
EOF

echo ""
echo "5. SAVE THE refresh_token FROM THE RESPONSE"
echo ""
echo "6. UPDATE YOUR VPS ENVIRONMENT:"
echo "   export GOOGLE_ADS_REFRESH_TOKEN='YOUR_NEW_REFRESH_TOKEN'"
echo ""
echo "7. TEST THE CONNECTION:"
echo "   /data/workspace/scripts/troubleshoot_google_ads.sh"
