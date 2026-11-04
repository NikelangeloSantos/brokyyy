#!/usr/bin/env python3
"""Brokey-Pipeline: aus einer Themen-Datei (thema.toml) eine Video-Mappe erzeugen.

Benutzung (aus dem Repo-Hauptordner):
    python3 tools/brokey.py neu 02 inflation --titel "Inflation frisst dein Geld"
    python3 tools/brokey.py baue videos/01-abo-chaos
    python3 tools/brokey.py pruefe-bausteine

Braucht nur Python 3.11 oder neuer, keine Zusatzpakete.
"""
from __future__ import annotations

import argparse
import ast
import operator
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BAUSTEINE = ROOT / "bausteine" / "bausteine.toml"
BIBLIOTHEK = ROOT / "brokey-prompt-bibliothek.md"
VORLAGE = ROOT / "tools" / "vorlage-thema.toml"

TEILE = ["hook", "setup", "geschichte", "rechnung", "lerneffekt", "punchline", "outro"]
WOERTER_PRO_SEKUNDE = 2.5  # ca. 150 Wörter/Minute, nur Schätzung
SRT_WOERTER_PRO_ZEILE = 7


# ---------------------------------------------------------------- Hilfen

def lade_toml(pfad: Path) -> dict:
    with open(pfad, "rb") as f:
        return tomllib.load(f)


def woerter(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg}


def rechne(ausdruck: str) -> float:
    """Sicheres Nachrechnen: nur Zahlen, + - * / und Klammern."""
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        raise ValueError(f"Nicht erlaubter Ausdruck: {ausdruck!r}")
    return ev(ast.parse(ausdruck.replace(",", "."), mode="eval"))


