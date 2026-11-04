# Brokey Prompt-Bibliothek

Wiederverwendbare Prompts für Bilder und Videos mit der Stickman-Figur **Brokey** (Kanal: Finanzen humorvoll erklärt).
Die Prompts sind auf Englisch, weil Bild- und Videomodelle damit meist zuverlässiger arbeiten. Kommentare sind auf Deutsch.

## So benutzt du die Bibliothek

Jeder Prompt wird aus Bausteinen zusammengesetzt:

```
[CHARACTER] + [STYLE] + [SZENE] + [MIMIK] + [HUMOR-BOOSTER] + [AVOID]
```

1. Lade immer das Referenzbild von Brokey mit hoch (gleiche Datei für alle Videos).
2. Kopiere CHARACTER und STYLE (Abschnitt 1) an den Anfang.
3. Hänge eine Szene (Abschnitt 4) und eine Mimik (Abschnitt 2) an.
4. Füge 1-2 Humor-Booster (Abschnitt 3) hinzu. Nicht mehr, sonst wird das Bild überladen.
5. Für Videos nutze die Bausteine aus Abschnitt 5.

Hinweis: Oberflächen und Funktionen von Flow ändern sich. Schau kurz nach, wie Referenzbilder und Bild-zu-Video aktuell heißen.

---

## 1. Basis-Bausteine (immer vorne einsetzen)

### CHARACTER
```
Brokey: a stick figure with a big round white head, thin black marker limbs, a red knit beanie with a fluffy pom-pom, heavy half-closed tired eyes with dark eye bags, a small flat mouth. Always exactly the same design as the reference image.
```

### STYLE (Papier-Look)
```
Hand-drawn black marker doodle on a white sheet of paper that fills the entire frame edge to edge, visible paper fibers, fine grain, faint creases, slightly wobbly marker lines, flat red color on the beanie, small flat color accents only where needed (gold for coins, brown for wallet), no table, no paper edges, no hands, aspect ratio 9:16.
```

### AVOID (ans Ende)
```
Avoid: text, letters, numbers, watermark, logos, brand names, extra characters, hands, realistic style, 3D render, gradients, photo background.
```

Warum "no text"? Bildmodelle machen bei Schrift oft Fehler. Texte und Zahlen fügst du später im Schnittprogramm ein.

---

## 2. Mimik-Set (6 Gesichter)

Eine Mimik pro Szene reicht. Das Gesicht trägt den Humor.

| Name | Einsatz | Prompt-Baustein |
|---|---|---|
| Gelangweilt (Standard) | Erzähl-Szenen, Alltag | `tired half-closed eyes, flat straight mouth, deadpan` |
| Panik | Hook, Rechnung, Schock | `eyes wide open and bulging, tiny pupils, mouth wide open in a scream, sweat drops flying off his head` |
| Selbstsicher-ahnungslos | Vor dem Fehler | `smug proud grin, one eyebrow raised, chest puffed out, completely unaware` |
| Erleuchtung | Lerneffekt, Punchline | `sudden realization, eyebrows raised high, eyes sparkling, a lightbulb drawn above his head` |
| Resigniert | Nach dem Fehler, Outro | `looks straight at the viewer, dead-eyed deadpan stare, slow sigh, slumped shoulders` |
| Hoffnung, dann Absturz | Gag mit Wendung | `eyes shining with hope, hands clasped, tiny smile` (Start) → `smile collapsing, eyes drained of color, jaw dropping` (Ende) |

---

## 3. Humor-Booster (je 1-2 pro Bild)

Hier steckt das, was Bilder lebendig und lustig macht.

| Booster | Baustein |
|---|---|
| Übertriebene Verformung | `squash and stretch, body stretched extremely tall and thin in panic` / `body squashed flat like a pancake` |
| Bewegungslinien | `hand-drawn black motion lines, impact stars, speed streaks, sweat drops flying` |
| Lebendige Objekte | `the gold coin has tiny legs and runs away, looking back with a smug face` |
| Größen-Gag | `tiny Brokey standing next to a gigantic receipt that towers over him` |
| Absurde Requisite | `wearing a ridiculously oversized helmet while holding a tiny umbrella` |
| Vierte Wand | `looks straight at the viewer with a deadpan expression, as if asking "really?"` |
| Marker-Spotlight | `dramatic marker-drawn spotlight rays pointing at him, like a courtroom drama` |
| Rand-Kritzeleien | `small doodled arrows, circles, stars and scribbles around him as if a student drew them in a notebook margin` |
| Engel-Teufel-Gag | `a tiny doodled devil with horns on one shoulder and a tiny angel with a halo on the other, both arguing` |
| Dramatischer Zusammenbruch | `Brokey melting into a puddle on the paper, only the beanie floating on top` |
| Zu viel des Guten | `way too many coins, shopping bags and cards piled on his head, he is barely visible underneath` |
| Running Gag | `one gold coin flying away in the background` (kommt in JEDEM Video vor, Wiedererkennung!) |

