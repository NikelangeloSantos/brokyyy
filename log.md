# Log: was funktioniert hat, was nicht

| Datum | Was (Prompt/Schritt) | Ergebnis 1-5 | Notiz |
|---|---|---|---|
| 2026-11-04 | Pipeline-Grundgerüst angelegt, Test mit 01-abo-chaos | – | Mappe wird erzeugt, Prompts noch nicht in Flow getestet |
| 2026-11-04 | Erster Testschnitt 01-abo-chaos mit Referenzbildern als Platzhalter, ohne Stimme | – | Ablauf klappt (65 s). Einblendung oben verdeckt bei Nahaufnahmen den Kopf |
| 2026-11-04 | Referenzbilder gesichtet | – | Schrift im Bild bei: brokey-holding-large-receipt ("TOTAL"), character-drawing-marker-line ("RENT BILLS"), two-brokeys-comparing ("SALE"?). person-using-laptop-at-desk hat dunklen Hintergrund statt Papier. person-smoking-cigarette: Rauchen für junge Zielgruppe vermeiden |
| 2026-11-04 | Auf 35-50 s umgestellt, schnelle Schnitte (Hook 0,6 s), Abo-Chaos auf 111 Wörter gekürzt | – | Testschnitt 47 s, noch ohne Stimme |
| 2026-11-04 | Vertonung mit Leander (eleven_multilingual_v2, speed 1.05), 651 Zeichen | – | 49 s mit Stimme, Szenenlängen folgen der Sprechdauer, Lautheit auf -14 LUFS normalisiert. API-Schlüssel hat kein voices_read (Stimmenliste nicht lesbar), TTS geht |
| 2026-11-04 | Bibliothek + eingang/ + Katalog (30 Bilder beschrieben), mehrere Medien pro Szene mit harten Schnitten | – | Abo-Chaos 49 s mit Schnellschnitt aus 3 Bildern im Hook. Offen: Test, dass Clips beim Wiederauftauchen weiterlaufen (mit echten Clips prüfen) |
| 2026-11-04 | 35 neue Medien (18 Clips, 17 Bilder) einsortiert und beschrieben; Abo-Chaos mit Clips neu geschnitten | – | Clips nur 360x640 -> werden hochskaliert (Lanczos + Schärfen), höhere Auflösung aus Flow wäre besser. Außerhalb des Hooks laufen mehrere Medien jetzt nacheinander |
| 2026-11-05 | 02 Impulskäufe: 9 Szenen, Leander, 598 Zeichen, 42 s, output/impulskaeufe.mp4 | – | Keine eigenen Clips zu den Szenen -> Ersatz aus Bibliothek (5 Standbilder mit langsamem Zoom, 4 Clips). Pausen vor Pointen als Stille eingefügt (Pausen-Syntax der API nicht verifiziert). Untertitel Carlito 64, 2x35 Zeichen |
