# Brokey – Finanzen humorvoll erklärt

Pipeline für TikTok-Videos mit dem Stickman **Brokey**. Aus einer Themen-Datei entsteht pro Video eine Mappe mit Skript, Szenenliste, Bild-/Video-Prompts, Faktencheck, Untertiteln, Voiceover-Text und Veröffentlichungs-Checkliste.

Projektregeln: `CLAUDE.md` · Look und Prompt-Bausteine: `brokey-prompt-bibliothek.md`

## Ordner

```
CLAUDE.md                     Projektregeln
brokey-prompt-bibliothek.md   Prompt-Bibliothek (Quelle der Wahrheit für den Look)
bausteine/bausteine.toml      dieselben Bausteine maschinenlesbar, wörtlich aus der Bibliothek
eingang/                      HIER neue Bilder/Clips hochladen (werden dann einsortiert)
bibliothek/bilder|clips/      sortierte Medien, katalog.toml = Beschreibung + Stichworte
tools/brokey.py               das Pipeline-Tool
tools/vorlage-thema.toml      Vorlage für neue Videos
videos/NN-name/thema.toml     DEINE Eingabe pro Video (Skript, Szenen, Zahlen)
videos/NN-name/*.md, *.srt    daraus erzeugt
log.md                        was funktioniert hat, was nicht
```

Die Bibliothek bleibt die Datei für Menschen. `bausteine.toml` ist die Kopie für das Tool. `pruefe-bausteine` stellt sicher, dass beide identisch bleiben.

## Benutzung

Du brauchst Python 3.11 oder neuer, sonst nichts. Alle Befehle laufen im Repo-Hauptordner.

**Neues Video anlegen:**
```bash
python3 tools/brokey.py neu 02 inflation --titel "Inflation frisst dein Geld"
```
Danach `videos/02-inflation/thema.toml` ausfüllen: Sprechertext und Einblendtexte auf Deutsch, Bildbeschreibungen auf Englisch, Mimik/Booster/Aktion als Namen aus `bausteine.toml`.

**Mappe bauen:**
```bash
python3 tools/brokey.py baue videos/01-abo-chaos
```
Ziel aktuell: 35–50 s (ca. 85–120 Wörter). Erzeugt `skript.md`, `szenen.md`, `prompts.md`, `faktencheck.md`, `untertitel.srt`, `einblendungen.srt`, `voiceover.txt` und `checkliste.md`.

Dabei wird automatisch geprüft:
- Rechnungen werden nachgerechnet.
- Markennamen werden gesucht.
- Der Disclaimer muss im Outro stehen.
- Der Running Gag muss vorkommen.
- Die Wortzahl soll bei 85–120 liegen (35–50 s).
- Der Hook soll höchstens ca. 3 s dauern.
- Pro Szene sind höchstens 2 Booster erlaubt.
- Im Bild-Prompt sollen keine Ziffern stehen.

**Bausteine gegen die Bibliothek prüfen:**
```bash
python3 tools/brokey.py pruefe-bausteine
```

**Stimme erzeugen** (ElevenLabs, braucht `ELEVENLABS_API_KEY` und `ELEVENLABS_VOICE_ID` als Umgebungsvariable oder in `.env`):
```bash
python3 tools/vertonung.py videos/01-abo-chaos
```
Zeigt vorher die Zeichenzahl und fragt nach, weil jede Anfrage Guthaben verbraucht. Erzeugt `medien/vo-01.mp3` usw. Mit `--neu 03` nur Szene 3 neu, mit `--tempo 1.1` etwas schneller.

**Neue Medien einsortieren und suchen:**
```bash
python3 tools/katalog.py einsortieren
```
```bash
python3 tools/katalog.py suche abo panik
```
`uebersicht` erzeugt `bibliothek/katalog.md` und ein Vorschaubild aller Medien.

**Video schneiden** (braucht ffmpeg):
```bash
python3 tools/schnitt.py videos/01-abo-chaos --plan
```
```bash
python3 tools/schnitt.py videos/01-abo-chaos
```
Schnelle Schnitte: Jede Szene wird in kurze Einstellungen mit wechselndem Ausschnitt zerlegt (Hook ca. alle 0,6 s, sonst ca. alle 1,8 s, pro Szene änderbar mit `schnitt_tempo = 1.2` in `thema.toml`).
`--plan` zeigt nur, welche Dateien gefunden wurden. Ohne `--plan` entsteht `export/01-abo-chaos.mp4` (1080×1920) mit eingebrannten Untertiteln, Einblendtexten und Disclaimer.
Lege dafür pro Szene in `videos/NN-name/medien/` ab:
- `szene-01.mp4` (Flow-Clip) oder `szene-01.png` (Standbild, bekommt Stop-Motion-Wackeln)
- mehrere pro Szene: `szene-01-a.mp4`, `szene-01-b.mp4` … oder `medien = ["bibliothek/clips/x.mp4", …]` in `thema.toml` → harte Schnitte im Schnitt-Tempo, Clips wackeln nicht
- `vo-01.mp3` (Stimme dieser Szene) – oder eine `voiceover.mp3` für alles

Fehlt ein Bild, kommt ein Platzhalter. Fehlt die Stimme, bleibt es stumm mit geschätzten Zeiten.
Videos und Audios (`*.mp4`, `*.mp3`, `export/`) landen nicht im Repo, weil sie zu groß sind.

ffmpeg installieren: Windows `winget install ffmpeg`, Mac `brew install ffmpeg`, Linux `sudo apt install ffmpeg`.

## Wichtig

- Zeiten in den SRT-Dateien sind **Schätzungen** (ca. 150 Wörter/Minute). Nach der Vertonung anpassen.
- Die Pipeline veröffentlicht **nichts**. `checkliste.md` hakst du vor dem Upload selbst ab, inklusive KI-Kennzeichnung nach den aktuellen TikTok-Regeln.
- API-Schlüssel (z. B. ElevenLabs) gehören nur in `.env`, niemals ins Repo. Vorlage: `.env.example`.
