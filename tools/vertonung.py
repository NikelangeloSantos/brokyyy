#!/usr/bin/env python3
"""Vertonung: Sprechertext jeder Szene per ElevenLabs in medien/vo-NN.mp3 umwandeln.

Benutzung (aus dem Repo-Hauptordner):
    python3 tools/vertonung.py videos/01-abo-chaos            # zeigt Zeichenzahl, fragt vor dem Senden
    python3 tools/vertonung.py videos/01-abo-chaos --ja       # ohne Rückfrage
    python3 tools/vertonung.py videos/01-abo-chaos --neu 03   # nur Szene 03 neu erzeugen

Stimme, Modell und Stimm-Einstellungen stehen in bausteine/stimme.toml (kein Geheimnis).
Der API-Schlüssel NUR aus der Umgebungsvariable ELEVENLABS_API_KEY oder der lokalen .env
(steht in .gitignore). In der Cloud-Umgebung setzt der Netzwerk-Proxy den Schlüssel selbst ein,
dann darf die Variable leer bleiben.

Schnittstelle laut ElevenLabs-Doku (geprüft 2026-11-04,
https://elevenlabs.io/docs/api-reference/text-to-speech/convert):
    POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128
    Header xi-api-key, JSON: text, model_id, voice_settings, previous_text, next_text
Jede Anfrage verbraucht Zeichen-Guthaben in deinem ElevenLabs-Konto.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brokey import PAUSE, ROOT, Mappe, fuer_tts  # noqa: E402

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
STANDARD_MODELL = "eleven_multilingual_v2"
STIMME = ROOT / "bausteine" / "stimme.toml"


def lade_env():
    """Einfache .env-Unterstützung ohne Zusatzpaket. Echte Umgebungsvariablen haben Vorrang."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for zeile in env.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#") or "=" not in zeile:
            continue
        k, v = zeile.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def tts(text: str, schluessel: str, stimme: str, modell: str, vorher: str, nachher: str,
        einstellungen: dict) -> bytes:
    body = {"text": text, "model_id": modell}
    if einstellungen:
        body["voice_settings"] = einstellungen
    if vorher:
        body["previous_text"] = vorher
    if nachher:
        body["next_text"] = nachher
    req = urllib.request.Request(
        API.format(voice_id=stimme), data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", "Accept": "audio/mpeg",
             **({"xi-api-key": schluessel} if schluessel else {})})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        sys.exit(f"ElevenLabs hat mit {e.code} geantwortet: {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"ElevenLabs nicht erreichbar ({e.reason}). Netzwerkzugriff auf api.elevenlabs.io prüfen.")


PAUSE_SEKUNDEN = 0.45


def verbinde_mit_pausen(stuecke: list[Path], ziel: Path):
    """Audio-Stücke hintereinander, dazwischen jeweils PAUSE_SEKUNDEN Stille."""
    eingabe, ketten = [], []
    for i, x in enumerate(stuecke):
        eingabe += ["-i", str(x)]
        if i:
            eingabe += ["-f", "lavfi", "-t", str(PAUSE_SEKUNDEN), "-i", "anullsrc=r=44100:cl=mono"]
    anzahl = len(stuecke) * 2 - 1
    f = "".join(f"[{i}:a]aresample=44100,aformat=channel_layouts=mono[x{i}];" for i in range(anzahl))
    f += "".join(f"[x{i}]" for i in range(anzahl)) + f"concat=n={anzahl}:v=0:a=1[out]"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *eingabe, "-filter_complex", f,
                        "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", str(ziel)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg-Fehler beim Verbinden:\n{r.stderr}")


def main():
    p = argparse.ArgumentParser(description="Voiceover mit ElevenLabs erzeugen")
    p.add_argument("ordner")
    p.add_argument("--ja", action="store_true", help="ohne Rückfrage senden")
    p.add_argument("--neu", nargs="*", metavar="NN", help="diese Szenen neu erzeugen (ohne Angabe: alle)")
    p.add_argument("--tempo", type=float, help="Sprechtempo, z. B. 1.1 (1.0 = normal)")
    p.add_argument("--medien", help="Ordner für die Audiodateien (Standard: <video>/medien)")
    p.add_argument("--stimme", help="andere voice_id als in bausteine/stimme.toml")
    p.add_argument("--stabilitaet", type=float, help="0-1, niedriger = lebendiger (Standard der Stimme)")
    a = p.parse_args()

    lade_env()
    cfg = tomllib.loads(STIMME.read_text(encoding="utf-8")) if STIMME.exists() else {}
    schluessel = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    stimme = a.stimme or os.environ.get("ELEVENLABS_VOICE_ID", "").strip() or cfg.get("voice_id", "")
    modell = os.environ.get("ELEVENLABS_MODEL_ID", "").strip() or cfg.get("model_id") or STANDARD_MODELL
    if not stimme:
        sys.exit("Keine Stimme: voice_id in bausteine/stimme.toml eintragen.")
    if not schluessel:
        print("Hinweis: kein ELEVENLABS_API_KEY gesetzt – nutze den Schlüssel des Netzwerk-Proxys (Cloud).")

    ordner = Path(a.ordner).resolve()
    m = Mappe(ordner)
    medien = Path(a.medien).resolve() if a.medien else ordner / "medien"
    medien.mkdir(parents=True, exist_ok=True)
    texte = [fuer_tts(s.get("sprechertext", "")) for s in m.szenen]
    teile_roh = [[fuer_tts(x) for x in s.get("sprechertext_tts", "").split(PAUSE) if x.strip()] for s in m.szenen]

    neu_alle = a.neu is not None and len(a.neu) == 0
    neu = {f"{int(x):02d}" for x in (a.neu or [])}
    aufgaben = []
    for i, t in enumerate(texte, 1):
        nn = f"{i:02d}"
        ziel = medien / f"vo-{nn}.mp3"
        if t and (not ziel.exists() or neu_alle or nn in neu):
            aufgaben.append((i, nn, t, ziel))
    if not aufgaben:
        print("Alle Szenen sind schon vertont. Mit --neu NN gezielt neu erzeugen.")
        return

    zeichen = sum(len(t) for _, _, t, _ in aufgaben)
    print(f"{len(aufgaben)} Szene(n), {zeichen} Zeichen, Modell {modell}.")
    print("Das verbraucht Zeichen-Guthaben in deinem ElevenLabs-Konto.")
    if not a.ja and input("Senden? [j/N] ").strip().lower() not in ("j", "ja", "y", "yes"):
        print("Abgebrochen, nichts gesendet.")
        return

    einstellungen = dict(cfg.get("voice_settings", {}))
    if a.tempo:
        einstellungen["speed"] = a.tempo
    if a.stabilitaet is not None:
        einstellungen["stability"] = a.stabilitaet
    for i, nn, t, ziel in aufgaben:
        vorher = texte[i - 2] if i > 1 else ""
        nachher = texte[i] if i < len(texte) else ""
        print(f"  Szene {nn} ...", end=" ", flush=True)
        teile = teile_roh[i - 1]
        if len(teile) <= 1:
            ziel.write_bytes(tts(t, schluessel, stimme, modell, vorher, nachher, einstellungen))
        else:  # [pause]: Stücke einzeln erzeugen (Kontext über previous/next_text) und mit Stille verbinden
            stuecke = []
            for k, teil in enumerate(teile):
                v = " ".join(teile[:k]) or vorher
                n = " ".join(teile[k + 1:]) or nachher
                f = medien / f"vo-{nn}-teil{k + 1}.mp3"
                f.write_bytes(tts(teil, schluessel, stimme, modell, v, n, einstellungen))
                stuecke.append(f)
            verbinde_mit_pausen(stuecke, ziel)
        print(f"{ziel.relative_to(ROOT)}")
    print(f"Fertig. Jetzt schneiden: python3 tools/schnitt.py {ordner.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
