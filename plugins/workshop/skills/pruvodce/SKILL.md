---
name: pruvodce
description: Použij, když uživatel napíše "/pruvodce", ptá se, jak používat workshopový balík (/oponentura, /codex-review, /konec, /pokracuj, statusline, hlídač kontextu, bez-diffu), nebo ho právě nainstaloval. Vysvětlí pracovní postup, zkontroluje instalaci a připraví strukturu aktuálního projektu.
allowed-tools: [Read, Write, Glob, Grep, Bash, AskUserQuestion]
---

# /pruvodce – jak s balíkem pracovat

Uživatel je možná začátečník. Mluv jednoduše, bez žargonu, a vysvětluj na tom, co má právě otevřené. Celé to má zabrat pár minut, ne přednášku.

## 1. Kontrola instalace

Pusť jeden příkaz. Nic neopravuj, jen zjisti stav:

```bash
claude plugin list 2>/dev/null | grep -q "workshop@claudecode-workshop" && echo "plugin workshop: ok" || echo "plugin workshop: CHYBÍ"
claude plugin list 2>/dev/null | grep -q "bez-diffu@claudecode-workshop" && echo "bez-diffu: ok" || echo "bez-diffu: není nainstalovaný"
python3 -I -c 'import json,os;d=json.load(open(os.path.expanduser("~/.claude/settings.json")));print("auto-update:", "ok" if d.get("extraKnownMarketplaces",{}).get("claudecode-workshop",{}).get("autoUpdate") else "vypnutý");print("statusline:", "ok" if "workshop-balik/statusline.py" in (d.get("statusLine") or {}).get("command","") else "jiná nebo žádná")'
for n in python3 git gh codex; do command -v $n >/dev/null && echo "$n: ok" || echo "$n: chybí"; done
```

- **Plugin chybí:** řekni, ať napíše `/plugin marketplace add tangero/claudecode-workshop` a `/plugin install workshop@claudecode-workshop`, nebo pustí instalační skript z README.
- **Auto-update vypnutý nebo jiná statusline:** vysvětli jednou větou, co to je, a jednou otázkou přes `AskUserQuestion` nabídni nápravu. Při souhlasu uprav `~/.claude/settings.json` Pythonem: `extraKnownMarketplaces.claudecode-workshop` = `{"source": {"source": "github", "repo": "tangero/claudecode-workshop"}, "autoUpdate": true}` a `statusLine` = `{"type": "command", "command": "python3 ~/.claude/workshop-balik/statusline.py", "padding": 0}`. Předtím soubor zazálohuj vedle. Cizí statusline nepřepisuj bez výslovného souhlasu. Statusline se objeví po restartu Claude Code.
- **Chybí `gh` nebo `codex`:** vadí jen `/codex-review`. Řekni to a pokračuj.

## 2. Vysvětli postup

Tohle vysvětli svými slovy, nejvýš na 15 řádcích:

```
nápad / PRD ──/oponentura──► stavba ──/codex-review──► merge
      ▲                                                 │
      └──── /pokracuj ◄── další session ◄── /konec ─────┘
```

- **`/oponentura`** použij, než začneš stavět. Napiš myšlenku nebo dej cestu k `docs/PRD.md`. Nezávislí oponenti najdou slabá místa, ty rozhodneš, co s nimi.
- **`/codex-review`** použij před merge PR. Proběhne jedno kolo review, opravy a verdikt. Mergovat se bude až s tvým souhlasem.
- **`/konec`** použij na konci každé session. Uloží rozhodnutí, otevřené otázky a „kde jsme skončili“ do souborů projektu. Bez něj se to, co se řeklo jen v chatu, ztratí.
- **`/pokracuj`** použij na začátku další session. Přečte předávku, ověří ji proti gitu a začne prvním krokem.

K tomu běží automaticky:

- **statusline** dole v okně: model, složka, větev, zaplnění kontextu, odhad ceny podle API a limity předplatného,
- **hlídač kontextu**: když se kontext plní (60 % a 80 %), Claude sám navrhne `/konec`,
- **bez-diffu**: po úpravě souboru uvidíš jen řádek `soubor · +12 −3`. Celý diff ukáže **ctrl+o**.

## 3. Projekt, ve kterém se právě pracuje

Zjisti, co projekt má: `CLAUDE.md`, `docs/PRD.md`, `docs/PLAN.md`, `docs/todo.md`, `docs/decisions.md`, `docs/gotchas.md` a `git rev-parse --is-inside-work-tree`.

- **Má všechno:** řekni to jednou větou. Je-li v `docs/todo.md` sekce `## Kde jsme skončili`, nabídni `/pokracuj`.
- **Něco chybí:** vypiš co a jednou otázkou přes `AskUserQuestion` nabídni, že založíš kostru. Volby:
  - „Založit chybějící soubory (Doporučeno)“,
  - „Jen CLAUDE.md a docs/todo.md“,
  - „Nic nezakládat“.

  Kostra má jen nadpisy a jednu větu, co do souboru patří, žádný vymyšlený obsah. `CLAUDE.md` dostane sekce `# Projekt`, `# Příkazy`, `# Kde co je` a `# Pravidla`. Do `# Pravidla` přijde věta *„Na začátku session si přečti `docs/todo.md` → `## Kde jsme skončili` a navaž na první krok.“* Existující soubory nepřepisuj.
- **Není to git repozitář:** řekni, že `/konec` pak necommituje a `/codex-review` nepůjde. Nabídni `git init`, ale neprováděj ho bez souhlasu.

## 4. Konec

Jedna věta s doporučeným dalším krokem podle stavu projektu: `/oponentura` nad nápadem, `/pokracuj`, nebo rovnou práce. Připomeň, že `/pruvodce` jde kdykoli spustit znovu.