def zeit_srt(sek: float) -> str:
    ms = int(round(sek * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def fuer_tts(text: str) -> str:
    """Sprechertext für Text-to-Speech (z. B. ElevenLabs) oder eigene Aufnahme aufbereiten."""
    t = text.strip()
    t = re.sub(r"(\d)\s*€", r"\1 Euro", t).replace("€", "Euro")
    t = re.sub(r"(\d)\s*%", r"\1 Prozent", t)
    t = re.sub(r"[*_#`]", "", t)          # Markdown-Reste
    t = re.sub(r"\s+", " ", t)
    return t


ABKUERZUNGEN = ("ca.", "z.B.", "z. B.", "bzw.", "evtl.", "inkl.", "mind.", "max.", "Nr.")


def saetze_mit_zahlen(text: str, ganz: bool = False) -> list[str]:
    """Sätze mit Ziffern finden. ganz=True: Text nicht in Sätze zerlegen (Einblendtexte)."""
    if ganz:
        return [text.strip()] if re.search(r"\d", text) else []
    t = text.strip()
    for a in ABKUERZUNGEN:
        t = t.replace(a, a.replace(".", "\u0000"))
    saetze = [x.replace("\u0000", ".") for x in re.split(r"(?<=[.!?])\s+", t)]
    return [s for s in saetze if re.search(r"\d", s)]


# ---------------------------------------------------------------- Mappe

class Mappe:
    def __init__(self, ordner: Path):
        self.ordner = ordner
        self.b = lade_toml(BAUSTEINE)
        self.t = lade_toml(ordner / "thema.toml")
        self.v = self.t.get("video", {})
        self.szenen = self.t.get("szene", [])
        self.fehler: list[str] = []
        self.warnungen: list[str] = []
        self._timing()

    # --- Zeiten schätzen
    def _timing(self):
        start = 0.0
        for s in self.szenen:
            dauer = max(2.0, woerter(s.get("sprechertext", "")) / WOERTER_PRO_SEKUNDE)
            s["_start"], s["_ende"] = start, start + dauer
            start += dauer
        self.dauer = start

    # --- Prompts
    def mimik(self, key: str, ende: bool = False) -> str:
        m = self.b["mimik"]
        if key not in m:
            self.fehler.append(f"Unbekannte Mimik '{key}'. Erlaubt: {', '.join(k for k in m if not k.endswith('_ende'))}")
            return ""
        if ende and f"{key}_ende" in m:
            return f"{m[key]}, then {m[key + '_ende']}"
        return m[key]

    def booster(self, s: dict) -> list[str]:
        out = []
        for k in s.get("booster", []):
            if k not in self.b["booster"]:
                self.fehler.append(f"Szene '{s.get('name')}': unbekannter Booster '{k}'. Erlaubt: {', '.join(self.b['booster'])}")
            else:
                out.append(self.b["booster"][k])
        if s.get("running_gag"):
            out.append(self.b["booster"]["running_gag"])
        return out

    def bild_prompt(self, s: dict) -> str:
        basis = self.b["basis"]
        teile = [basis["character"], basis["style"], s.get("bild", "").strip().rstrip(".") + "."]
        teile.append(f"Expression: {self.mimik(s.get('mimik', ''))}.")
        b = self.booster(s)
        if b:
            teile.append("Humor: " + ", ".join(b) + ".")
        teile.append(basis["avoid"])
        return "\n".join(teile)

    def video_prompt(self, s: dict) -> str:
        v = self.b["video"]
        if s.get("aktion_frei"):
            aktion = s["aktion_frei"].strip()
        elif s.get("aktion"):
            aktion = self.b["aktion"].get(s["aktion"], "")
            if not aktion:
                self.fehler.append(f"Szene '{s.get('name')}': unbekannte Aktion '{s['aktion']}'. Erlaubt: {', '.join(self.b['aktion'])}")
        else:
            aktion = ""
            self.warnungen.append(f"Szene '{s.get('name')}': keine Aktion angegeben (aktion oder aktion_frei).")
        schuss = s.get("video_schuss") or s.get("bild", "")
        teile = [v["intro"], schuss.strip().rstrip(".") + ".",
                 f"Expression: {self.mimik(s.get('mimik', ''), ende=True)}.", aktion,
                 v["style"], v["sound"], v["avoid"]]
        return "\n".join(t for t in teile if t)

    # --- Prüfungen
    def pruefe(self):
        b, v = self.b["pruefung"], self.v
        alle_texte = " ".join(
            " ".join([s.get("sprechertext", ""), s.get("einblendtext", ""), s.get("bild", ""),
                      s.get("aktion_frei", ""), s.get("video_schuss", "")]) for s in self.szenen
        ) + " " + v.get("caption", "") + " " + " ".join(v.get("hashtags", []))

        for marke in b["markennamen"]:
            if re.search(rf"(?<![\w-]){re.escape(marke)}(?![\w-])", alle_texte, re.IGNORECASE):
                self.fehler.append(f"Markenname gefunden: '{marke}' – bitte durch neutrale Beschreibung ersetzen.")

        if any("TODO" in str(x) for x in [self.v, self.szenen]):
            self.warnungen.append("Es stehen noch TODO-Platzhalter in thema.toml.")

        n = sum(woerter(s.get("sprechertext", "")) for s in self.szenen)
        self.wortzahl = n
        if not b["woerter_min"] <= n <= b["woerter_max"]:
            self.warnungen.append(f"Sprechertext hat {n} Wörter (Ziel {b['woerter_min']}-{b['woerter_max']}).")

        teile = [s.get("teil") for s in self.szenen]
        for t in teile:
            if t not in TEILE:
                self.fehler.append(f"Unbekannter Teil '{t}'. Erlaubt: {', '.join(TEILE)}")
        for pflicht in ["hook", "rechnung", "lerneffekt", "outro"]:
            if pflicht not in teile:
                self.warnungen.append(f"Kein Szenen-Teil '{pflicht}' – gehört zum Standard-Aufbau.")
        if teile and teile[0] != "hook":
            self.warnungen.append("Die erste Szene ist kein Hook.")
        if self.szenen and self.szenen[0]["_ende"] > 3.5:
            self.warnungen.append(f"Hook-Sprechertext dauert ca. {self.szenen[0]['_ende']:.1f} s (Ziel: max. ~3 s).")

        disc = v.get("disclaimer", "")
        if not disc:
            self.fehler.append("Kein Disclaimer in [video] gesetzt.")
        elif not any(disc.lower() in s.get("einblendtext", "").lower() for s in self.szenen if s.get("teil") == "outro"):
            self.fehler.append(f"Disclaimer '{disc}' fehlt im Einblendtext der Outro-Szene.")

        if not any(s.get("running_gag") for s in self.szenen):
            self.fehler.append("Running Gag (fliegende Münze) kommt in keiner Szene vor.")

        for s in self.szenen:
            if len(s.get("booster", [])) > 2:
                self.warnungen.append(f"Szene '{s.get('name')}': mehr als 2 Humor-Booster.")
            if re.search(r"\d", s.get("bild", "")):
                self.warnungen.append(f"Szene '{s.get('name')}': Ziffern im Bild-Prompt – Bildmodelle schreiben dann evtl. Text ins Bild.")

        self.rechen_ergebnisse = []
        for r in self.t.get("rechnung", []):
            try:
                ist = rechne(r["ausdruck"])
                ok = abs(ist - float(r["ergebnis"])) < 0.005
            except Exception as e:  # noqa: BLE001
                ist, ok = f"Fehler: {e}", False
            self.rechen_ergebnisse.append((r, ist, ok))
            if not ok:
                self.fehler.append(f"Rechnung stimmt nicht: {r['ausdruck']} = {ist}, angegeben {r['ergebnis']}.")

        if self.dauer < 61:
            self.warnungen.append(f"Geschätzte Sprechdauer {self.dauer:.0f} s – für >1 Minute evtl. zu kurz (echte Dauer nach Vertonung prüfen).")

    # --- Dateien schreiben
    def kopf(self, titel: str) -> str:
        v = self.v
        return f"# {titel}: {v.get('titel', '')}\n\n_Automatisch erzeugt aus `thema.toml` – Änderungen bitte dort machen und neu bauen._\n\n"

    def schreibe(self):
        v, o = self.v, self.ordner
        # skript.md
        z = [self.kopf("Skript"),
             f"- **Thema:** {v.get('thema', '')}\n- **Lerneffekt:** {v.get('lerneffekt', '')}\n",
             f"- **Zielgruppe:** {v.get('zielgruppe', '')}\n- **Ton:** {v.get('ton', '')}\n",
             f"- **Wörter:** {self.wortzahl} · **geschätzte Dauer:** ca. {self.dauer:.0f} s\n\n"]
        for s in self.szenen:
            z.append(f"## {s.get('name', '')} ({s.get('teil', '')}, ca. {s['_start']:.0f}–{s['_ende']:.0f} s)\n\n")
            z.append(f"**Erzähler:** {s.get('sprechertext', '').strip()}\n\n")
            if s.get("einblendtext"):
                z.append(f"**Einblendung:** {s['einblendtext']}\n\n")
        (o / "skript.md").write_text("".join(z), encoding="utf-8")

        # szenen.md
        z = [self.kopf("Szenenliste")]
        for i, s in enumerate(self.szenen, 1):
            booster = ", ".join(s.get("booster", [])) or "–"
            if s.get("running_gag"):
                booster += " + running_gag"
            z.append(f"## {i}. {s.get('name', '')} ({s.get('teil', '')}, ca. {s['_start']:.0f}–{s['_ende']:.0f} s)\n\n"
                     f"- **Bild:** {s.get('bild_de') or s.get('bild', '')}\n"
                     f"- **Mimik:** {s.get('mimik', '')}\n- **Humor-Booster:** {booster}\n"
                     f"- **Aktion (Video):** {s.get('aktion') or ('frei' if s.get('aktion_frei') else '–')}\n"
                     f"- **Sprechertext:** {s.get('sprechertext', '').strip()}\n"
                     f"- **Einblendtext:** {s.get('einblendtext', '') or '–'}\n\n")
        (o / "szenen.md").write_text("".join(z), encoding="utf-8")

        # prompts.md
        z = [self.kopf("Prompts"),
             f"Referenzbild bei jedem Prompt mit hochladen: `{v.get('referenzbild', 'TODO')}`\n\n"]
        for i, s in enumerate(self.szenen, 1):
            z.append(f"## {i}. {s.get('name', '')}\n\n### Bild\n\n```\n{self.bild_prompt(s)}\n```\n\n"
                     f"### Video (Bild-zu-Video, Startbild = Bild oben)\n\n```\n{self.video_prompt(s)}\n```\n\n")
        (o / "prompts.md").write_text("".join(z), encoding="utf-8")

        # faktencheck.md
        z = [self.kopf("Faktencheck"),
             "Alles hier vor dem Upload selbst prüfen und abhaken. Automatisch gefunden heißt **nicht** geprüft.\n\n",
             "## Rechnungen (automatisch nachgerechnet)\n\n"]
        for r, ist, ok in self.rechen_ergebnisse:
            z.append(f"- [ ] {'✅' if ok else '❌'} {r.get('beschreibung', '')}: `{r['ausdruck']}` = {ist} "
                     f"(angegeben: {r['ergebnis']} {r.get('einheit', '')}) – {r.get('hinweis', '')}\n")
        if not self.rechen_ergebnisse:
            z.append("- keine Rechnungen eingetragen\n")
        z.append("\n## Sätze mit Zahlen (aus Sprecher- und Einblendtext)\n\n")
        for s in self.szenen:
            for satz in saetze_mit_zahlen(s.get("sprechertext", "")) + saetze_mit_zahlen(s.get("einblendtext", ""), ganz=True):
                z.append(f"- [ ] ({s.get('name', '')}) {satz}\n")
        z.append("\n## Behauptungen und Annahmen\n\n")
        for f in self.t.get("fakt", []):
            z.append(f"- [ ] **{f.get('status', 'offen')}:** {f.get('text', '')}"
                     + (f" – Quelle: {f['quelle']}" if f.get("quelle") else "") + "\n")
        if not self.t.get("fakt"):
            z.append("- keine eingetragen\n")
        (o / "faktencheck.md").write_text("".join(z), encoding="utf-8")

        # untertitel.srt (Sprechertext) und einblendungen.srt (Einblendtexte)
        srt, nr = [], 1
        for s in self.szenen:
            w = re.findall(r"\S+", s.get("sprechertext", ""))
            if not w:
                continue
            stuecke = [w[i:i + SRT_WOERTER_PRO_ZEILE] for i in range(0, len(w), SRT_WOERTER_PRO_ZEILE)]
            t = s["_start"]
            for st in stuecke:
                d = (s["_ende"] - s["_start"]) * len(st) / len(w)
                srt.append(f"{nr}\n{zeit_srt(t)} --> {zeit_srt(t + d)}\n{' '.join(st)}\n")
                t += d
                nr += 1
        (o / "untertitel.srt").write_text("\n".join(srt), encoding="utf-8")
        ein = [f"{i}\n{zeit_srt(s['_start'])} --> {zeit_srt(s['_ende'])}\n{s['einblendtext']}\n"
               for i, s in enumerate([s for s in self.szenen if s.get("einblendtext")], 1)]
        (o / "einblendungen.srt").write_text("\n".join(ein), encoding="utf-8")

        # voiceover.txt
        vo = "\n\n".join(fuer_tts(s.get("sprechertext", "")) for s in self.szenen if s.get("sprechertext"))
        (o / "voiceover.txt").write_text(vo + "\n", encoding="utf-8")

        # checkliste.md (Schritt 10, immer manuell)
        auto = "\n".join(f"  - ❌ {x}" for x in self.fehler) + ("\n" if self.fehler else "")
        auto += "\n".join(f"  - ⚠️ {x}" for x in self.warnungen) + ("\n" if self.warnungen else "")
        tags = " ".join(v.get("hashtags", []))
        (o / "checkliste.md").write_text(f"""{self.kopf("Veröffentlichungs-Checkliste")}Diese Liste hakst **du** vor dem Upload ab. Die Pipeline veröffentlicht nichts.

Automatische Prüfung beim letzten Bauen: {"keine Probleme gefunden" if not (self.fehler or self.warnungen) else ""}
{auto}
## Inhalt
- [ ] Disclaimer „{v.get('disclaimer', '')}“ ist im Video sichtbar
- [ ] Alle Punkte in `faktencheck.md` geprüft
- [ ] Preise/Renditen als Beispiel bzw. „ungefähr“ gekennzeichnet
- [ ] Keine Kauf- oder Anlageempfehlung, kein Gewinnversprechen
- [ ] Genau ein klarer Lerneffekt: {v.get('lerneffekt', '')}

## Bild und Ton
- [ ] Gleiches Referenzbild benutzt, Brokey sieht aus wie immer (rote Mütze)
- [ ] Papier füllt das ganze Bild, kein Tisch, kein Rand, keine Hände
- [ ] Kein Text/Kauderwelsch in generierten Bildern
- [ ] Keine Markennamen oder Logos (auch nicht in Untertiteln)
- [ ] Running Gag (fliegende Münze) drin
- [ ] Hook in den ersten 3 Sekunden ohne Ton verständlich

## TikTok (aktuelle Regeln in der App prüfen!)
- [ ] **KI-generierte Inhalte gekennzeichnet** (Bilder/Clips aus Flow, Stimme aus ElevenLabs) – aktuelle TikTok-Vorgaben dazu geprüft
- [ ] Videolänge erfüllt die aktuellen Bedingungen (z. B. Creator Rewards) – in der App geprüft
- [ ] Caption: {v.get('caption', '')}
- [ ] Hashtags: {tags}
- [ ] Ergebnis in `log.md` eingetragen
""", encoding="utf-8")


# ---------------------------------------------------------------- Befehle

def cmd_baue(args):
    ordner = Path(args.ordner).resolve()
    if not (ordner / "thema.toml").exists():
        sys.exit(f"Keine thema.toml in {ordner}")
    m = Mappe(ordner)
    m.pruefe()
    m.schreibe()
    print(f"Mappe gebaut: {ordner.relative_to(ROOT) if ordner.is_relative_to(ROOT) else ordner}")
    print(f"  {len(m.szenen)} Szenen · {m.wortzahl} Wörter · ca. {m.dauer:.0f} s")
    for f in m.fehler:
        print(f"  FEHLER:  {f}")
    for w in m.warnungen:
        print(f"  WARNUNG: {w}")
    if not (m.fehler or m.warnungen):
        print("  Alle automatischen Prüfungen ok.")
    return 1 if m.fehler else 0


def cmd_neu(args):
    slug = re.sub(r"[^a-z0-9]+", "-", args.slug.lower()).strip("-")
    ordner = ROOT / "videos" / f"{int(args.nummer):02d}-{slug}"
    ziel = ordner / "thema.toml"
    if ziel.exists():
        sys.exit(f"{ziel} gibt es schon – nichts überschrieben.")
    ordner.mkdir(parents=True, exist_ok=True)
    text = VORLAGE.read_text(encoding="utf-8")
    text = text.replace("{{NUMMER}}", f"{int(args.nummer):02d}").replace("{{SLUG}}", slug)
    text = text.replace("{{TITEL}}", args.titel or "TODO")
    ziel.write_text(text, encoding="utf-8")
    print(f"Angelegt: {ziel.relative_to(ROOT)}\nJetzt ausfüllen und dann: python3 tools/brokey.py baue {ordner.relative_to(ROOT)}")


def cmd_pruefe_bausteine(_args):
    b = lade_toml(BAUSTEINE)
    bib = BIBLIOTHEK.read_text(encoding="utf-8")
    fehlt = []
    for gruppe, werte in b.items():
        if gruppe == "pruefung":
            continue
        for k, text in werte.items():
            if k == "intro":
                continue
            if text not in bib:
                fehlt.append(f"{gruppe}.{k}")
    if fehlt:
        print("Diese Bausteine stehen nicht wörtlich in der Bibliothek (bitte abgleichen):")
        for f in fehlt:
            print("  -", f)
        return 1
    print("Alle Bausteine stimmen wörtlich mit brokey-prompt-bibliothek.md überein.")
    return 0


def main():
    p = argparse.ArgumentParser(description="Brokey-Pipeline")
    sub = p.add_subparsers(dest="befehl", required=True)
    b = sub.add_parser("baue", help="Mappe aus videos/<ordner>/thema.toml erzeugen")
    b.add_argument("ordner")
    b.set_defaults(f=cmd_baue)
    n = sub.add_parser("neu", help="Neuen Video-Ordner mit leerer thema.toml anlegen")
    n.add_argument("nummer")
    n.add_argument("slug")
    n.add_argument("--titel")
    n.set_defaults(f=cmd_neu)
    k = sub.add_parser("pruefe-bausteine", help="Bausteine gegen die Prompt-Bibliothek prüfen")
    k.set_defaults(f=cmd_pruefe_bausteine)
    a = p.parse_args()
    sys.exit(a.f(a) or 0)


if __name__ == "__main__":
    main()
