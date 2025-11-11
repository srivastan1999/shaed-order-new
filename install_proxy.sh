#!/usr/bin/env zsh

# Install Cloud SQL Proxy
# Run this once to install the proxy

echo "============================================================"
echo "Installing Cloud SQL Proxy"
echo "============================================================"
echo ""

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    URL="https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.arm64"
    echo "Detected: Apple Silicon (M1/M2)"
else
    URL="https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64"
    echo "Detected: Intel Mac"
fi

echo ""
echo "Downloading Cloud SQL Proxy..."
curl -o cloud-sql-proxy "$URL"

if [ $? -ne 0 ]; then
    echo "✗ Download failed"
    exit 1
fi

echo "✓ Downloaded"
echo ""

echo "Making executable..."
chmod +x cloud-sql-proxy

echo "✓ Made executable"
echo ""

echo "Moving to /usr/local/bin/ (requires sudo)..."
sudo mv cloud-sql-proxy /usr/local/bin/

if [ $? -eq 0 ]; then
    echo "✓ Installed successfully"
    echo ""
    echo "============================================================"
    echo "Installation Complete!"
    echo "============================================================"
    echo ""
    echo "You can now run:"
    echo "  ./start_proxy.sh"
    echo ""
else
    echo "✗ Failed to move to /usr/local/bin/"
    echo ""
    echo "You can still use it from current directory:"
    echo "  mv /usr/local/bin/cloud-sql-proxy ./cloud-sql-proxy"
    echo "  ./start_proxy.sh"
fi

