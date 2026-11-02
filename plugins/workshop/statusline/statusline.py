#!/usr/bin/env python3
"""Status line pro Claude Code – dva řádky, jen standardní knihovna Pythonu.

  Opus 5.5 · high │ claudecode-workshop │ ⎇ main ●3 ↑1 │ PR #12 ✓
  ▓▓▓▓▓░░░░░ 48 % kontextu (96k/200k) │ ≈ $1.84 API · 37 min │ 5h 31 % · týden 12 % │ +120 −15

Claude Code pošle na stdin JSON se stavem session, skript vypíše řádky.
Navíc uloží zaplnění kontextu do ~/.claude/stav-kontextu/<session>.json,
odkud ho čte hook hlidac-kontextu.py (sám velikost okna nezná).

Nastavení v ~/.claude/settings.json (udělá ho instaluj.sh nebo /pruvodce):
  "statusLine": {"type": "command", "command": "python3 ~/.claude/workshop-balik/statusline.py"}
Kopii v ~/.claude/workshop-balik/ udržuje aktuální hook uvitani.py z pluginu.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"
ZELENA = "\033[32m"
ZLUTA = "\033[33m"
CERVENA = "\033[31m"
AZUROVA = "\033[36m"
FIALOVA = "\033[35m"

ODDELOVAC = f" {DIM}│{RESET} "
STAV = Path.home() / ".claude" / "stav-kontextu"


def hodnota(data, *klice, vychozi=None):
    """Bezpečně vytáhne vnořenou hodnotu: hodnota(d, "cost", "total_cost_usd")."""
    for klic in klice:
        if not isinstance(data, dict) or klic not in data:
            return vychozi
        data = data[klic]
    return data if data is not None else vychozi


def git(adresar, *argumenty):
    try:
        vysledek = subprocess.run(
            ["git", "--no-optional-locks", "-C", adresar, *argumenty],
            capture_output=True, text=True, timeout=1,
        )
        return vysledek.stdout.strip() if vysledek.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def barva_podle(procenta):
    if procenta >= 80:
        return CERVENA
    if procenta >= 60:
        return ZLUTA
    return ZELENA


def tisice(n):
    return f"{n / 1000:.0f}k" if n >= 1000 else str(n)


def segment_model(d):
    model = hodnota(d, "model", "display_name", vychozi="?")
    text = f"{BOLD}{model}{RESET}"
    uroven = hodnota(d, "effort", "level")
    if uroven:
        text += f" {DIM}· {uroven}{RESET}"
    if hodnota(d, "fast_mode"):
        text += f" {ZLUTA}⚡{RESET}"
    return text


def segment_adresar(d):
    aktualni = hodnota(d, "workspace", "current_dir") or hodnota(d, "cwd") or os.getcwd()
    projekt = hodnota(d, "workspace", "project_dir") or aktualni
    jmeno = Path(aktualni).name
    if aktualni != projekt and aktualni.startswith(projekt.rstrip("/") + "/"):
        jmeno = f"{Path(projekt).name}/{os.path.relpath(aktualni, projekt)}"
    return f"{AZUROVA}{jmeno}{RESET}", aktualni


def segment_git(adresar, d):
    vetev = git(adresar, "branch", "--show-current")
    if vetev is None:
        return None  # není git repozitář
    vetev = vetev or f"({git(adresar, 'rev-parse', '--short', 'HEAD') or '?'})"
    text = f"{FIALOVA}⎇ {vetev}{RESET}"
    zmeny = git(adresar, "status", "--porcelain")
    if zmeny:
        text += f" {ZLUTA}●{len(zmeny.splitlines())}{RESET}"
    rozdil = git(adresar, "rev-list", "--left-right", "--count", "@{upstream}...HEAD")
    if rozdil:
        pozadu, napred = (int(x) for x in rozdil.split())
        if napred:
            text += f" {DIM}↑{napred}{RESET}"
        if pozadu:
            text += f" {DIM}↓{pozadu}{RESET}"
    cislo = hodnota(d, "pr", "number")
    if cislo:
        znacka = {"approved": "✓", "changes_requested": "✗", "pending": "…", "draft": "✎"}.get(
            hodnota(d, "pr", "review_state"), "")
        text += f"{ODDELOVAC}PR #{cislo}{(' ' + znacka) if znacka else ''}"
    return text


def segment_kontext(d):
    procenta = hodnota(d, "context_window", "used_percentage")
    velikost = hodnota(d, "context_window", "context_window_size", vychozi=200000)
    tokeny = hodnota(d, "context_window", "total_input_tokens", vychozi=0)
    if procenta is None:
        return f"{DIM}kontext –{RESET}", None
    procenta = float(procenta)
    barva = barva_podle(procenta)
    plne = min(10, round(procenta / 10))
    pruh = f"{barva}{'▓' * plne}{DIM}{'░' * (10 - plne)}{RESET}"
    text = f"{pruh} {barva}{procenta:.0f} %{RESET} {DIM}kontextu ({tisice(tokeny)}/{tisice(velikost)}){RESET}"
    if procenta >= 70:
        text += f" {CERVENA}→ /konec{RESET}"
    return text, {"procenta": procenta, "velikost": velikost, "tokeny": tokeny}


def segment_cena(d):
    cena = hodnota(d, "cost", "total_cost_usd")
    minuty = hodnota(d, "cost", "total_duration_ms", vychozi=0) / 60000
    casti = []
    if cena is not None:
        casti.append(f"≈ ${cena:.2f} API")
    if minuty >= 1:
        casti.append(f"{minuty:.0f} min" if minuty < 60 else f"{minuty / 60:.1f} h")
    return " · ".join(casti) if casti else None


def segment_limity(d):
    casti = []
    for klic, popis in (("five_hour", "5h"), ("seven_day", "týden")):
        procenta = hodnota(d, "rate_limits", klic, "used_percentage")
        if procenta is not None:
            casti.append(f"{barva_podle(procenta)}{popis} {procenta:.0f} %{RESET}")
    return " · ".join(casti) if casti else None


def segment_radky(d):
    plus = hodnota(d, "cost", "total_lines_added", vychozi=0)
    minus = hodnota(d, "cost", "total_lines_removed", vychozi=0)
    if not plus and not minus:
        return None
    return f"{ZELENA}+{plus}{RESET} {CERVENA}−{minus}{RESET}"


def uloz_stav(d, kontext):
    """Zapíše zaplnění kontextu pro hook hlidac-kontextu.py."""
    session = hodnota(d, "session_id")
    if not session or not kontext:
        return
    try:
        STAV.mkdir(parents=True, exist_ok=True)
        (STAV / f"{session}.json").write_text(json.dumps(kontext), encoding="utf-8")
    except OSError:
        pass


def main():
    try:
        d = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("statusline: neplatný vstup")
        return
    adresar_text, adresar = segment_adresar(d)
    kontext_text, kontext = segment_kontext(d)
    uloz_stav(d, kontext)

    prvni = [segment_model(d), adresar_text, segment_git(adresar, d)]
    druhy = [kontext_text, segment_cena(d), segment_limity(d), segment_radky(d)]
    print(ODDELOVAC.join(s for s in prvni if s))
    print(ODDELOVAC.join(s for s in druhy if s))


if __name__ == "__main__":
    main()
