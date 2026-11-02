#!/usr/bin/env python3
"""Hlídač kontextu – UserPromptSubmit hook pro Claude Code.

Model sám nevidí, jak plný má kontext. Tenhle hook to při každé zprávě
změří a po překročení prahu modelu řekne, ať navrhne /konec a novou
session (/pokracuj). Na každém prahu se ozve jednou. Po kompaktaci, kdy
zaplnění klesne, se prahy znovu odjistí.

Zaplnění bere ze stavu, který zapisuje statusline.py
(~/.claude/stav-kontextu/<session>.json). Bez něj ho spočítá z poslední
odpovědi v záznamu session a okno odhadne na 200 000 tokenů.

Nastavení (proměnné prostředí, nepovinné):
  KONEC_PRAHY  prahy v procentech, výchozí "60,80"
  KONEC_OKNO   velikost okna, když chybí stav ze statusline, výchozí 200000

Registruje ho plugin workshop v hooks/hooks.json.
"""

import json
import os
import sys
from pathlib import Path

STAV = Path.home() / ".claude" / "stav-kontextu"


def prahy():
    try:
        return sorted(int(p) for p in os.environ.get("KONEC_PRAHY", "60,80").split(",") if p.strip())
    except ValueError:
        return [60, 80]


def ze_statusline(session):
    try:
        stav = json.loads((STAV / f"{session}.json").read_text(encoding="utf-8"))
        return float(stav["procenta"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def ze_zaznamu(cesta):
    """Zaplnění z usage poslední odpovědi hlavní konverzace (bez subagentů)."""
    try:
        okno = int(os.environ.get("KONEC_OKNO", "200000"))
        with open(cesta, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 2_000_000))  # stačí konec souboru
            radky = f.read().decode("utf-8", "replace").splitlines()
    except (OSError, ValueError):
        return None
    for radek in reversed(radky):
        try:
            z = json.loads(radek)
        except json.JSONDecodeError:
            continue
        if z.get("type") != "assistant" or z.get("isSidechain"):
            continue
        u = (z.get("message") or {}).get("usage") or {}
        tokeny = sum(u.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens",
                                             "cache_creation_input_tokens", "output_tokens"))
        if tokeny:
            return 100 * tokeny / okno
    return None


def main():
    try:
        vstup = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    session = vstup.get("session_id")
    if not session:
        return 0

    procenta = ze_statusline(session)
    if procenta is None and vstup.get("transcript_path"):
        procenta = ze_zaznamu(vstup["transcript_path"])
    if procenta is None:
        return 0

    seznam = prahy()
    soubor = STAV / f"{session}.ohlaseno.json"
    try:
        ohlaseno = set(json.loads(soubor.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        ohlaseno = set()

    # Po kompaktaci kontext klesne – prahy, pod které se vrátil, znovu odjisti.
    ohlaseno = {p for p in ohlaseno if procenta >= p - 10}
    prekroceno = [p for p in seznam if procenta >= p and p not in ohlaseno]

    zprava = None
    if prekroceno:
        prah = max(prekroceno)
        ohlaseno.update(prekroceno)
        if prah == seznam[-1]:
            zprava = (
                f"Kontext je zaplněný na {procenta:.0f} %. Nezačínej nové větší téma. "
                "Dokonči rozdělaný krok a na konci odpovědi uživateli navrhni postup /konec → /clear → /pokracuj "
                "(zapsat práci, vyprázdnit kontext, navázat). Řekni to jednou větou."
            )
        else:
            zprava = (
                f"Kontext je zaplněný na {procenta:.0f} %. Až dokončíš aktuální krok, "
                "jednou větou uživateli navrhni postup /konec → /clear → /pokracuj, "
                "pokud další práce není jen drobnost."
            )

    try:
        STAV.mkdir(parents=True, exist_ok=True)
        soubor.write_text(json.dumps(sorted(ohlaseno)), encoding="utf-8")
    except OSError:
        pass

    if zprava:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": zprava,
        }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
