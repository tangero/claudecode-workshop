# /konec – předávka směny

Skill pro Claude Code. Na konci session uloží do souborů projektu všechno, co se v ní zjistilo a rozhodlo, aby další session navázala bez ztráty kontextu.

- Přečte **celý záznam session**, i tu část, kterou už kompaktace vyhodila z paměti.
- Každý váš prompt odškrtne v evidenci a na konci řekne poměr („prompty 11/11“).
- Projde session podle **Rumsfeldovy matice**:
  - **známé známé:** rozhodnutí, pravidla, záludnosti → zapíše je i s důvodem,
  - **známé neznámé:** otevřené otázky → zapíše je jako otevřené, ne jako tvrzení,
  - **neznámé známé:** co padlo a nikdo si toho nevšiml → dohledá to a probere s vámi,
  - **mylně známé:** co v souborech platilo a session to vyvrátila → opraví to podle zdroje,
  - **neznámé neznámé:** co skill neviděl → přizná to s počty.
- Sporné věci s vámi probere jednu po druhé, drobnosti neřeší.
- Commitne jen soubory, do kterých sám zapsal.

## Struktura projektu

```
projekt/
├─ CLAUDE.md
├─ README.md
├─ .claude/settings.json
└─ docs/
   ├─ PRD.md, PLAN.md, todo.md, decisions.md, gotchas.md
   ├─ design.md, readers.md, inputs.md
   └─ … další pomocné soubory (vypsané v CLAUDE.md)
```

Soubory, které projekt nemá, skill nezakládá. Jen je vypíše.

## Instalace

Je součástí pluginu `workshop`, viz [instalace v hlavním README](../../../README.md#instalace).

Na konci práce napište v Claude Code `/konec`. Příští session začněte `/pokracuj` (nebo jen otevřete projekt: `CLAUDE.md` odkáže na předávku).

Skript `scripts/prepis.py` jde pustit i samostatně, potřebuje jen Python 3:

```sh
python3 scripts/prepis.py prehled ~/.claude/projects/<slug>/<session-id>.jsonl
```
