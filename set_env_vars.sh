#!/bin/bash
# Script to set all environment variables in Vercel
# Run this script to set all required environment variables

set -e

echo "🔐 Setting environment variables in Vercel..."
echo ""

# Read base64 credentials
BASE64_CREDS=$(cat /tmp/gcp_creds_base64.txt | tr -d '\n')

echo "1️⃣  Setting GOOGLE_APPLICATION_CREDENTIALS_JSON..."
echo "$BASE64_CREDS" | vercel env add GOOGLE_APPLICATION_CREDENTIALS_JSON production
echo "$BASE64_CREDS" | vercel env add GOOGLE_APPLICATION_CREDENTIALS_JSON preview
echo "$BASE64_CREDS" | vercel env add GOOGLE_APPLICATION_CREDENTIALS_JSON development

echo ""
echo "2️⃣  Setting PROJECT_ID..."
echo "arcane-transit-357411" | vercel env add PROJECT_ID production
echo "arcane-transit-357411" | vercel env add PROJECT_ID preview
echo "arcane-transit-357411" | vercel env add PROJECT_ID development

echo ""
echo "3️⃣  Setting DOWNLOAD_PROJECT_ID..."
echo "arcane-transit-357411" | vercel env add DOWNLOAD_PROJECT_ID production
echo "arcane-transit-357411" | vercel env add DOWNLOAD_PROJECT_ID preview
echo "arcane-transit-357411" | vercel env add DOWNLOAD_PROJECT_ID development

echo ""
echo "4️⃣  Setting ENVIRONMENT..."
echo "production" | vercel env add ENVIRONMENT production
echo "production" | vercel env add ENVIRONMENT preview
echo "production" | vercel env add ENVIRONMENT development

echo ""
echo "5️⃣  Setting NEXT_PUBLIC_API_URL..."
echo "/api" | vercel env add NEXT_PUBLIC_API_URL production
echo "/api" | vercel env add NEXT_PUBLIC_API_URL preview
echo "/api" | vercel env add NEXT_PUBLIC_API_URL development

echo ""
echo "✅ All environment variables set!"
echo ""
echo "🚀 Next step: Redeploy"
echo "   Run: vercel --prod"
echo ""
echo "🧪 Then test:"
echo "   curl https://shaed-order-elt.vercel.app/api/health"