Faustregel: Der Humor kommt aus **Kontrast** (ruhiger Typ trifft auf übertriebenes Chaos). Brokey bleibt trocken, die Welt um ihn herum spielt verrückt.

---

## 4. Szenen-Templates (Bilder)

Platzhalter in `[ECKIGEN KLAMMERN]` austauschen.

### 4.1 Hook-Panik
```
[CHARACTER] [STYLE] Brokey stares at a very long bank statement paper that unrolls to the floor, [MIMIK: Panik], gold coins flying out of his wallet, sweat drops, black motion lines. [AVOID]
```

### 4.2 Gehaltstag
```
[CHARACTER] [STYLE] Brokey stands under a rain of gold coins, arms wide open, [MIMIK: Selbstsicher-ahnungslos]. In the background the coins already run away on tiny legs toward bills labeled only with simple icons (house, phone, cart). [AVOID]
```

### 4.3 Impulskauf
```
[CHARACTER] [STYLE] Brokey is dragged across the paper by a huge shopping bag that has a mischievous grin, a tiny doodled devil on his shoulder whispers to him, [MIMIK: Hoffnung, dann Absturz]. [AVOID]
```

### 4.4 Abo-Chaos
```
[CHARACTER] [STYLE] A big doodled octopus made of subscription cards (simple icons: play button, music note, cloud, dumbbell, game controller) wraps its tentacles around Brokey's wallet, Brokey sits on the sofa unaware, [MIMIK: Gelangweilt]. [AVOID]
```

### 4.5 Inflation
```
[CHARACTER] [STYLE] Brokey holds up a single gold coin that is visibly shrinking like laundry that came out of a washing machine too hot, [MIMIK: Resigniert]. Next to him an empty shopping cart that got bigger. [AVOID]
```

### 4.6 Zinseszins (Schneeball)
```
[CHARACTER] [STYLE] A small gold coin rolls down a long paper hill and grows into a gigantic snowball made of coins, Brokey runs in front of it in panic, [MIMIK: Panik], calendar pages fly through the air. [AVOID]
```

### 4.7 Steuererklärung
```
[CHARACTER] [STYLE] Brokey is buried up to his neck under a mountain of paper forms, folders and receipts, only his beanie and tired eyes stick out, one paper airplane flies away, [MIMIK: Resigniert]. [AVOID]
```

### 4.8 Sparer vs. Spender
```
[CHARACTER] [STYLE] Split composition on one sheet: on the left a calm Brokey with a gray beanie sits next to a neat small tower of coins, on the right a chaotic Brokey with a red beanie surrounded by shopping bags and empty wallets, both look at each other, [MIMIK: Selbstsicher-ahnungslos / Gelangweilt]. [AVOID]
```

### 4.9 Mythen-Check
```
[CHARACTER] [STYLE] Brokey holds a giant magnifying glass over a doodled cracked "myth" balloon that is about to pop, marker-drawn spotlight rays, [MIMIK: Erleuchtung]. [AVOID]
```

### 4.10 Lerneffekt / Punchline
```
[CHARACTER] [STYLE] Brokey with a lightbulb above his head draws a thick marker line through three crossed-out items, tiny confetti made of marker dots, [MIMIK: Erleuchtung]. [AVOID]
```

### 4.11 Outro
```
[CHARACTER] [STYLE] Brokey waves tiredly toward the viewer, one gold coin falls at his feet and rolls off, [MIMIK: Resigniert]. [AVOID]
```

---

## 5. Video-Prompts (Bild-zu-Video)

Ein Videoclip ist besser als viele Einzelbilder, wenn du Bewegung brauchst. Nimm das fertige Standbild als Startbild.

### Aufbau eines Video-Prompts
```
[SHOT: was ist zu sehen] + [AKTION in Phasen] + [KAMERA] + [VIDEO-STYLE] + [SOUND] + [AVOID]
```

### VIDEO-STYLE
```
Stop-motion feel at about 8 to 12 frames per second, hand-drawn line boil effect (lines slightly wobble each frame), the paper background stays perfectly static and fills the entire frame, camera locked flat top-down, no hands, no tools.
```

### SOUND
```
No speech, no music. Only subtle cartoon sound effects: coin clink, boing, whoosh, paper rustle.
```
Die Stimme (Erzähler) kommt später im Schnitt dazu, damit sie immer gleich klingt.

### Aktions-Bausteine (mit Zeitstruktur)

| Name | Baustein |
|---|---|
| Panik-Zittern | `0-2s: Brokey freezes. 2-5s: he starts shaking uncontrollably, eyes bulging, sweat drops flying outward. 5-8s: he collapses backwards in slow motion.` |
| Münze flieht | `0-3s: the gold coin wobbles on the paper. 3-5s: it grows tiny legs and sprints away. 5-8s: Brokey slowly turns his head and watches it go, deadpan.` |
| Wallet-Schock | `0-2s: Brokey opens his wallet. 2-4s: a single moth flies out, nothing else. 4-8s: he stares at the viewer, one tear rolls down.` |
| Aufblas-Gag | `0-3s: Brokey's head slowly inflates like a balloon as the bill grows. 3-5s: it hits the paper edge. 5-8s: it deflates with a loud pffff and he lies flat.` |
| Facepalm | `0-2s: Brokey realizes his mistake. 2-3s: slow-motion facepalm. 3-6s: the beanie falls over his eyes. 6-8s: a coin drops onto the ground next to him.` |
| Schock-Zoom (optional) | `quick punch-in zoom on his face at second 3, then back to normal` (bricht die feste Kamera, nur gezielt einsetzen) |
| Auflösen | `Brokey melts into a puddle on the paper, only the beanie remains floating on top.` |

