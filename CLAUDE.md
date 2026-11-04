# Projekt: Brokey (TikTok-Kanal, Finanzen humorvoll erklärt)

Diese Datei erklärt dir (Claude Code), worum es in diesem Projekt geht, welche Regeln gelten und was deine Aufgabe ist. Lies sie vollständig, bevor du etwas baust oder änderst.

## 1. Worum es geht

Ich (der Nutzer) baue als Selbstständiger einen TikTok-Kanal auf. Es geht um Finanzthemen, die leicht, lustig und verständlich erklärt werden, mit einer Stickman-Figur namens **Brokey**. Alles Material ist selbst erstellt (keine fremden Bilder, Clips oder Marken).

Ziel dieses Repos: Den Ablauf für neue Videos **Schritt für Schritt automatisieren**, damit ich schneller und konsistenter Videos produzieren kann.

## 2. Kanalkonzept

- **Format:** Kurzvideos, aktuell **35-50 Sekunden** mit schnellen Schnitten (vor allem im Hook), Ziel: erst 10.000 Follower. Später ggf. über 1 Minute für das TikTok Creator Rewards Program (aktuelle Bedingungen in der App prüfen, nicht annehmen).
- **Zielgruppe:** breit, von Teenagern über Azubis und Berufseinsteiger bis zu Leuten mit etwas Vorwissen.
- **Ton:** sarkastisch, dramatisch, leicht übertrieben, aber nie zu viel. Am Ende soll man wirklich etwas verstanden haben.
- **Grundregel:** Der Witz transportiert die Info, er ersetzt sie nicht. Pro Video genau ein klarer Lerneffekt, verpackt in eine übertriebene Mini-Geschichte.
- **Erzählform:** Trockener Erzähler (Voiceover) kommentiert sarkastisch, dem Stickman passiert das Chaos. Sarkasmus kommt vom Erzähler, Übertreibung von der Figur.
- **Videoformate:** Fehler-Reihen ("Dinge, die du mit 20 falsch machst"), Alltags-Sketche (Abo-Chaos, Impulskäufe, Gehaltstag), Begriffe erklärt (ETF, Inflation, Zinseszins, Schufa, Steuererklärung), Vergleiche (Sparer vs. Spender), Mythen-Check.
- **Typischer Aufbau eines Videos:**
  1. Hook in den ersten 3 Sekunden (Verlustangst, Schock oder Neugier, ohne Ton verständlich)
  2. Setup (Brokey und die Ausgangslage)
  3. Übertriebene Mini-Geschichte oder Zeitraffer
  4. Rechnung oder Ergebnis (mit klaren Beispielzahlen, als Beispiel gekennzeichnet)
  5. Lerneffekt als Punchline
  6. Outro mit Hinweis "Keine Anlageberatung" bzw. "Keine Finanzberatung"

## 3. Die Figur Brokey (verbindlich)

- Stickman mit großem rundem weißem Kopf, dünnen schwarzen Marker-Gliedern
- **Rote Strickmütze mit Bommel** (Signalfarbe des Kanals, immer rot)
- Schwere, halb geschlossene müde Augen mit Augenringen, kleiner gerader Mund
- Running Gag: leeres braunes Portemonnaie, eine goldene Münze fliegt davon (in jedem Video enthalten)
- Name: **Brokey** (nicht "Pete", das war ein früherer Arbeitstitel)
- Rolle: Er ist nie schlau, ihm passiert das Chaos. Er bleibt trocken, die Welt um ihn herum dreht durch.

## 4. Visueller Stil (verbindlich)

- Handgezeichneter schwarzer Marker-Doodle auf einem **weißen Blatt Papier, das das komplette Bild ausfüllt** (sichtbare Papierfasern, Körnung, leichte Knicke, kein Tisch, keine Papierränder, keine Hände)
- Format 9:16 (Hochformat)
- Kein Text im generierten Bild (Bildmodelle machen bei Schrift Fehler). Text, Zahlen und Untertitel werden **später im Schnitt/per Code** eingefügt.
- Keine Markennamen, Logos oder geschützten Figuren
- Videos: Stop-Motion-Look mit ca. 8-12 Bildern pro Sekunde, wackelnde Linien ("line boil"), statischer Papierhintergrund, feste Kamera

