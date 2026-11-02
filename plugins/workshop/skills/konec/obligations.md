# Co kam patří

Referenční tabulka pro *Fázi 3* skillu [`/konec`](SKILL.md). Má dva směry: **od souboru k session** (co sem mělo přibýt, i když o tom nikdo nemluvil) a **od položky k souboru** (kam patří to, co jsi v session našel). Neber jako samozřejmé, že se soubory průběžně aktualizovaly – na to se zapomíná nejčastěji.

**Soubor, který projekt nemá, přeskoč** a v závěru ho uveď mezi chybějícími. Soubory navíc, které projekt uvádí v `CLAUDE.md` pod `# Kde co je`, prověř stejně – podle toho, co o nich `CLAUDE.md` říká.

## Od souboru k session

| Soubor | Co v session zakládá povinnost zápisu |
|---|---|
| `CLAUDE.md` → `# Projekt` | změnilo se, co projekt je nebo pro koho je |
| `CLAUDE.md` → `# Příkazy` | přibyl nebo se změnil příkaz na spuštění, build, testy, nasazení |
| `CLAUDE.md` → `# Kde co je` | vznikl, přesunul se nebo zanikl soubor či složka, které má Claude znát |
| `CLAUDE.md` → `# Pravidla` | vzniklo nebo se změnilo pravidlo, konvence, „takhle to tu děláme vždycky“ |
| `README.md` | změnilo se, co projekt umí nebo jak se spouští – **popis pro člověka**; pokyny pro Clauda do README nepatří, přesuň je do `CLAUDE.md` |
| `.claude/settings.json` | uživatel opakovaně schvaloval tentýž příkaz a řekl, ať se už neptá – navrhni pravidlo (zápis jen s jeho souhlasem) |
| `docs/PRD.md` | změnilo se zadání: co se staví, pro koho, co je v rozsahu a co mimo |
| `docs/PLAN.md` | úkoly se odpracovaly (odškrtnout `[x]`), nebo se plán rozešel se skutečností |
| `docs/todo.md` | něco se odložilo a je rozhodnuto, že se to udělá; **hotové položky odsud smaž**; **vždy** přepiš sekci `## Kde jsme skončili` |
| `docs/decisions.md` | padlo rozhodnutí, zvolila se varianta, něco se zamítlo, změnil se názor |
| `docs/gotchas.md` | narazilo se na záludnost, chybu nástroje nebo obejití, které z kódu nevyčtete |
| `docs/design.md` | změnilo se designové pravidlo: barvy, typografie, komponenty, rozvržení |
| `docs/readers.md` | zjistilo se něco o čtenářích: persona, návštěvnost, chování, potřeba |
| `docs/inputs.md` | přibyl nebo se změnil vstupní soubor či zdroj dat, jeho formát nebo pravidla přístupu |

## Od položky k souboru

| Co jsi našel | Kam to patří |
|---|---|
| Pravidlo, konvence, jak se v projektu pracuje | `CLAUDE.md` → `# Pravidla` |
| Rozhodnutí s důvodem a zavrženými variantami | `docs/decisions.md` |
| Záludnost, obejití, „pozor na…“ | `docs/gotchas.md` |
| Odložený úkol, u kterého je rozhodnuto, že se udělá | `docs/todo.md` |
| Nezávazný nápad, o kterém se nerozhodlo | `docs/todo.md` → `## Nápady (nerozhodnuto)` |
| Otevřená otázka (známé neznámé) | `docs/todo.md` → `## Otevřené otázky`: otázka · co chybí · jak se to zjistí |
| Hotový úkol | odškrtnout v `docs/PLAN.md`, smazat z `docs/todo.md` |
| Změna zadání | `docs/PRD.md` |
| Designové pravidlo | `docs/design.md` |
| Poznatek o čtenářích webu | `docs/readers.md` |
| Vstupní data a přístup k nim | `docs/inputs.md` |
| Co Claude během session uložil do auto memory a týká se projektu | přenes do `CLAUDE.md` nebo příslušného `docs/` souboru, aby to platilo pro každého, kdo projekt otevře |
| Obecný poznatek mimo projekt | znalostní báze – jen pokud ji `CLAUDE.md` uvádí a uživatel souhlasí |

## Jak zápis v souboru dopadne

| Nález | Pole matice | Co uděláš |
|---|---|---|
| v souboru chybí | neznámé známé | doplň v plné kvalitě |
| v souboru je, ale session to vyvrátila | mylně známé | přepiš na platné znění, starou větu nenech vedle |
| v souboru je jako fakt, ale nikdo to neověřil | mylně známé | ověř proti zdroji, jinak přepiš na otevřenou otázku |
| je to na dvou místech | – | nech na jednom, druhé ať odkazuje |
| je to ve špatném souboru | – | přesuň podle tabulky výš |
| je to tam a platí | známé známé | nic |
