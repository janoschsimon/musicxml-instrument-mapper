# MusicXML Instrument Mapper

Tool zum Zuweisen von MuseScore-Sounds in MusicXML-Dateien.

## Features
- Automatische Erkennung von Instrumenten in MusicXML-Dateien
- Zuweisen von Sounds aus verschiedenen Bibliotheken (MuseSounds, CineSamples, etc.)
- Abspielen von Testtönen
- Unterstützung für kostenlose und Premium-Sounds
- Automatische Updates

## Installation

### Für macOS

1. Laden Sie das Installationsskript herunter:
   ```
   curl -L https://raw.githubusercontent.com/janoschsimon/musicxml-instrument-mapper/main/install.sh -o install.sh
   ```

2. Machen Sie es ausführbar und führen Sie es aus:
   ```
   chmod +x install.sh
   ./install.sh
   ```

3. Die Anwendung wird im Ordner `Applications` installiert und kann von dort gestartet werden.

### Für Windows

1. Öffnen Sie PowerShell als Administrator und führen Sie folgenden Befehl aus:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. Laden Sie das Installationsskript herunter und führen Sie es aus:
   ```powershell
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/janoschsimon/musicxml-instrument-mapper/main/install.ps1" -OutFile "install.ps1"
   .\install.ps1
   ```

3. Die Anwendung wird im lokalen Benutzerverzeichnis installiert und im Startmenü sowie auf dem Desktop verknüpft.

### Manuelle Installation (alle Betriebssysteme)

1. Klonen Sie dieses Repository:
   ```
   git clone https://github.com/janoschsimon/musicxml-instrument-mapper.git
   ```

2. Navigieren Sie zum Projektverzeichnis:
   ```
   cd musicxml-instrument-mapper
   ```

3. Starten Sie die Anwendung:
   ```
   python musicxml-instrument-mapper.py
   ```

## Verwendung
1. MusicXML-Datei öffnen
2. Instrumente zuweisen
3. Speichern

## Updates

Die Anwendung sucht automatisch nach Updates beim Start.

### Manuelle Updates

#### Auf macOS:
```
cd ~/Applications/MusicXMLMapper
./update.command
```

#### Auf Windows:
Verwenden Sie die "Update MusicXML Mapper"-Verknüpfung im Startmenü oder führen Sie aus:
```
cd %LOCALAPPDATA%\MusicXMLMapper
update.bat
```

## Voraussetzungen
- Python 3.6 oder höher
- Git
