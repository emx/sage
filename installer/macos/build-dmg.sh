#!/bin/bash
set -euo pipefail

# Build a signed macOS .dmg installer for SAGE.
#
# Prerequisites:
#   - Xcode command line tools
#   - Developer ID Application certificate in keychain
#   - Apple notarytool credentials (for notarization)
#
# Environment variables:
#   SAGE_VERSION      - Version string (e.g. "2.1.0")
#   SAGE_ARCH         - Target architecture: "amd64" or "arm64" (default: current)
#   SIGN_IDENTITY     - Code signing identity (e.g. "Developer ID Application: Your Name (TEAMID)")
#   NOTARIZE          - Set to "1" to notarize (requires APPLE_ID, APPLE_TEAM_ID, APPLE_PASSWORD)
#   APPLE_ID          - Apple ID email for notarization
#   APPLE_TEAM_ID     - Apple Developer Team ID
#   APPLE_PASSWORD    - App-specific password for notarization

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VERSION="${SAGE_VERSION:-dev}"
ARCH="${SAGE_ARCH:-$(uname -m)}"

# Normalize arch names
case "$ARCH" in
    amd64|x86_64) GOARCH="amd64"; ARCH_LABEL="x86_64" ;;
    arm64|aarch64) GOARCH="arm64"; ARCH_LABEL="arm64" ;;
    *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

APP_NAME="SAGE"
DMG_NAME="SAGE-${VERSION}-macOS-${ARCH_LABEL}"
BUILD_DIR="${PROJECT_ROOT}/dist/macos-${ARCH_LABEL}"
APP_DIR="${BUILD_DIR}/${APP_NAME}.app"

echo "==> Building SAGE ${VERSION} for macOS ${ARCH_LABEL}"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Build the binary
echo "==> Compiling sage-lite..."
LDFLAGS="-s -w -X main.version=${VERSION} -X main.commit=$(git -C "$PROJECT_ROOT" rev-parse --short HEAD) -X main.date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
CGO_ENABLED=0 GOOS=darwin GOARCH="$GOARCH" go build \
    -ldflags "$LDFLAGS" \
    -o "${BUILD_DIR}/sage-lite" \
    "${PROJECT_ROOT}/cmd/sage-lite"

# Create .app bundle structure
echo "==> Creating app bundle..."
mkdir -p "${APP_DIR}/Contents/MacOS"
mkdir -p "${APP_DIR}/Contents/Resources"

# Copy binary
cp "${BUILD_DIR}/sage-lite" "${APP_DIR}/Contents/MacOS/sage-lite"

# Create launcher script that opens Terminal with sage-lite
cat > "${APP_DIR}/Contents/MacOS/SAGE" << 'LAUNCHER'
#!/bin/bash
# SAGE Launcher — opens Terminal and runs sage-lite
SAGE_BIN="$(dirname "$0")/sage-lite"

# If first run, do setup first
if [ ! -d "$HOME/.sage" ]; then
    osascript -e "tell application \"Terminal\"
        activate
        do script \"'${SAGE_BIN}' setup && '${SAGE_BIN}' serve\"
    end tell"
else
    osascript -e "tell application \"Terminal\"
        activate
        do script \"'${SAGE_BIN}' serve\"
    end tell"
fi
LAUNCHER
chmod +x "${APP_DIR}/Contents/MacOS/SAGE"

# Create Info.plist
cat > "${APP_DIR}/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>SAGE</string>
    <key>CFBundleDisplayName</key>
    <string>SAGE — AI Memory</string>
    <key>CFBundleIdentifier</key>
    <string>com.sage.personal</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>CFBundleExecutable</key>
    <string>SAGE</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>12.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright 2024-2026 Dhillon Andrew Kannabhiran. Apache 2.0 License.</string>
</dict>
</plist>
PLIST

# Copy icon if it exists
if [ -f "${SCRIPT_DIR}/AppIcon.icns" ]; then
    cp "${SCRIPT_DIR}/AppIcon.icns" "${APP_DIR}/Contents/Resources/AppIcon.icns"
else
    echo "    (No AppIcon.icns found — DMG will use default icon)"
fi

# Code sign if identity provided
if [ -n "${SIGN_IDENTITY:-}" ]; then
    echo "==> Code signing with: ${SIGN_IDENTITY}"
    codesign --force --options runtime --deep \
        --sign "$SIGN_IDENTITY" \
        --timestamp \
        "${APP_DIR}/Contents/MacOS/sage-lite"
    codesign --force --options runtime --deep \
        --sign "$SIGN_IDENTITY" \
        --timestamp \
        "${APP_DIR}"
    echo "    Verifying signature..."
    codesign --verify --deep --strict --verbose=2 "${APP_DIR}"
else
    echo "    (Skipping code signing — set SIGN_IDENTITY to enable)"
fi

# Create DMG
echo "==> Creating DMG..."
DMG_TEMP="${BUILD_DIR}/dmg-staging"
mkdir -p "$DMG_TEMP"
cp -R "${APP_DIR}" "$DMG_TEMP/"
ln -s /Applications "$DMG_TEMP/Applications"

# Create a README in the DMG
cat > "$DMG_TEMP/README.txt" << README
SAGE — Give Your AI a Memory
=============================

Drag SAGE.app to Applications, then double-click to start.

On first launch, SAGE opens a Terminal window and runs the
setup wizard to configure your personal memory node.

After setup, SAGE starts automatically and opens the Brain
Dashboard in your browser at http://localhost:8080.

For Claude Code / CLI usage:
  /Applications/SAGE.app/Contents/MacOS/sage-lite serve
  /Applications/SAGE.app/Contents/MacOS/sage-lite mcp

More info: https://github.com/l33tdawg/sage
License: Apache 2.0
Author: Dhillon Andrew Kannabhiran
README

hdiutil create -volname "SAGE ${VERSION}" \
    -srcfolder "$DMG_TEMP" \
    -ov -format UDZO \
    "${BUILD_DIR}/${DMG_NAME}.dmg"

# Notarize if requested
if [ "${NOTARIZE:-}" = "1" ] && [ -n "${APPLE_ID:-}" ]; then
    echo "==> Notarizing DMG..."
    xcrun notarytool submit "${BUILD_DIR}/${DMG_NAME}.dmg" \
        --apple-id "$APPLE_ID" \
        --team-id "$APPLE_TEAM_ID" \
        --password "$APPLE_PASSWORD" \
        --wait

    echo "==> Stapling notarization ticket..."
    xcrun stapler staple "${BUILD_DIR}/${DMG_NAME}.dmg"
else
    echo "    (Skipping notarization — set NOTARIZE=1 to enable)"
fi

echo ""
echo "==> Done! DMG created at:"
echo "    ${BUILD_DIR}/${DMG_NAME}.dmg"
echo ""
ls -lh "${BUILD_DIR}/${DMG_NAME}.dmg"
