#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_NAME="Ollama Local AI"
APP_DIR="$SCRIPT_DIR/$APP_NAME.app"

rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# ── Info.plist ─────────────────────────────────────────────────────────

cat > "$APP_DIR/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Ollama Local AI</string>
    <key>CFBundleDisplayName</key>
    <string>Ollama Local AI</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.ollama-local-ai</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>12.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# ── Store project path ────────────────────────────────────────────────

echo "$PROJECT_DIR" > "$APP_DIR/Contents/Resources/project_path"

# ── Launcher executable ───────────────────────────────────────────────

cat > "$APP_DIR/Contents/MacOS/launcher" << 'LAUNCHER'
#!/bin/bash

RESOURCES_DIR="$(cd "$(dirname "$0")/../Resources" && pwd)"
PROJECT_DIR="$(cat "$RESOURCES_DIR/project_path")"
START_SCRIPT="$PROJECT_DIR/scripts/start.sh"

if [ ! -f "$START_SCRIPT" ]; then
    osascript -e "display alert \"Ollama Local AI\" message \"Project not found at: $PROJECT_DIR\" as critical"
    exit 1
fi

osascript <<EOF
tell application "Terminal"
    activate
    do script "\"$START_SCRIPT\""
end tell
EOF
LAUNCHER

chmod +x "$APP_DIR/Contents/MacOS/launcher"

# ── App Icon (PNG via pure Python, converted to icns via sips/iconutil)

python3 << 'PYICON'
import struct, zlib, os

SIZE = 512
BG_R, BG_G, BG_B = 59, 130, 246  # blue
FG_R, FG_G, FG_B = 255, 255, 255  # white

pixels = []
for y in range(SIZE):
    row = []
    for x in range(SIZE):
        cx, cy = SIZE // 2, SIZE // 2
        r = SIZE // 2 - 20
        dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        if dist <= r:
            edge = max(0, min(1, (r - dist) / 2))
            in_letter = False
            # "A" shape
            ax = x - 128
            ay = SIZE - y - 100
            if 120 <= ax <= 260 and 40 <= ay <= 340:
                mid = 190
                half_w = int(10 + (340 - ay) * 0.3)
                if abs(ax - mid) <= half_w:
                    if abs(ax - mid) >= half_w - 28 or ay < 60:
                        in_letter = True
                    if 140 <= ay <= 175:
                        in_letter = True
            # "I" shape
            ix = x - 280
            iy = SIZE - y - 100
            if 40 <= iy <= 340 and 20 <= ix <= 100:
                if 60 <= ix <= 76 or iy >= 310 or iy <= 70:
                    in_letter = True

            if in_letter:
                row.append((FG_R, FG_G, FG_B, int(255 * edge)))
            else:
                row.append((BG_R, BG_G, BG_B, int(255 * edge)))
        else:
            row.append((0, 0, 0, 0))
    pixels.append(row)

def make_png(pixels, size):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    raw = b''
    for row in pixels:
        raw += b'\x00'
        for r, g, b, a in row:
            raw += struct.pack('BBBB', r, g, b, a)

    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')

png_data = make_png(pixels, SIZE)
with open('/tmp/ollama_icon.png', 'wb') as f:
    f.write(png_data)
print("Icon PNG generated")
PYICON

if [ -f "/tmp/ollama_icon.png" ]; then
    ICONSET="/tmp/OllamaAI.iconset"
    rm -rf "$ICONSET"
    mkdir -p "$ICONSET"
    for S in 16 32 64 128 256 512; do
        sips -z $S $S /tmp/ollama_icon.png --out "$ICONSET/icon_${S}x${S}.png" 2>/dev/null
    done
    for S in 16 32 128 256; do
        S2=$((S * 2))
        sips -z $S2 $S2 /tmp/ollama_icon.png --out "$ICONSET/icon_${S}x${S}@2x.png" 2>/dev/null
    done
    iconutil -c icns "$ICONSET" -o "$APP_DIR/Contents/Resources/AppIcon.icns" 2>/dev/null && echo "Icon created" || echo "iconutil failed, using default icon"
    rm -rf "$ICONSET" /tmp/ollama_icon.png
fi

echo "Created: $APP_DIR"
