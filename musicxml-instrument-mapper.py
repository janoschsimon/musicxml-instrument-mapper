import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import xml.etree.ElementTree as ET
import re
import os
import json
import platform
from pathlib import Path

class MusicXMLInstrumentMapper:
    def __init__(self, root):
        self.root = root
        self.root.title("MusicXML Instrument Mapper")
        self.root.geometry("1024x768")
        
        # Initialisierung für Sound-Libraries
        self.sound_libraries = {}
        
        # Fallback-Sound-Libraries, falls keine gefunden werden
        self.default_libraries = {
            "CineSamples": {
                "Strings": ["strings.violin.cinesamples", "strings.viola.cinesamples"],
                "Woodwinds": ["woodwinds.flute.cinesamples", "woodwinds.oboe.cinesamples"],
                "Brass": ["brass.trumpet.cinesamples", "brass.horn.cinesamples"],
                "Percussion": ["percussion.timpani.cinesamples", "percussion.cymbals.cinesamples"]
            },
            "Orchestral Tools": {
                "Strings": ["strings.violin.berlin", "strings.viola.berlin"],
                "Woodwinds": ["woodwinds.flute.berlin", "woodwinds.oboe.berlin"],
                "Brass": ["brass.trumpet.berlin", "brass.horn.berlin"],
                "Percussion": ["percussion.timpani.berlin", "percussion.cymbals.berlin"]
            }
        }
        
        # Standard-Kategorien für Instrumentenerkennung
        self.instrument_categories = {
            "violin": "Strings",
            "viola": "Strings",
            "cello": "Strings",
            "bass": "Strings",
            "flute": "Woodwinds",
            "oboe": "Woodwinds",
            "clarinet": "Woodwinds",
            "bassoon": "Woodwinds",
            "trumpet": "Brass",
            "horn": "Brass",
            "trombone": "Brass",
            "tuba": "Brass",
            "timpani": "Percussion",
            "percussion": "Percussion"
        }
        
        # Hauptframe erstellen
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dateiauswahl
        file_frame = ttk.Frame(self.main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="MusicXML Datei:").pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Durchsuchen...", command=self.browse_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Analyse", command=self.analyze_file).pack(side=tk.LEFT, padx=5)
        
        # Instrument-Mapping-Frame
        self.mapping_frame = ttk.LabelFrame(self.main_frame, text="Instrument Mapping")
        self.mapping_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbare Ansicht für viele Instrumente
        self.canvas = tk.Canvas(self.mapping_frame)
        scrollbar = ttk.Scrollbar(self.mapping_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Aktionsbuttons
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Speichern", command=self.save_changes).pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="Als neu speichern", command=self.save_as_new).pack(side=tk.RIGHT)
        
        # Status-Label
        self.status_var = tk.StringVar(value="Bereit")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Initialisiere Variablen
        self.xml_tree = None
        self.instrument_mappings = []
        
        # Jetzt können wir nach MuseScore-Sounds suchen, nachdem die UI initialisiert wurde
        self.load_musescore_sounds()
        
        # Fallback, falls keine Sounds gefunden wurden
        if not self.sound_libraries:
            self.sound_libraries = self.default_libraries.copy()
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("MusicXML files", "*.xml *.musicxml"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def analyze_file(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine Datei aus.")
            return
            
        try:
            # Lösche vorherige Mapping-Widgets
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            self.instrument_mappings = []
            
            # Parse XML
            self.xml_tree = ET.parse(file_path)
            root = self.xml_tree.getroot()
            
            # Finde Namespace falls vorhanden
            ns = {}
            match = re.match(r'{(.+)}', root.tag)
            if match:
                ns['ns'] = match.group(1)
                ns_prefix = '{' + ns['ns'] + '}'
            else:
                ns_prefix = ''
            
            # Finde alle Instrumente in der MusicXML-Datei
            found_instruments = []
            
            # Suche nach score-part-Elementen
            part_elements = root.findall('.//' + ns_prefix + 'score-part')
            
            # Header für die Tabelle
            header_frame = ttk.Frame(self.scrollable_frame)
            header_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(header_frame, text="Original Name", width=20).grid(row=0, column=0, padx=5)
            ttk.Label(header_frame, text="Sound Library", width=15).grid(row=0, column=1, padx=5)
            ttk.Label(header_frame, text="Kategorie", width=15).grid(row=0, column=2, padx=5)
            ttk.Label(header_frame, text="Instrument", width=20).grid(row=0, column=3, padx=5)
            ttk.Label(header_frame, text="Vorschau", width=30).grid(row=0, column=4, padx=5)
            
            # Für jedes gefundene Instrument
            for idx, part in enumerate(part_elements):
                part_id = part.get('id')
                
                # Finde den Instrumentennamen
                part_name_elem = part.find('.//' + ns_prefix + 'part-name')
                if part_name_elem is not None and part_name_elem.text:
                    part_name = part_name_elem.text.strip()
                else:
                    part_name = f"Instrument {idx+1}"
                
                # Finde instrument-sound wenn vorhanden
                instrument_sound = None
                sound_elem = part.find('.//' + ns_prefix + 'instrument-sound')
                if sound_elem is not None and sound_elem.text:
                    instrument_sound = sound_elem.text.strip()
                
                # Erstelle ein neues Mapping für dieses Instrument
                mapping_frame = ttk.Frame(self.scrollable_frame)
                mapping_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(mapping_frame, text=part_name, width=20).grid(row=0, column=0, padx=5)
                
                # Erstelle Dropdown für Sound-Library
                library_var = tk.StringVar()
                library_dropdown = ttk.Combobox(mapping_frame, textvariable=library_var, width=15)
                library_dropdown['values'] = list(self.sound_libraries.keys())
                library_dropdown.current(0)  # Setze Standard
                library_dropdown.grid(row=0, column=1, padx=5)
                
                # Erstelle Dropdown für Kategorie
                category_var = tk.StringVar()
                category_dropdown = ttk.Combobox(mapping_frame, textvariable=category_var, width=15)
                category_dropdown['values'] = ["Strings", "Woodwinds", "Brass", "Percussion"]
                
                # Versuche, die Kategorie zu erraten
                guessed_category = None
                for key, category in self.instrument_categories.items():
                    if key.lower() in part_name.lower():
                        guessed_category = category
                        break
                
                if guessed_category:
                    category_var.set(guessed_category)
                else:
                    category_dropdown.current(0)  # Setze Standard
                
                category_dropdown.grid(row=0, column=2, padx=5)
                
                # Erstelle Dropdown für Instrument
                instrument_var = tk.StringVar()
                instrument_dropdown = ttk.Combobox(mapping_frame, textvariable=instrument_var, width=20)
                
                # Aktualisiere Instrument-Dropdown basierend auf Kategorie
                def update_instruments(*args):
                    library = library_var.get()
                    category = category_var.get()
                    if library in self.sound_libraries and category in self.sound_libraries[library]:
                        instrument_dropdown['values'] = self.sound_libraries[library][category]
                        if instrument_dropdown['values']:
                            instrument_dropdown.current(0)
                    update_preview()
                
                library_var.trace_add("write", update_instruments)
                category_var.trace_add("write", update_instruments)
                
                instrument_dropdown.grid(row=0, column=3, padx=5)
                
                # Vorschau des Sound-Identifiers
                preview_var = tk.StringVar()
                preview_label = ttk.Label(mapping_frame, textvariable=preview_var, width=30)
                preview_label.grid(row=0, column=4, padx=5)
                
                def update_preview(*args):
                    preview_var.set(instrument_var.get())
                
                instrument_var.trace_add("write", update_preview)
                
                # Initial aktualisieren
                update_instruments()
                
                # Speichere Mapping-Informationen
                self.instrument_mappings.append({
                    'part_id': part_id,
                    'part_name': part_name,
                    'library_var': library_var,
                    'category_var': category_var,
                    'instrument_var': instrument_var,
                    'original_sound': instrument_sound
                })
            
            self.status_var.set(f"{len(self.instrument_mappings)} Instrumente gefunden.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Analysieren der Datei: {str(e)}")
            self.status_var.set("Fehler bei der Analyse.")
    
    def save_changes(self):
        if not self.xml_tree or not self.instrument_mappings:
            messagebox.showerror("Fehler", "Keine Daten zum Speichern vorhanden.")
            return
        
        try:
            root = self.xml_tree.getroot()
            # Finde Namespace falls vorhanden
            ns = {}
            match = re.match(r'{(.+)}', root.tag)
            if match:
                ns['ns'] = match.group(1)
                ns_prefix = '{' + ns['ns'] + '}'
            else:
                ns_prefix = ''
            
            # Aktualisiere jeden Part mit dem neuen Instrument Sound
            for mapping in self.instrument_mappings:
                part_id = mapping['part_id']
                new_sound = mapping['instrument_var'].get()
                
                # Finde den entsprechenden Part
                part_elem = root.find('.//' + ns_prefix + f'score-part[@id="{part_id}"]')
                if part_elem is not None:
                    # Suche nach instrument-sound Element
                    sound_elem = part_elem.find('.//' + ns_prefix + 'instrument-sound')
                    
                    if sound_elem is not None:
                        # Aktualisiere existierendes Element
                        sound_elem.text = new_sound
                    else:
                        # Erstelle neues Element
                        # Finde zuerst score-instrument
                        score_instrument = part_elem.find('.//' + ns_prefix + 'score-instrument')
                        if score_instrument is not None:
                            sound_elem = ET.SubElement(score_instrument, ns_prefix + 'instrument-sound')
                            sound_elem.text = new_sound
            
            # Speichere Änderungen
            self.xml_tree.write(self.file_path_var.get(), encoding='UTF-8', xml_declaration=True)
            
            messagebox.showinfo("Erfolg", "Änderungen wurden gespeichert!")
            self.status_var.set("Änderungen gespeichert.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Änderungen: {str(e)}")
            self.status_var.set("Fehler beim Speichern.")
    
    def save_as_new(self):
        if not self.xml_tree:
            messagebox.showerror("Fehler", "Keine Daten zum Speichern vorhanden.")
            return
        
        new_file_path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("MusicXML files", "*.xml"), ("All files", "*.*")],
            initialdir=str(Path(self.file_path_var.get()).parent)
        )
        
        if new_file_path:
            old_path = self.file_path_var.get()
            self.file_path_var.set(new_file_path)
            self.save_changes()
            # Zurück zur alten Datei, falls der Benutzer weiterarbeiten möchte
            self.file_path_var.set(old_path)
    
    def load_musescore_sounds(self):
        """Sucht nach installierten MuseScore-Sounds und lädt diese dynamisch."""
        self.status_var.set("Suche nach MuseScore-Sounds...")
        
        # Mögliche Installationspfade von MuseScore je nach Betriebssystem
        search_paths = []
        
        system = platform.system()
        if system == "Windows":
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            
            search_paths = [
                os.path.join(program_files, "MuseScore 4"),
                os.path.join(program_files_x86, "MuseScore 4"),
                os.path.join(program_files, "MuseScore 3"),
                os.path.join(program_files_x86, "MuseScore 3")
            ]
            
            # Auch im AppData-Verzeichnis suchen (für MuseHub)
            appdata = os.environ.get("APPDATA", "")
            if appdata:
                search_paths.append(os.path.join(appdata, "MuseScore", "MuseScore4"))
                search_paths.append(os.path.join(appdata, "MuseScore", "MuseScore3"))
                search_paths.append(os.path.join(appdata, "MuseHub"))
        
        elif system == "Darwin":  # macOS
            search_paths = [
                "/Applications/MuseScore 4.app/Contents/Resources",
                "/Applications/MuseScore 3.app/Contents/Resources",
                os.path.expanduser("~/Library/Application Support/MuseScore"),
                os.path.expanduser("~/Library/Application Support/MuseHub")
            ]
        
        elif system == "Linux":
            search_paths = [
                "/usr/share/mscore-4.0",
                "/usr/share/mscore",
                "/usr/local/share/mscore",
                os.path.expanduser("~/.local/share/MuseScore"),
                os.path.expanduser("~/.local/share/MuseHub")
            ]
        
        # Suche nach Metadaten-Dateien
        metadata_files = []
        for path in search_paths:
            if not os.path.exists(path):
                continue
                
            # Verschiedene mögliche Speicherorte für die Soundfonts-Metadaten
            possible_locations = [
                os.path.join(path, "soundfonts", "muse-sounds-metadata.json"),
                os.path.join(path, "sounds", "metadata.json"),
                os.path.join(path, "Soundfonts", "metadata.json")
            ]
            
            for loc in possible_locations:
                if os.path.exists(loc):
                    metadata_files.append(loc)
        
        if not metadata_files:
            self.status_var.set("Keine MuseSound-Metadaten gefunden, verwende Standard-Bibliotheken.")
            return
        
        # Parsen der gefundenen Metadaten-Dateien
        for metadata_file in metadata_files:
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Verarbeite die Metadaten je nach Format
                if isinstance(data, dict) and "sounds" in data:
                    self._process_musehub_metadata(data)
                elif isinstance(data, list):
                    self._process_musescore_metadata(data)
                
                self.status_var.set(f"MuseSound-Bibliotheken erfolgreich geladen aus {metadata_file}")
                
            except Exception as e:
                self.status_var.set(f"Fehler beim Laden der Metadaten: {str(e)}")
    
    def _process_musehub_metadata(self, data):
        """Verarbeitet Metadaten im MuseHub-Format."""
        sounds = data.get("sounds", [])
        
        for sound in sounds:
            library_name = sound.get("publisher", "Unbekannt")
            sound_id = sound.get("id", "")
            display_name = sound.get("displayName", "")
            
            # Versuche, die Kategorie und den Instrumententyp zu extrahieren
            category = "Andere"
            for possible_category in ["Strings", "Woodwinds", "Brass", "Percussion", "Keys"]:
                if possible_category.lower() in sound_id.lower() or possible_category.lower() in display_name.lower():
                    category = possible_category
                    break
            
            # Füge die Bibliothek hinzu, falls noch nicht vorhanden
            if library_name not in self.sound_libraries:
                self.sound_libraries[library_name] = {}
            
            # Füge die Kategorie hinzu, falls noch nicht vorhanden
            if category not in self.sound_libraries[library_name]:
                self.sound_libraries[library_name][category] = []
            
            # Füge den Sound hinzu
            self.sound_libraries[library_name][category].append(sound_id)
    
    def _process_musescore_metadata(self, data):
        """Verarbeitet Metadaten im MuseScore-Format."""
        for sound in data:
            if not isinstance(sound, dict):
                continue
                
            sound_id = sound.get("id", "")
            if not sound_id:
                continue
                
            # Extrahiere den Bibliotheksnamen aus dem Sound-ID
            library_name = "MuseScore"
            for possible_lib in ["CineSamples", "Berlin", "Orchestral Tools", "Spitfire"]:
                if possible_lib.lower() in sound_id.lower():
                    library_name = possible_lib
                    break
            
            # Normalisiere Bibliotheksnamen
            if "berlin" in library_name.lower() or "orchestral tools" in library_name.lower():
                library_name = "Orchestral Tools"
            
            # Bestimme die Kategorie
            category = "Andere"
            for possible_category in ["Strings", "Woodwinds", "Brass", "Percussion", "Keys"]:
                if possible_category.lower() in sound_id.lower():
                    category = possible_category
                    break
            
            # Füge die Bibliothek hinzu, falls noch nicht vorhanden
            if library_name not in self.sound_libraries:
                self.sound_libraries[library_name] = {}
            
            # Füge die Kategorie hinzu, falls noch nicht vorhanden
            if category not in self.sound_libraries[library_name]:
                self.sound_libraries[library_name][category] = []
            
            # Füge den Sound hinzu, falls noch nicht vorhanden
            if sound_id not in self.sound_libraries[library_name][category]:
                self.sound_libraries[library_name][category].append(sound_id)


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicXMLInstrumentMapper(root)
    root.mainloop()
