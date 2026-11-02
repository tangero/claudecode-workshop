---
name: pokracuj
description: Použij na začátku session, když uživatel napíše "/pokracuj", "navaž", "kde jsme skončili" nebo se vrací k rozdělané práci. Přečte předávku `## Kde jsme skončili` v docs/todo.md, kterou zapsal /konec, ověří ji proti skutečnému stavu repozitáře, shrne ji a začne prvním krokem.
allowed-tools: [Read, Glob, Grep, Bash, AskUserQuestion]
---

# /pokracuj – převzetí směny

Protějšek `/konec`. Předávka je jen tvrzení o stavu z doby, kdy se psala. Než na ni navážeš, ověř ji. Mezitím mohl na projektu pracovat někdo jiný, jiná session nebo uživatel ručně.

## 1. Načti předávku

1. Přečti `docs/todo.md` → `## Kde jsme skončili`. Pak `CLAUDE.md` → `# Pravidla`.
2. **Sekce chybí:** řekni to jednou větou. Nabídni stručný přehled ze zbytku `docs/todo.md`, `docs/PLAN.md` a `git log --oneline -10` a skonči tím otázkou, čím začít. Předávku si nevymýšlej.

## 2. Ověř ji proti zdroji

Každý bod porovnej se skutečností. Použij příkazy, ne domněnky:

| V předávce | Ověř |
|---|---|
| větev a commit | `git branch --show-current`, `git log --oneline <hash>..HEAD` |
| rozdělané soubory | `git status --porcelain`, existence souborů |
| padající test, rozbitý build | nespouštěj nic drahého; jen když to `CLAUDE.md` → `# Příkazy` uvádí jako rychlou kontrolu |
| otevřené otázky | jsou pořád v `## Otevřené otázky`, nebo je mezitím někdo rozhodl v `decisions.md`? |

Rozdíly ohlas jako **posun**:

- **commity po předávce:** kdo, kdy a čeho se týkají (`git log <hash>..HEAD --stat`),
- **jiná větev:** na které jsme a kde leží ta z předávky,
- **předávka tvrdí necommitnuté změny, ale nejsou** (nebo obráceně).

Posun neopravuj. Jen ho ukaž, protože mění první krok.

## 3. Shrnutí

Nejvýš osm řádků, v Markdownu:

**Navazuji na:** <datum předávky> · větev `<větev>` · <na čem se dělalo, jednou větou>
**Stav:** <rozdělané, ověřeno> · <posun, nebo „beze změn od předávky“>
**Důsledky, které platí:** <z předávky, jen ty, které se týkají prvního kroku>
**Čeká na tebe:** <otevřené otázky, nebo „nic“>
**První krok:** <z předávky, upravený podle posunu>

## 4. Začni

- **Na nic se nečeká a posun není:** rovnou proveď první krok. Neptej se „mám začít?“.
- **Čeká se na rozhodnutí uživatele, nebo posun mění první krok:** polož jednu otázku přes `AskUserQuestion` s věcnými variantami a pak pokračuj.
- **Předávku neměň.** Přepíše ji až příští `/konec`.
