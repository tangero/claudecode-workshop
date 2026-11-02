#!/usr/bin/env python3
"""Uvítání a údržba – SessionStart hook pluginu workshop.

Při každém skutečném startu session (ne po /clear, kompaktaci nebo obnovení):

1. Zkopíruje statusline.py z pluginu do ~/.claude/workshop-balik/, když se
   liší. Plugin nemůže sám nastavit statusLine, ale tahle kopie se díky
   tomu aktualizuje spolu s ním.
2. V první session po instalaci řekne Claudovi, ať uživatele uvítá a
   nabídne /pruvodce.
3. Po aktualizaci pluginu řekne Claudovi, ať jednou shrne novinky
   z CHANGELOG.md.

Stav si drží v ~/.claude/workshop-balik/ (uvitano, verze).
"""

import json
import shutil
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
BALIK = Path.home() / ".claude" / "workshop-balik"
ZNACKA = BALIK / "uvitano"
VERZE = BALIK / "verze"

UVITANI = (
    "Uživatel právě nainstaloval workshopový balík Claude Code. Na úplném začátku své první "
    "odpovědi ho česky a nejvýš na šesti řádcích uvítej: řekni, že má nové příkazy /oponentura "
    "(prověřit nápad nebo PRD před stavbou), /codex-review (review před merge), /konec (uložit "
    "práci na konci session) a /pokracuj (navázat v další session), že hlídač kontextu sám "
    "navrhne /konec a že se balík sám aktualizuje. Nabídni /pruvodce, který vše vysvětlí, "
    "nastaví statusline a připraví strukturu projektu. Pak normálně odpověz na to, co uživatel napsal."
)


def novinky():
    """Vrátí (verze, text) první sekce CHANGELOG.md, nebo (None, "")."""
    try:
        radky = (PLUGIN / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    except OSError:
        return None, ""
    verze, text = None, []
    for r in radky:
        if r.startswith("## "):
            if verze:
                break
            verze = r[3:].strip()
        elif verze:
            text.append(r)
    return verze, "\n".join(text).strip()


def srovnej_statusline():
    zdroj, cil = PLUGIN / "statusline" / "statusline.py", BALIK / "statusline.py"
    try:
        if not cil.exists() or cil.read_bytes() != zdroj.read_bytes():
            shutil.copyfile(zdroj, cil)
    except OSError:
        pass


def main():
    try:
        vstup = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        vstup = {}
    if vstup.get("source", "startup") != "startup":
        return 0
    try:
        BALIK.mkdir(parents=True, exist_ok=True)
    except OSError:
        return 0
    srovnej_statusline()

    verze, text = novinky()
    try:
        videna = VERZE.read_text(encoding="utf-8").strip()
    except OSError:
        videna = None

    zprava = None
    if not ZNACKA.exists():
        zprava = UVITANI
    elif verze and videna and verze != videna and text:
        zprava = (
            f"Workshopový balík se aktualizoval na verzi {verze}. Na úplném začátku své první "
            "odpovědi to uživateli česky oznam a novinky shrň nejvýš na čtyřech řádcích:\n" + text
            + "\nPak normálně odpověz na to, co uživatel napsal."
        )

    # Značky zapisuj před výstupem: bez nich by se zpráva opakovala pořád.
    try:
        ZNACKA.write_text("1", encoding="utf-8")
        if verze:
            VERZE.write_text(verze, encoding="utf-8")
    except OSError:
        return 0
    if zprava:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": zprava,
        }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
