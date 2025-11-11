#!/bin/bash

# Deploy and Test Script for Vercel

echo "🚀 Deploying to Vercel..."
echo ""

# Deploy
vercel --prod

echo ""
echo "⏳ Waiting 10 seconds for deployment to complete..."
sleep 10

echo ""
echo "🧪 Testing backend health endpoint..."
echo ""

# Test health endpoint
HEALTH_RESPONSE=$(curl -s https://shaed-order-elt.vercel.app/api/health)
echo "Response: $HEALTH_RESPONSE"
echo ""

# Check if it's successful
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Backend is working!"
else
    echo "❌ Backend is not working. Check logs in Vercel Dashboard."
fi

echo ""
echo "🧪 Testing field comparison endpoint..."
echo ""

# Test field comparison
COMPARISON_RESPONSE=$(curl -s "https://shaed-order-elt.vercel.app/api/ford-field-comparison?old_date=2025-11-07&new_date=2025-11-10&limit=5")
echo "Response (first 200 chars): ${COMPARISON_RESPONSE:0:200}..."
echo ""

if echo "$COMPARISON_RESPONSE" | grep -q "data"; then
    echo "✅ Field comparison endpoint is working!"
else
    echo "❌ Field comparison endpoint has issues."
fi

echo ""
echo "✅ Testing complete!"
echo "Frontend: https://shaed-order-elt.vercel.app"
echo "Backend Health: https://shaed-order-elt.vercel.app/api/health"

