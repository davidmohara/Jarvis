#!/bin/bash
set -e

# ─────────────────────────────────────────────────────────────────────────────
# HealthQuery Build Script
#
# Prerequisites:
#   - Xcode installed (xcode-select --install)
#   - Paid Apple Developer account
#   - "Apple Development: David O'Hara (TEAMID)" certificate in Keychain
#
# Usage:
#   bash build.sh
#
# First run after build:
#   .build/release/HealthQuery
#   → macOS will show a permission prompt for HealthKit access. Approve once.
#     All subsequent runs are silent.
# ─────────────────────────────────────────────────────────────────────────────

# ── Configuration ─────────────────────────────────────────────────────────────
# Find your Team ID at: https://developer.apple.com/account → Membership Details
TEAM_ID="479NC5HJKS"
SIGNER_NAME="Apple Development: David O'Hara ($TEAM_ID)"
BINARY_NAME="HealthQuery"
ENTITLEMENTS="Resources/HealthQuery.entitlements"
BUILD_PATH=".build/release/$BINARY_NAME"

# ── Validate ──────────────────────────────────────────────────────────────────
if [ "$TEAM_ID" = "YOUR_TEAM_ID" ]; then
    echo "Error: Update TEAM_ID in build.sh before building."
    echo "Find your Team ID at https://developer.apple.com/account → Membership Details"
    exit 1
fi

if ! command -v swift &>/dev/null; then
    echo "Error: Swift not found. Install Xcode from the App Store."
    exit 1
fi

# ── Build ─────────────────────────────────────────────────────────────────────
echo "Building $BINARY_NAME (release)..."
swift build -c release 2>&1

# ── Create App Bundle with Info.plist ──────────────────────────────────────────
# For HealthKit to work on command-line apps, we need to create a proper app bundle
BUNDLE_PATH=".build/release/$BINARY_NAME.app"
mkdir -p "$BUNDLE_PATH/Contents/MacOS"
mkdir -p "$BUNDLE_PATH/Contents"

# Copy binary
cp "$BUILD_PATH" "$BUNDLE_PATH/Contents/MacOS/$BINARY_NAME"

# Create Info.plist
cat > "$BUNDLE_PATH/Contents/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>com.improving.healthquery</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>HealthQuery</string>
    <key>CFBundleName</key>
    <string>HealthQuery</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>NSHealthShareUsageDescription</key>
    <string>HealthQuery needs access to your health data to export metrics for Galen analysis.</string>
    <key>NSHealthUpdateUsageDescription</key>
    <string>HealthQuery reads health data from Apple Health to provide wellness metrics.</string>
</dict>
</plist>
EOF

# Update BUILD_PATH to point to the bundled executable
BUILD_PATH="$BUNDLE_PATH"

# ── Sign ──────────────────────────────────────────────────────────────────────
echo ""
echo "Signing with: $SIGNER_NAME"
codesign \
    --force \
    --sign "$SIGNER_NAME" \
    --entitlements "$ENTITLEMENTS" \
    --options runtime \
    "$BUNDLE_PATH"

# ── Verify ────────────────────────────────────────────────────────────────────
echo ""
echo "Verifying signature..."
codesign -dvvv "$BUNDLE_PATH" 2>&1 | grep -E "(Authority|TeamIdentifier|Entitlements)" || true

echo ""
echo "─────────────────────────────────────────────────────────────────────────"
echo "Build complete: $BUNDLE_PATH"
echo ""
echo "Next steps:"
echo "  1. Run: open $BUNDLE_PATH"
echo "     Or: $BUNDLE_PATH/Contents/MacOS/$BINARY_NAME"
echo "  2. Approve the HealthKit permission prompt (one time only)"
echo "  3. Verify output contains records from your devices"
echo "  4. Note the 'source' string that Hume uses — update SourceID.hume"
echo "     in main.swift if it differs from 'com.hume.health'"
echo "─────────────────────────────────────────────────────────────────────────"