### Beispiel für ein fertiges Video
```
Use the character Brokey from the reference image. He stands on a white sheet of paper that fills the entire frame and opens his empty wallet. 0-2s: he looks inside, hopeful. 2-4s: a single moth flies out. 4-6s: his face drains of color, eyes widen. 6-8s: a gold coin with tiny legs runs across the paper and out of frame while Brokey watches, deadpan. Stop-motion feel at about 10 frames per second, hand-drawn line boil effect, paper background perfectly static, camera locked flat top-down. No speech, no music, only subtle cartoon sound effects. Avoid: text, letters, extra characters, hands, realistic style, 3D.
```

---

## 6. Hook-Bilder (erste 3 Sekunden)

Der Hook-Frame muss ohne Ton verständlich und übertrieben sein. Gute Zutaten:

- Große Mimik in der Bildmitte (Gesicht füllt mind. 40 % des Bildes)
- Ein klarer "Fehler" oder Schock (Rechnung, leeres Portemonnaie, verschwindende Münzen)
- Maximal 3 Elemente im Bild
- Bewegungsrichtung in den ersten 1-2 Sekunden (zittern, fliegen, fallen)

Beispiel:
```
[CHARACTER] [STYLE] Extreme close-up of Brokey's face filling the frame, eyes bulging, mouth wide open in a scream, a giant receipt unrolling in front of him, a coin flying past his head, black motion lines, sweat drops. [AVOID]
```

---

## 7. Fehler beheben

| Problem | Lösung |
|---|---|
| Figur sieht anders aus | Referenzbild erneut hochladen und `exactly the same design as the reference image, do not change the character` ergänzen |
| Papier wirkt wie Tisch mit Rand | `seamless paper background, texture continues beyond the frame, no edges, no shadows at the borders` |
| Papier wirkt zu glatt | `more pronounced paper fibers, faint fold lines, photographed in daylight` |
| Text im Bild ist Kauderwelsch | Text komplett streichen und im Schnitt einfügen |
| Hintergrund wackelt im Video | `background perfectly static`, im Zweifel Figur freistellen und auf festes Papierbild legen |
| Bild zu überladen | Nur 1 Humor-Booster, maximal 3 Objekte |
| Zu wenig Witz | Kontrast verstärken: Brokey ruhig, Chaos groß. Mimik anpassen (Abschnitt 2) |
| Hände tauchen auf | `no hands, no fingers, no human body parts` ergänzen |

---

## 8. Leere Vorlage (kopieren und ausfüllen)

```
[CHARACTER]
[STYLE]
Scene: [WAS PASSIERT]
Expression: [MIMIK-BAUSTEIN]
Humor: [BOOSTER 1], [BOOSTER 2]
Props: [OBJEKTE, MAX. 3]
[AVOID]
```

Für Video zusätzlich:
```
Action: [AKTION IN PHASEN]
[VIDEO-STYLE]
[SOUND]
```

---

## 9. Konsistenz-Checkliste vor jedem Upload

- [ ] Gleiches Referenzbild benutzt
- [ ] CHARACTER- und STYLE-Block unverändert kopiert
- [ ] Beanie bleibt rot (Signalfarbe des Kanals)
- [ ] Papier füllt das ganze Bild, kein Tisch und kein Rand
- [ ] Kein Text im Bild
- [ ] Keine Markennamen oder Logos
- [ ] Max. 1-2 Humor-Booster
- [ ] Running Gag (fliegende Münze) enthalten
- [ ] Hook-Frame klar und übertrieben

---

## 10. Vorschlag für die GitHub-Struktur

```
brokey-prompts/
├─ README.md            Kurzbeschreibung des Projekts
├─ bausteine.md         Abschnitt 1-3 (CHARACTER, STYLE, Mimik, Booster)
├─ szenen.md            Abschnitt 4 (Szenen-Templates)
├─ video.md             Abschnitt 5 (Video-Prompts)
├─ videos/
│  ├─ 01-abo-chaos.md   Skript + verwendete Prompts pro Video
│  └─ 02-...
└─ log.md               Was funktioniert hat / was nicht
```

Mit einer `log.md` hältst du fest, welche Prompts gute Ergebnisse geliefert haben (Tabelle: Datum, Prompt, Ergebnis 1-5, Notiz). Das spart dir später viel Zeit.

Hinweis: Lege in dem Repo keine Zugangsdaten, API-Schlüssel oder persönlichen Daten ab. Bei einem öffentlichen Repo sieht jeder deine Prompts.
