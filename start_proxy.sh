#!/usr/bin/env zsh

# Start Cloud SQL Proxy for database access
# Run this in a separate terminal and keep it running

echo "============================================================"
echo "Starting Cloud SQL Proxy"
echo "============================================================"
echo ""
echo "Instance: arcane-transit-357411:us-central1:order-management"
echo "Port: 5555"
echo ""
echo "Keep this terminal open while using the database."
echo "Press Ctrl+C to stop the proxy."
echo ""
echo "============================================================"
echo ""

# Try to find cloud-sql-proxy in different locations
if command -v cloud-sql-proxy &> /dev/null; then
    cloud-sql-proxy arcane-transit-357411:us-central1:order-management -p 5555
elif command -v cloud_sql_proxy &> /dev/null; then
    cloud_sql_proxy arcane-transit-357411:us-central1:order-management -p 5555
elif [ -f "./cloud-sql-proxy" ]; then
    ./cloud-sql-proxy arcane-transit-357411:us-central1:order-management -p 5555
elif [ -f "/usr/local/bin/cloud-sql-proxy" ]; then
    /usr/local/bin/cloud-sql-proxy arcane-transit-357411:us-central1:order-management -p 5555
elif [ -f "/opt/homebrew/bin/cloud-sql-proxy" ]; then
    /opt/homebrew/bin/cloud-sql-proxy arcane-transit-357411:us-central1:order-management -p 5555
else
    echo "✗ Error: cloud-sql-proxy not found!"
    echo ""
    echo "Please install it first:"
    echo ""
    echo "Option 1: Download directly"
    echo "  curl -o cloud-sql-proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64"
    echo "  chmod +x cloud-sql-proxy"
    echo "  sudo mv cloud-sql-proxy /usr/local/bin/"
    echo ""
    echo "Option 2: Use gcloud"
    echo "  gcloud components install cloud-sql-proxy"
    echo ""
    echo "Then run this script again."
    exit 1
fi