Eine ausführliche, bereits vorhandene Prompt-Bibliothek liegt im Repo (siehe Abschnitt 8). **Nutze deren Bausteine** (CHARACTER, STYLE, AVOID, Mimik-Set, Humor-Booster, Szenen- und Video-Prompts), statt neue Stile zu erfinden.

## 5. Leitplanken (nicht verhandelbar)

**Inhalt und Recht**
- **Bildung statt Beratung:** keine konkreten Kauf- oder Anlageempfehlungen, keine Gewinnversprechen, keine Get-rich-quick-Versprechen.
- Renditen und Preise immer als **Annahme/Beispiel** kennzeichnen, nie als Garantie.
- **Zahlen und Fakten müssen geprüft werden** (Rechenbeispiele nachrechnen, Rechtliches nicht behaupten, bei Unsicherheit als offene Frage an mich markieren).
- Keine Markennamen von Anbietern in Bildern oder Texten, keine Logos.
- Jedes Video bekommt einen sichtbaren Disclaimer ("Keine Anlageberatung" bzw. "Keine Finanzberatung").
- Du bist kein Steuer- oder Rechtsberater. Bei Gewerbe, Steuern, Konto und Recht gilt die Klärung mit Finanzamt, Gewerbeamt oder Steuerberater.
- Ich prüfe vor dem Hochladen die aktuellen TikTok-Regeln, insbesondere zur Kennzeichnung KI-generierter Inhalte. Baue die Pipeline so, dass eine solche Kennzeichnung nicht vergessen wird (z. B. Checklistenpunkt), und behaupte nicht, dass sie unnötig ist.

**Sicherheit und Technik**
- **Niemals Zugangsdaten, API-Schlüssel oder Tokens ins Repo schreiben.** Nutze Umgebungsvariablen und eine `.env`-Datei, die in `.gitignore` steht. Lege eine `.env.example` ohne echte Werte an.
- Keine Logins, Konten oder Bezahlvorgänge im Namen des Nutzers ohne ausdrückliche Bestätigung.
- Nichts automatisch auf TikTok veröffentlichen. **Der Mensch (ich) prüft und lädt hoch.**
- Keine Dateien aus unsicheren Quellen herunterladen oder ausführen.
- Vor größeren Änderungen (Löschen, Umstrukturieren, Abhängigkeiten) kurz fragen.

## 6. Ziel der Automatisierung

Eine Pipeline, bei der ich mit einem Thema starte und möglichst viele Schritte vorbereitet bekomme:

1. **Thema und Lerneffekt** festlegen (Eingabe: Thema, Zielgruppe, gewünschter Ton)
2. **Skript** nach dem Aufbau aus Abschnitt 2 erzeugen (inkl. Sprechertext, ca. 85-120 Wörter für 35-50 Sekunden)
3. **Szenenliste** mit pro Szene: Bildbeschreibung, Mimik, Humor-Booster, Sprechertext, Einblendtext
4. **Bild-Prompts** aus den Bausteinen der Prompt-Bibliothek zusammensetzen
5. **Video-Prompts** (Bild-zu-Video) mit Aktionen in Zeitphasen erzeugen
6. **Faktencheck-Liste:** alle Zahlen, Annahmen und Behauptungen des Skripts extrahieren, damit ich sie prüfen kann
7. **Untertitel/Einblendtexte** als Datei (z. B. SRT) erzeugen
8. **Voiceover:** Sprechertext sauber aufbereiten (für TTS oder meine eigene Aufnahme)
9. **Zusammenbau** (später): Bilder/Clips, Audio und Untertitel zu einem fertigen Video, z. B. mit ffmpeg
10. **Veröffentlichungs-Checkliste:** Disclaimer drin, Zahlen geprüft, KI-Kennzeichnung, Caption und Hashtags, keine Markennamen

Priorität: erst Schritte 1-7 (Texte, Prompts, Checklisten), dann 8-9, wenn ich es möchte. Schritt 10 ist immer manuell.

## 7. Wie du arbeiten sollst

