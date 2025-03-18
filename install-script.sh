#!/bin/bash

# Farben für Terminal-Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== MusicXML Instrument Mapper Installer ===${NC}"
echo -e "${BLUE}Willkommen bei der Installation des MusicXML Instrument Mappers${NC}"

# Bestimme Installationsort
INSTALL_DIR="$HOME/Applications/MusicXMLMapper"
REPO_URL="https://github.com/janoschsimon/musicxml-instrument-mapper.git"
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

# Überprüfen, ob Git installiert ist
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git ist nicht installiert. Installation wird abgebrochen.${NC}"
    echo "Bitte installieren Sie Git von git-scm.com oder über Homebrew (brew install git)."
    exit 1
fi

# Erstelle Installationsverzeichnis
echo -e "${BLUE}Erstelle Installationsverzeichnis...${NC}"
mkdir -p "$INSTALL_DIR"

# Repository klonen/aktualisieren
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${BLUE}Vorhandene Installation gefunden. Aktualisiere...${NC}"
    cd "$INSTALL_DIR"
    git pull
else
    echo -e "${BLUE}Lade MusicXML Instrument Mapper herunter...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Python-Abhängigkeiten installieren
echo -e "${BLUE}Installiere Abhängigkeiten...${NC}"
pip3 install -r requirements.txt

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

# Update-Mechanismus in die App integrieren
cat > "$INSTALL_DIR/auto_updater.py" << 'EOF'
import os
import sys
import subprocess
import time

def check_for_updates():
    """Prüft auf Updates im Repository und wendet sie an."""
    try:
        # Aktuellen Pfad ermitteln
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Git Status prüfen
        result = subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=current_dir,
            capture_output=True,
            text=True
        )
        
        # Prüfen, ob Updates verfügbar sind
        result = subprocess.run(
            ["git", "rev-list", "HEAD..origin/main", "--count"],
            cwd=current_dir,
            capture_output=True,
            text=True
        )
        
        commit_count = result.stdout.strip()
        if commit_count and int(commit_count) > 0:
            return True
        return False
    except Exception as e:
        print(f"Fehler beim Prüfen auf Updates: {e}")
        return False

def apply_updates():
    """Wendet verfügbare Updates an."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Updates anwenden
        subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=current_dir,
            check=True
        )
        
        # Abhängigkeiten aktualisieren
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=current_dir,
            check=True
        )
        
        return True
    except Exception as e:
        print(f"Fehler beim Anwenden der Updates: {e}")
        return False

if __name__ == "__main__":
    # Diese Datei kann direkt ausgeführt werden, um Updates zu erzwingen
    if apply_updates():
        print("Updates erfolgreich angewendet.")
    else:
        print("Keine Updates verfügbar oder Fehler beim Update-Prozess.")
EOF

# Integriere den Auto-Updater in die Hauptanwendung durch einen Wrapper
mv "$INSTALL_DIR/musicxml-instrument-mapper.py" "$INSTALL_DIR/musicxml-instrument-mapper_original.py"

cat > "$INSTALL_DIR/musicxml-instrument-mapper.py" << 'EOF'
#!/usr/bin/env python3
import os
import sys
import importlib.util
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_update():
    """Prüft auf Updates und fragt den Benutzer, ob sie angewendet werden sollen."""
    try:
        spec = importlib.util.spec_from_file_location("auto_updater", 
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_updater.py"))
        auto_updater = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auto_updater)
        
        if auto_updater.check_for_updates():
            # Erstelle ein tkinter-Fenster für die Update-Abfrage
            root = tk.Tk()
            root.withdraw()  # Verstecke das Hauptfenster
            
            update = messagebox.askyesno(
                "Update verfügbar",
                "Es ist ein Update für MusicXML Instrument Mapper verfügbar. Möchten Sie es jetzt installieren?",
                icon='info'
            )
            
            if update:
                if auto_updater.apply_updates():
                    messagebox.showinfo(
                        "Update erfolgreich",
                        "Das Update wurde erfolgreich installiert. Die Anwendung wird jetzt neu gestartet."
                    )
                    # Starte die Anwendung neu
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    messagebox.showerror(
                        "Update fehlgeschlagen",
                        "Das Update konnte nicht installiert werden. Die Anwendung wird ohne Update gestartet."
                    )
    except Exception as e:
        print(f"Fehler beim Update-Check: {e}")

if __name__ == "__main__":
    # Prüfe auf Updates beim Start
    check_update()
    
    # Führe die eigentliche Anwendung aus
    original_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "musicxml-instrument-mapper_original.py"
    )
    
    exec(open(original_script).read())
EOF

chmod +x "$INSTALL_DIR/musicxml-instrument-mapper.py"

echo -e "${GREEN}Installation abgeschlossen!${NC}"
echo -e "${GREEN}MusicXML Instrument Mapper wurde erfolgreich installiert.${NC}"
echo -e "${BLUE}Sie können die Anwendung starten durch:${NC}"
echo -e "  1. Doppelklick auf die App ${GREEN}/Applications/MusicXML Mapper.app${NC}"
echo -e "  2. Oder durch Ausführen von ${GREEN}$INSTALL_DIR/launch.command${NC}"
echo -e "${BLUE}Die Anwendung wird automatisch nach Updates suchen beim Start.${NC}"
echo -e "${BLUE}Genießen Sie MusicXML Instrument Mapper!${NC}"
