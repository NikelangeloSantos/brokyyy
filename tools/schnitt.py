#!/usr/bin/env python3
"""Schnitt: Bilder/Clips + Voiceover + Untertitel + Einblendtexte -> fertiges 9:16-Video (ffmpeg).

Benutzung (aus dem Repo-Hauptordner):
    python3 tools/schnitt.py videos/01-abo-chaos

Erwartete Dateien im Video-Ordner unter medien/ (NN = Szenennummer 01, 02, ...):
    szene-NN.mp4 / .mov / .webm   Clip aus Flow (bevorzugt)
    szene-NN.png / .jpg / .jpeg   oder Standbild (bekommt leichtes Stop-Motion-Wackeln)
    vo-NN.mp3 / .wav              Voiceover pro Szene (z. B. aus tools/vertonung.py)
    voiceover.mp3 / .wav          alternativ: ein Voiceover für alles
Mehrere Medien pro Szene: szene-NN-a.mp4, szene-NN-b.mp4 ... oder in thema.toml
`medien = ["clips/x.mp4", "bilder/y.jpg"]` – dann wird im Schnitt-Tempo hart zwischen ihnen geschnitten.
Clips wackeln nicht; Standbilder bekommen leichtes Stop-Motion-Wackeln.
Fehlt etwas, kommt ein Platzhalter-Bild bzw. Stille, damit du trotzdem schon den Ablauf siehst.

Ausgabe: videos/<ordner>/export/<ordner>.mp4 und untertitel-final.srt (echte Zeiten).
Braucht ffmpeg (mit libass) im PATH.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brokey import ROOT, Mappe, zeit_srt  # noqa: E402

B, H = 1080, 1920
FPS = 30
STOPMOTION_FPS = 10
PAUSE_NACH_SZENE = 0.15  # Sekunden Luft nach dem Sprechertext (kurz = schnelleres Tempo)
WOERTER_PRO_UNTERTITEL = 5
CLIP_SFX_LAUTSTAERKE = 0.35  # Soundeffekte aus Flow-Clips leise unter die Stimme
# Schnelle Schnitte: jede Szene wird in kurze Einstellungen mit wechselndem Ausschnitt zerlegt
# (Totale -> Gesicht nah -> halbnah -> sehr nah). Pro Szene in thema.toml ueberschreibbar: schnitt_tempo = 1.2
SCHNITT_TEMPO_HOOK = 0.6     # Sekunden pro Einstellung im Hook
SCHNITT_TEMPO = 1.8          # Sekunden pro Einstellung sonst
# Zoomstufen der Einstellungen und wie weit oben (0 = Bildoberkante, 0.5 = Mitte) der Ausschnitt sitzt
EINSTELLUNGEN = [(1.0, 0.5), (1.3, 0.33), (1.12, 0.45), (1.45, 0.3)]
WACKELN = 3                  # Pixel Stop-Motion-Wackeln bei Standbildern
WACKELN_HOOK = 6
BILD_ENDUNGEN = (".png", ".jpg", ".jpeg", ".webp")
CLIP_ENDUNGEN = (".mp4", ".mov", ".webm", ".mkv")
AUDIO_ENDUNGEN = (".mp3", ".wav", ".m4a")


def ffmpeg(*args: str):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg-Fehler:\n{r.stderr}")


def probe(datei: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                        "-of", "json", str(datei)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def dauer(datei: Path) -> float:
    return float(probe(datei)["format"]["duration"])


def hat_audio(datei: Path) -> bool:
    return any(s.get("codec_type") == "audio" for s in probe(datei).get("streams", []))


def finde(ordner: Path, stamm: str, endungen) -> Path | None:
    for e in endungen:
        p = ordner / f"{stamm}{e}"
        if p.exists():
            return p
    return None


# ---------------------------------------------------------------- ASS-Untertitel

def ass_text(t: str) -> str:
    t = t.replace("\\", "").replace("{", "(").replace("}", ")")
    return t.replace(" · ", "\\N").replace("\n", "\\N")


def ass_zeit(sek: float) -> str:
    cs = int(round(sek * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"


ASS_KOPF = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {B}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Untertitel,DejaVu Sans,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6,0,2,90,90,560,1
Style: Einblendung,DejaVu Sans,74,&H00FFFFFF,&H00FFFFFF,&H002F2FD3,&H00000000,1,0,0,0,100,100,0,0,3,18,0,8,80,80,230,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def untertitel_stuecke(text: str, start: float, ende: float):
    """Sprechertext in kurze Stücke teilen, Zeit nach Zeichenanzahl verteilen."""
    w = text.split()
    stuecke = [" ".join(w[i:i + WOERTER_PRO_UNTERTITEL]) for i in range(0, len(w), WOERTER_PRO_UNTERTITEL)]
    gesamt = sum(len(s) for s in stuecke) or 1
    t = start
    for s in stuecke:
        d = (ende - start) * len(s) / gesamt
        yield t, t + d, s
        t += d


# ---------------------------------------------------------------- Segmente

def platzhalter(ziel: Path, text: str):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (B, H), (246, 244, 238))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 54)
    except OSError:
        f = ImageFont.load_default()
    d.multiline_text((B // 2, H // 2), text, fill=(120, 120, 120), font=f, anchor="mm", align="center", spacing=20)
    img.save(ziel)


def zoom_ausdruck(tempo: float, fps: int) -> tuple[str, str, str]:
    """zoompan-Ausdrücke: alle `tempo` Sekunden harter Schnitt auf die nächste Einstellung."""
    k = max(1, round(tempo * fps))
    idx = f"mod(floor(in/{k}),{len(EINSTELLUNGEN)})"
    z, y = "1", "0.5"
    for i in reversed(range(len(EINSTELLUNGEN))):
        zi, yi = EINSTELLUNGEN[i]
        z = f"if(eq({idx},{i}),{zi},{z})"
        y = f"if(eq({idx},{i}),{yi},{y})"
    x_expr = "iw/2-iw/zoom/2"
    y_expr = f"max(0,min(ih-ih/zoom,ih*({y})-ih/zoom/2))"
    return z, x_expr, y_expr


def ist_clip(p: Path) -> bool:
    return p.suffix.lower() in CLIP_ENDUNGEN


def ausschnitt(zoom: float, y_anteil: float) -> str:
    """Fester Bildausschnitt (für wechselnde Einstellungen ohne Kamerafahrt)."""
    if zoom == 1.0:
        return f"scale={B}:{H}"
    return (f"crop=w=iw/{zoom}:h=ih/{zoom}:x=(iw-iw/{zoom})/2:"
            f"y='max(0,min(ih-ih/{zoom},ih*{y_anteil}-ih/{zoom}/2))',scale={B}:{H}")


def baue_einstellung(medium: Path, d: float, ziel: Path, *, start: float = 0.0, zoom_tempo: float | None = None,
                     einstellung=(1.0, 0.5), wackeln: int = 0):
    """Eine Einstellung (ein Bild oder Clip-Stück) als MP4 mit Ton (Clip-Geräusche oder Stille)."""
    gross_b, gross_h = int(B * 1.5), int(H * 1.5)  # Reserve, damit Ausschnitte scharf bleiben
    if ist_clip(medium):
        eingabe = ["-ss", f"{start:.3f}", "-i", str(medium)]
        # kleine Clips (z. B. 360x640) mit Lanczos hochskalieren und leicht nachschärfen
        v = (f"[0:v]fps={FPS},scale={gross_b}:{gross_h}:force_original_aspect_ratio=increase:flags=lanczos,"
             f"crop={gross_b}:{gross_h},unsharp=5:5:0.6,"
             f"tpad=stop_mode=clone:stop_duration={d + 1:.2f},trim=duration={d:.3f},setpts=PTS-STARTPTS,")
        if zoom_tempo:
            z, x, y = zoom_ausdruck(zoom_tempo, FPS)
            v += f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={B}x{H}:fps={FPS},"
        else:
            v += ausschnitt(*einstellung) + ","
        v += "setsar=1,format=yuv420p[v]"
    else:
        eingabe = ["-loop", "1", "-t", f"{d:.3f}", "-i", str(medium)]
        # Standbild: 10 fps + leichtes Wackeln = Stop-Motion-/Line-Boil-Gefühl
        v = (f"[0:v]fps={STOPMOTION_FPS},scale={gross_b + 4 * wackeln}:{gross_h + 4 * wackeln}:force_original_aspect_ratio=increase,"
             f"crop={gross_b}:{gross_h}:x='(iw-{gross_b})/2+{wackeln}*sin(n*2.3)':y='(ih-{gross_h})/2+{wackeln}*cos(n*1.7)',")
        if zoom_tempo:
            z, x, y = zoom_ausdruck(zoom_tempo, STOPMOTION_FPS)
            v += f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={B}x{H}:fps={STOPMOTION_FPS},"
        else:
            v += ausschnitt(*einstellung) + ","
        v += f"fps={FPS},setsar=1,format=yuv420p[v]"
    if ist_clip(medium) and hat_audio(medium):
        a = (f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={CLIP_SFX_LAUTSTAERKE},"
             f"apad,atrim=duration={d:.3f}[a]")
    else:
        eingabe += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        a = f"[1:a]atrim=duration={d:.3f}[a]"
    ffmpeg(*eingabe, "-filter_complex", f"{v};{a}", "-map", "[v]", "-map", "[a]", "-t", f"{d:.3f}",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(ziel))


def einstellungen_planen(medien: list[Path], d: float, tempo: float, hook: bool):
    """Liste von (medium, dauer, start, zoom_tempo, einstellung).

    - 1 Standbild: wechselnde Ausschnitte im Tempo (sonst wirkt es tot)
    - 1 Clip: läuft durch, ohne Zoom; nur im Hook schnelle Ausschnittwechsel
    - mehrere Medien im Hook: harte Schnitte zwischen ihnen im Tempo, Clips laufen weiter statt neu zu starten
    - mehrere Medien sonst: nacheinander, jedes bekommt seinen Anteil der Szene
    """
    if len(medien) == 1:
        m = medien[0]
        if ist_clip(m) and not hook:
            return [(m, d, 0.0, None, (1.0, 0.5))]
        return [(m, d, 0.0, tempo, (1.0, 0.5))]
    if not hook:  # ausserhalb des Hooks: Medien nacheinander, damit die Mini-Geschichte lesbar bleibt
        anteil = d / len(medien)
        return [(m, anteil, 0.0, None if ist_clip(m) else tempo, (1.0, 0.5)) for m in medien]
    n = max(len(medien), round(d / tempo))
    laenge = d / n
    clip_pos = {m: 0.0 for m in medien}
    clip_dauer = {m: dauer(m) for m in medien if ist_clip(m)}
    plan = []
    for k in range(n):
        m = medien[k % len(medien)]
        runde = k // len(medien)
        start = 0.0
        if m in clip_dauer:
            start = clip_pos[m] if clip_pos[m] + laenge <= clip_dauer[m] else 0.0
            clip_pos[m] = start + laenge
            einst = (1.0, 0.5)
        else:  # Standbild wiederholt sich -> anderer Ausschnitt
            einst = EINSTELLUNGEN[runde % len(EINSTELLUNGEN)]
        plan.append((m, laenge, start, None, einst))
    return plan


def baue_segment(medien: list[Path], stimme: Path | None, d: float, ziel: Path, tempo: float, wackeln: int,
                 hook: bool, tmp: Path):
    teile = []
    for k, (m, dk, start, zt, einst) in enumerate(einstellungen_planen(medien, d, tempo, hook)):
        t = tmp / f"{ziel.stem}-e{k:02d}.mp4"
        baue_einstellung(m, dk, t, start=start, zoom_tempo=zt, einstellung=einst,
                         wackeln=0 if ist_clip(m) else wackeln)
        teile.append(t)
    eingabe = [x for t in teile for x in ("-i", str(t))]
    n = len(teile)
    eingabe += ["-i", str(stimme)] if stimme else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    f = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][sfx];"
    f += (f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration={d:.3f}[stimme];"
          f"[stimme][sfx]amix=inputs=2:normalize=0,atrim=duration={d:.3f}[a]")
    ffmpeg(*eingabe, "-filter_complex", f, "-map", "[v]", "-map", "[a]", "-t", f"{d:.3f}",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(ziel))
    return n


# ---------------------------------------------------------------- Hauptablauf

def schneide(ordner: Path, nur_pruefen: bool = False) -> Path | None:
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg nicht gefunden. Bitte installieren (siehe README).")
    m = Mappe(ordner)
    m.pruefe()
    medien = ordner / "medien"
    gesamt_vo = finde(medien, "voiceover", AUDIO_ENDUNGEN)
    gesamt_vo_dauer = dauer(gesamt_vo) if gesamt_vo else None
    gesamt_woerter = sum(len(s.get("sprechertext", "").split()) for s in m.szenen) or 1

    plan = []
    for i, s in enumerate(m.szenen, 1):
        nn = f"{i:02d}"
        if s.get("medien"):
            eintraege = s["medien"] if isinstance(s["medien"], list) else [s["medien"]]
            liste = [ROOT / e for e in eintraege]
        else:  # medien/szene-NN.mp4, szene-NN-a.mp4, szene-NN-b.png ...
            liste = sorted(x for x in medien.glob(f"szene-{nn}*")
                           if x.suffix.lower() in CLIP_ENDUNGEN + BILD_ENDUNGEN) if medien.exists() else []
        for x in [x for x in liste if not x.exists()]:
            print(f"  WARNUNG: Szene {nn}: {x.relative_to(ROOT)} gibt es nicht.")
        medium = [x for x in liste if x.exists()]
        stimme = finde(medien, f"vo-{nn}", AUDIO_ENDUNGEN)
        if stimme:
            d = dauer(stimme) + PAUSE_NACH_SZENE
            quelle = "Stimme"
        elif gesamt_vo_dauer:
            d = gesamt_vo_dauer * len(s.get("sprechertext", "").split()) / gesamt_woerter
            quelle = "Anteil voiceover"
        else:
            d = s["_ende"] - s["_start"] + PAUSE_NACH_SZENE
            quelle = "geschätzt"
        plan.append(dict(nn=nn, szene=s, medium=medium, stimme=stimme, d=d, quelle=quelle))

    print(f"Schnittplan {ordner.name}:")
    t = 0.0
    for p in plan:
        namen = ", ".join(x.name for x in p["medium"]) if p["medium"] else "FEHLT -> Platzhalter"
        print(f"  {p['nn']} {t:5.1f}-{t + p['d']:5.1f}s ({p['quelle']:>16})  Medien: {namen}"
              f"  Stimme: {p['stimme'].name if p['stimme'] else ('voiceover' if gesamt_vo else 'FEHLT -> Stille')}")
        t += p["d"]
    print(f"  Gesamt: {t:.1f} s")
    for f in m.fehler:
        print(f"  FEHLER:  {f}")
    if nur_pruefen:
        return None
    if m.fehler:
        sys.exit("Erst die Fehler in thema.toml beheben (python3 tools/brokey.py baue ...).")

    export = ordner / "export"
    export.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        liste, ass, srt, t = [], [ASS_KOPF], [], 0.0
        for p in plan:
            medium = p["medium"]
            if not medium:
                ph = tmp / f"platzhalter-{p['nn']}.png"
                platzhalter(ph, f"Szene {p['nn']}\n{p['szene'].get('name', '')}\n\nmedien/szene-{p['nn']}.mp4\nfehlt noch")
                medium = [ph]
            seg = tmp / f"seg-{p['nn']}.mp4"
            hook = p["szene"].get("teil") == "hook"
            tempo = p["szene"].get("schnitt_tempo") or (SCHNITT_TEMPO_HOOK if hook else SCHNITT_TEMPO)
            n = baue_segment(medium, p["stimme"], p["d"], seg, tempo, WACKELN_HOOK if hook else WACKELN, hook, tmp)
            print(f"  Szene {p['nn']}: {n} Einstellung(en)")
            liste.append(f"file '{seg}'")

            s, ende = p["szene"], t + p["d"]
            sprech_ende = ende - (PAUSE_NACH_SZENE if p["quelle"] != "Anteil voiceover" else 0)
            if s.get("einblendtext"):
                ass.append(f"Dialogue: 1,{ass_zeit(t)},{ass_zeit(ende)},Einblendung,,0,0,0,,{ass_text(s['einblendtext'])}\n")
            for a, e, txt in untertitel_stuecke(s.get("sprechertext", ""), t, sprech_ende):
                ass.append(f"Dialogue: 0,{ass_zeit(a)},{ass_zeit(e)},Untertitel,,0,0,0,,{ass_text(txt)}\n")
                srt.append(f"{len(srt) + 1}\n{zeit_srt(a)} --> {zeit_srt(e)}\n{txt}\n")
            t = ende

        (tmp / "liste.txt").write_text("\n".join(liste))
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(tmp / "liste.txt"), "-c", "copy", str(tmp / "roh.mp4"))
        (tmp / "text.ass").write_text("".join(ass), encoding="utf-8")
        ziel = export / f"{ordner.name}.mp4"
        print("  brenne Untertitel und Einblendungen ein ...")
        ffmpeg("-i", str(tmp / "roh.mp4"), "-vf", f"ass={tmp / 'text.ass'}",
               "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
               "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-movflags", "+faststart", str(ziel))
        (export / "untertitel-final.srt").write_text("\n".join(srt), encoding="utf-8")
    print(f"Fertig: {ziel.relative_to(ROOT) if ziel.is_relative_to(ROOT) else ziel} ({dauer(ziel):.1f} s)")
    if not all(p["stimme"] for p in plan) and not gesamt_vo:
        print("  Hinweis: ohne Voiceover geschnitten (stumm, Zeiten geschätzt).")
    print("  Vor dem Upload: checkliste.md abhaken (inkl. KI-Kennzeichnung).")
    return ziel


def main():
    p = argparse.ArgumentParser(description="Brokey-Video schneiden")
    p.add_argument("ordner")
    p.add_argument("--plan", action="store_true", help="nur Schnittplan anzeigen, nichts rendern")
    a = p.parse_args()
    schneide(Path(a.ordner).resolve(), nur_pruefen=a.plan)


if __name__ == "__main__":
    main()