- **Klein anfangen.** Baue zuerst ein einfaches, lauffähiges Grundgerüst (z. B. ein Skript, das aus einem Thema eine Markdown-Datei mit Skript, Szenenliste und Prompts erzeugt), bevor du Automatisierung für Bild- oder Videogenerierung planst.
- **Frag mich, bevor du Annahmen triffst**, besonders bei:
  - Programmiersprache und Tools (Vorschlag: Python, aber bitte frag)
  - welche Bild-/Video-/Audio-Tools ich nutzen kann (ich nutze bisher Google Flow für Bilder/Videos; ob und wie sich das automatisieren lässt, ist offen und muss geprüft werden, nicht annehmen)
  - Kosten und Konten
- **Keine erfundenen Schnittstellen.** Wenn du nicht sicher bist, ob ein Tool eine API oder Funktion hat, sag es und prüfe die aktuelle Dokumentation, statt zu raten.
- **Transparent bleiben:** Erkläre kurz, was du gebaut hast und wie ich es benutze. Keine langen Berichte, ein paar klare Sätze reichen.
- **Reproduzierbar:** Jedes Video bekommt einen eigenen Ordner mit Skript, Szenenliste, Prompts und Faktencheck, damit alles nachvollziehbar und versionierbar ist.
- **Sprache:** Mit mir auf Deutsch kommunizieren. Bild-/Video-Prompts auf Englisch (funktioniert mit den Modellen zuverlässiger), Skripte und Texte fürs Video auf Deutsch.

## 8. Vorhandene Dateien

- `brokey-prompt-bibliothek.md`: Baukasten mit CHARACTER-, STYLE- und AVOID-Blöcken, Mimik-Set, Humor-Boostern, Szenen-Templates, Video-Prompts, Fehlerbehebung und Checkliste. **Die Bausteine daraus sind die Quelle der Wahrheit für den Look.**

Vorgeschlagene Struktur (kannst du anpassen, aber bitte kurz begründen):

```
brokey/
├─ CLAUDE.md                  diese Datei
├─ README.md                  Kurzbeschreibung und Anleitung
├─ bausteine/                 aus der Prompt-Bibliothek (character, style, avoid, mimik, booster)
├─ videos/
│  └─ 01-abo-chaos/
│     ├─ skript.md
│     ├─ szenen.md
│     ├─ prompts.md
│     ├─ faktencheck.md
│     └─ untertitel.srt
├─ tools/                     Skripte der Pipeline
├─ .env.example
├─ .gitignore
└─ log.md                     was funktioniert hat, was nicht
```

## 9. Bereits vorhandenes Beispiel (Video 1)

**Thema:** Abo-Chaos ("Brokey zahlt 600 € im Jahr für Dinge, die er vergessen hat").
**Lerneffekt:** Kleine Abos wirken harmlos, summieren sich aber. Einmal im Monat den Kontoauszug prüfen.
**Rechenbeispiel:** 5 Abos à ca. 10 € = 50 € im Monat = 600 € im Jahr (vereinfachte Beispielpreise, im Video als "ungefähr" kennzeichnen).
**Szenen:** Hook (Panik vor Kontoauszug) → Setup (5 Abo-Karten um Brokey) → Der Haken (Münzen fliegen jeden Monat raus) → Die Rechnung → Lerneffekt (drei Abos durchstreichen) → Punchline (resignierter Blick) → Outro mit Disclaimer.

Nutze dieses Video als erstes Testbeispiel für die Pipeline.

## 10. Erste Aufgaben

1. Lies diese Datei und `brokey-prompt-bibliothek.md`.
2. Fasse in 3-5 Sätzen zusammen, was du verstanden hast, und stelle mir die offenen Fragen (Sprache/Tools, welche Generierungstools ich nutzen kann, Budget, Betriebssystem).
3. Lege die Ordnerstruktur und die Grunddateien an (`.gitignore`, `.env.example`, `README.md`, `log.md`).
4. Baue ein einfaches Tool, das aus einer Themen-Eingabe eine Video-Mappe (Skript, Szenenliste, Prompts, Faktencheck) als Markdown-Dateien erzeugt, und teste es mit dem Beispiel "Abo-Chaos".
5. Berichte mir kurz, was funktioniert und was als Nächstes sinnvoll wäre.
