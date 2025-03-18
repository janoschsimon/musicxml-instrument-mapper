#!/bin/bash

# Farben für Terminal-Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== MusicXML Instrument Mapper Installer ===${NC}"
echo -e "${BLUE}Lokale Installation von Ihrem aktuellen Verzeichnis${NC}"

# Bestimme Installationsort
INSTALL_DIR="$HOME/Applications/MusicXMLMapper"
CURRENT_DIR="$(pwd)"
APP_NAME="MusicXML Mapper.app"

# Überprüfen, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 ist nicht installiert. Installation wird abgebrochen.${NC}"
    echo "Bitte installieren Sie Python 3 von python.org oder über Homebrew (brew install python)."
    exit 1
fi

# Überprüfen, ob pip installiert ist
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 ist nicht installiert. Installation wird abgebrochen.${NC}"
    echo "Bitte installieren Sie pip für Python 3."
    exit 1
fi

# Erstelle Installationsverzeichnis
echo -e "${BLUE}Erstelle Installationsverzeichnis...${NC}"
mkdir -p "$INSTALL_DIR"

# Kopiere das aktuelle Verzeichnis ins Zielverzeichnis
echo -e "${BLUE}Kopiere Dateien in das Installationsverzeichnis...${NC}"
cp -R "$CURRENT_DIR"/* "$INSTALL_DIR/"

# Python-Abhängigkeiten installieren
echo -e "${BLUE}Installiere Abhängigkeiten...${NC}"
pip3 install -r "$INSTALL_DIR/requirements.txt"

# App-Verknüpfung erstellen
echo -e "${BLUE}Erstelle App-Verknüpfung...${NC}"

# Erstelle ein einfaches Launcher-Skript
cat > "$INSTALL_DIR/launch.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 musicxml-instrument-mapper.py
EOF

# Mache es ausführbar
chmod +x "$INSTALL_DIR/launch.command"

# Erstelle ein .app-Bundle
APP_DIR="$INSTALL_DIR/$APP_NAME/Contents/MacOS"
mkdir -p "$APP_DIR"

# Kopiere das Launcher-Skript in das Bundle
cp "$INSTALL_DIR/launch.command" "$APP_DIR/MusicXMLMapper"
chmod +x "$APP_DIR/MusicXMLMapper"

# Erstelle eine Info.plist
mkdir -p "$INSTALL_DIR/$APP_NAME/Contents"
cat > "$INSTALL_DIR/$APP_NAME/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>MusicXMLMapper</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.janoschsimon.musicxmlmapper</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>MusicXML Mapper</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Erstelle einen Symlink im /Applications-Ordner
ln -sf "$INSTALL_DIR/$APP_NAME" "/Applications/MusicXML Mapper.app"

# Auto-Update-Skript erstellen
echo -e "${BLUE}Erstelle Auto-Update-Skript...${NC}"
cat > "$INSTALL_DIR/update.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "Prüfe auf Updates..."
git pull
pip3 install -r requirements.txt
echo "Update abgeschlossen. Starte Anwendung..."
exec "./launch.command"
EOF

chmod +x "$INSTALL_DIR/update.command"

# Machen Sie das Verzeichnis zum Git-Repository, falls es keines ist
if [ ! -d "$INSTALL_DIR/.git" ]; then
    echo -e "${BLUE}Initialisiere Git-Repository für Updates...${NC}"
    cd "$INSTALL_DIR"
    git init
    git remote add origin "https://github.com/janoschsimon/musicxml-instrument-mapper.git"
    git fetch
    git checkout -b main
    git add .
    git commit -m "Initial installation"
fi

echo -e "${GREEN}Installation abgeschlossen!${NC}"
echo -e "${GREEN}MusicXML Instrument Mapper wurde erfolgreich installiert.${NC}"
echo -e "${BLUE}Sie können die Anwendung starten durch:${NC}"
echo -e "  1. Doppelklick auf die App ${GREEN}/Applications/MusicXML Mapper.app${NC}"
echo -e "  2. Oder durch Ausführen von ${GREEN}$INSTALL_DIR/launch.command${NC}"
echo -e "${BLUE}Die Anwendung wird automatisch nach Updates suchen beim Start.${NC}"
echo -e "${BLUE}Genießen Sie MusicXML Instrument Mapper!${NC}"
