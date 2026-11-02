#!/usr/bin/env python3
"""Přepis session Claude Code pro příkaz /konec.

Záznam session (~/.claude/projects/<slug>/<session-id>.jsonl) je většinou
technický šum: systémové připomínky, snímky souborů, výpisy nástrojů.
Skript z něj vytáhne to, co se dá vytěžit, a spočítá, co ne.

Příkazy:
    prepis.py prehled <session.jsonl>   souhrn: co se čte, co ne, seznam promptů
    prepis.py cisty   <session.jsonl>   čitelný přepis s čísly řádků zdroje

Každý řádek výstupu nese číslo řádku v .jsonl ([L123]), aby šla každá citace
ověřit příkazem `sed -n '123p' <session.jsonl>`.

Co se počítá jako prompt:
  - text, který uživatel napsal (i slash příkaz, `! příkaz` a vložený text),
  - každá odpověď v dialogu AskUserQuestion zvlášť (dvě otázky = dva prompty),
  - zpráva poslaná během odpovědi, ale jen jednou: v záznamu je jako zařazení
    do fronty a pak znovu jako doručení,
  - rozepsaná verze promptu se nepočítá, když ve stejném tahu existuje delší
    verze, která jím začíná.

Návratový kód: 0 hotovo, 2 špatné volání nebo nečitelný soubor.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Nástroje, jejichž výstup je jen obsah souborů. Ty se čtou přímo z disku.
POUZE_SOUBORY = {"Read", "Grep", "Glob", "LS", "NotebookRead"}
# Nástroje, jejichž výstup je jen potvrzení zápisu.
ZAPISY = {"Edit", "Write", "MultiEdit", "NotebookEdit", "TodoWrite"}
# Nástroj s odpověďmi uživatele na otázky.
DOTAZ = "AskUserQuestion"

MAX_VYSTUP = 3000  # znaků z výsledku nástroje v čistém přepisu

# Značky, do kterých Claude Code balí text, který napsal uživatel.
# Text začínající jinou značkou (<task-notification>, <bash-stdout>,
# <local-command-stdout>, <agent-message>…) vložil harness, ne uživatel.
UZIVATELSKE_ZNACKY = {"command-name", "command-message", "command-args",
                      "pasted_content", "bash-input"}
HLASKY_SYSTEMU = ("[Request interrupted", "[SYSTEM")

RE_PRIPOMINKA = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
RE_ZNACKA = re.compile(r"\s*<([\w-]+)")
RE_PRIKAZ = re.compile(r"<command-name>\s*(/?[^<\s]+)\s*</command-name>")
RE_ARGUMENTY = re.compile(r"<command-args>(.*?)</command-args>", re.S)
RE_SHELL = re.compile(r"<bash-input>(.*?)</bash-input>", re.S)
RE_VLOZENO = re.compile(r"</?pasted_content[^>]*>")
RE_ODLOZENO = re.compile(r"Full output saved to:\s*(\S+)")
RE_ODPOVED = re.compile(r'"(.+?)"="(.*?)"(?=, "|\. You can|\.?\s*$)', re.S)


def nacti(cesta):
    """Vrátí seznam (číslo_řádku, záznam). Poškozené řádky přeskočí."""
    zaznamy = []
    with open(cesta, encoding="utf-8", errors="replace") as f:
        for cislo, radek in enumerate(f, 1):
            radek = radek.strip()
            if not radek:
                continue
            try:
                zaznam = json.loads(radek)
            except json.JSONDecodeError:
                continue
            if isinstance(zaznam, dict):
                zaznamy.append((cislo, zaznam))
    return zaznamy


def bloky(zaznam):
    """Obsah zprávy jako seznam bloků (text převede na jeden blok)."""
    obsah = (zaznam.get("message") or {}).get("content")
    if isinstance(obsah, str):
        return [{"type": "text", "text": obsah}]
    return obsah if isinstance(obsah, list) else []


def text_vysledku(blok):
    obsah = blok.get("content")
    if isinstance(obsah, str):
        return obsah
    if isinstance(obsah, list):
        return "\n".join(c.get("text", "") for c in obsah
                         if isinstance(c, dict) and c.get("type") == "text")
    return ""


def jeden_radek(text):
    return " ".join(text.split())


def uzivatelsky_text(text):
    """Očistí text od vložek harnessu. Vrátí None, když to není prompt."""
    text = RE_PRIPOMINKA.sub("", text or "").strip()
    if not text or text.startswith(HLASKY_SYSTEMU):
        return None
    znacka = RE_ZNACKA.match(text)
    if znacka and znacka.group(1) not in UZIVATELSKE_ZNACKY:
        return None
    prikaz = RE_PRIKAZ.search(text)
    if prikaz:
        jmeno = prikaz.group(1)
        if not jmeno.startswith("/"):
            jmeno = "/" + jmeno
        argumenty = RE_ARGUMENTY.search(text)
        argumenty = argumenty.group(1).strip() if argumenty else ""
        return f"{jmeno} {argumenty}".strip()
    shell = RE_SHELL.search(text)
    if shell:
        return "! " + shell.group(1).strip()
    if RE_VLOZENO.search(text):
        return "[vloženo] " + RE_VLOZENO.sub("", text).strip()
    return text


def odpovedi_dialogu(zaznam, blok):
    """Každá odpověď z AskUserQuestion jako samostatný text."""
    vysledek = zaznam.get("toolUseResult")
    if isinstance(vysledek, dict) and isinstance(vysledek.get("answers"), dict):
        poznamky = vysledek.get("annotations") or {}
        texty = []
        for otazka, odpoved in vysledek["answers"].items():
            t = f"[dialog] {jeden_radek(otazka)} → {odpoved}"
            poznamka = (poznamky.get(otazka) or {}).get("notes") if isinstance(poznamky, dict) else None
            if poznamka:
                t += f" (poznámka: {poznamka})"
            texty.append(t)
        if texty:
            return texty
    text = text_vysledku(blok)
    pary = RE_ODPOVED.findall(text)
    if pary:
        return [f"[dialog] {jeden_radek(o)} → {a}" for o, a in pary]
    return ["[dialog] " + text.strip()] if text.strip() else []


def odlozene_vystupy(text):
    """Cesty k plným výstupům, které na disku opravdu existují."""
    nalezene = []
    for cesta in RE_ODLOZENO.findall(text):
        cesta = cesta.rstrip(".,)")
        if Path(cesta).expanduser().is_file():
            nalezene.append(cesta)
    return nalezene


def projdi(zaznamy):
    """Jeden průchod záznamem. Vrátí události, prompty a statistiku."""
    nastroje = {}  # id volání -> jméno nástroje
    udalosti = []  # (řádek, druh, text) pro čistý přepis
    prompty = []  # (řádek, text, tah) — tah None = nesmí se slučovat
    stat = Counter()
    velikost = Counter()
    odlozene = set()
    fronta = defaultdict(list)  # text -> řádky zařazení čekající na doručení
    tah = 0

    def pridej_prompt(cislo, text, tah_promptu, popisek="PROMPT"):
        prompty.append((cislo, text, tah_promptu))
        udalosti.append((cislo, popisek, text))
        velikost["čte se"] += len(text)

    for cislo, z in zaznamy:
        druh = z.get("type")
        if z.get("isSidechain"):
            stat["záznamy subagentů"] += 1
            continue

        if z.get("isCompactSummary"):
            stat["kompaktace"] += 1
            udalosti.append((cislo, "KOMPAKTACE", "— souhrn po kompaktaci —"))
            continue

        if druh == "queue-operation":
            if z.get("operation") == "enqueue":
                t = uzivatelsky_text(z.get("content") if isinstance(z.get("content"), str) else "")
                if t:
                    fronta[jeden_radek(t)].append(cislo)
                    pridej_prompt(cislo, t, None, "PROMPT (během odpovědi)")
            continue

        if druh == "attachment":
            priloha = z.get("attachment") or {}
            if priloha.get("type") == "queued_command" and isinstance(priloha.get("prompt"), str):
                t = uzivatelsky_text(priloha["prompt"])
                if t:
                    cekajici = fronta.get(jeden_radek(t))
                    if cekajici:
                        cekajici.pop(0)  # doručení už započítaného zařazení
                    else:
                        pridej_prompt(cislo, t, None, "PROMPT (během odpovědi)")
            continue

        if druh == "assistant":
            tah += 1
            for b in bloky(z):
                typ = b.get("type")
                if typ == "text" and b.get("text", "").strip():
                    udalosti.append((cislo, "CLAUDE", b["text"].strip()))
                    velikost["čte se"] += len(b["text"])
                elif typ == "thinking":
                    stat["bloky myšlení"] += 1
                    velikost["myšlení"] += len(b.get("thinking", ""))
                elif typ == "tool_use":
                    jmeno = b.get("name", "?")
                    nastroje[b.get("id")] = jmeno
                    vstup = b.get("input") or {}
                    if jmeno == "Bash":
                        popis = vstup.get("command", "")
                    elif jmeno in ZAPISY or jmeno in POUZE_SOUBORY:
                        popis = vstup.get("file_path") or vstup.get("path") or vstup.get("pattern", "")
                    elif jmeno == DOTAZ:
                        popis = " | ".join(q.get("question", "") for q in vstup.get("questions", []))
                    else:
                        popis = json.dumps(vstup, ensure_ascii=False)[:300]
                    udalosti.append((cislo, f"NÁSTROJ {jmeno}", popis))
            continue

        if druh != "user":
            continue

        meta = z.get("isMeta")
        for b in bloky(z):
            typ = b.get("type")
            if typ == "image":
                stat["obrázky"] += 1
            elif typ == "tool_result":
                jmeno = nastroje.get(b.get("tool_use_id"), "?")
                text = text_vysledku(b)
                odlozene.update(odlozene_vystupy(text))
                if jmeno == DOTAZ:
                    for t in odpovedi_dialogu(z, b):
                        pridej_prompt(cislo, t, None)
                elif jmeno in POUZE_SOUBORY:
                    stat["výstupy čtení souborů"] += 1
                    velikost["výstupy čtení souborů"] += len(text)
                elif jmeno in ZAPISY:
                    pass
                else:
                    kratsi = text if len(text) <= MAX_VYSTUP else text[:MAX_VYSTUP] + f"\n… [zkráceno, celé na řádku L{cislo}]"
                    udalosti.append((cislo, f"VÝSLEDEK {jmeno}", kratsi.strip()))
                    velikost["čte se"] += len(kratsi)
                    velikost["zkrácené výstupy nástrojů"] += max(0, len(text) - MAX_VYSTUP)
            elif typ == "text" and not meta:
                t = uzivatelsky_text(b.get("text", ""))
                if t:
                    cekajici = fronta.get(jeden_radek(t))
                    if cekajici and cekajici[0] < cislo:
                        cekajici.pop(0)  # doručení zprávy z fronty jako běžný prompt
                    else:
                        pridej_prompt(cislo, t, tah)

    prompty, rozepsane = bez_rozepsanych(prompty)
    stat["rozepsané verze promptů (vynechány)"] = rozepsane
    udalosti.sort(key=lambda u: u[0])
    return udalosti, prompty, stat, velikost, sorted(odlozene)


def bez_rozepsanych(prompty):
    """Vynechá prompt, který je jen začátkem delšího promptu ze stejného tahu."""
    vysledek, vynechano = [], 0
    for cislo, text, tah in prompty:
        kratky = jeden_radek(text)
        if tah is not None and any(
            jiny_tah == tah and jeden_radek(jiny) != kratky and jeden_radek(jiny).startswith(kratky)
            for _, jiny, jiny_tah in prompty
        ):
            vynechano += 1
            continue
        vysledek.append((cislo, text))
    return sorted(vysledek), vynechano


def kb(znaky):
    return f"{znaky / 1024:.1f} kB"


def prehled(zaznamy, cesta):
    _, prompty, stat, velikost, odlozene = projdi(zaznamy)
    celkem = Path(cesta).stat().st_size
    kompaktace = stat["kompaktace"]

    print(f"Soubor: {cesta}")
    print(f"Velikost záznamu: {kb(celkem)} · vytěžitelný text: {kb(velikost['čte se'])}")
    print(f"Kompaktace: {kompaktace}"
          + ("  → část konverzace už v kontextu není, přečti přepis celý" if kompaktace
             else "  → celá konverzace je v kontextu, přepis použij jen k dohledání"))
    print(f"Prompty uživatele: {len(prompty)}")
    if stat["rozepsané verze promptů (vynechány)"]:
        print(f"  (vynecháno rozepsaných verzí: {stat['rozepsané verze promptů (vynechány)']})")
    print()
    print("NEČTE SE (patří do mezí běhu):")
    print(f"  bloky myšlení: {stat['bloky myšlení']} ({kb(velikost['myšlení'])} textu)")
    print(f"  výstupy čtení souborů: {stat['výstupy čtení souborů']} ({kb(velikost['výstupy čtení souborů'])}) – obsah je v souborech")
    print(f"  obrázky: {stat['obrázky']}")
    print(f"  zkrácené výstupy nástrojů: {kb(velikost['zkrácené výstupy nástrojů'])} – celé v .jsonl")
    if stat["záznamy subagentů"]:
        print(f"  záznamy subagentů: {stat['záznamy subagentů']}")
    print(f"  odložené výstupy (existující soubory): {len(odlozene)}")
    for o in odlozene:
        print(f"    {o}")
    print()
    print("PROMPTY (pro evidenci):")
    for i, (cislo, text) in enumerate(prompty, 1):
        print(f"  {i:3}. [L{cislo}] {jeden_radek(text)[:110]}")
    return 0


def cisty(zaznamy):
    udalosti, *_ = projdi(zaznamy)
    for cislo, druh, text in udalosti:
        print(f"[L{cislo}] {druh}: {text}")
        print()
    return 0


def main(argumenty):
    if len(argumenty) != 2 or argumenty[0] not in ("prehled", "cisty"):
        print("Použití: prepis.py prehled|cisty <session.jsonl>", file=sys.stderr)
        return 2
    prikaz, cesta = argumenty
    try:
        zaznamy = nacti(cesta)
    except OSError as chyba:
        print(f"Nelze přečíst {cesta}: {chyba}", file=sys.stderr)
        return 2
    if not zaznamy:
        print(f"{cesta}: žádné čitelné záznamy", file=sys.stderr)
        return 2
    return prehled(zaznamy, cesta) if prikaz == "prehled" else cisty(zaznamy)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
