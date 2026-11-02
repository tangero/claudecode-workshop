---
name: codex-review
description: Jedno code review větve nebo PR přes Codex před merge. Nejdřív se pustí testy, nálezy se ověří a opraví v jednom běhu (nejvýš 10 kroků), dřív zamítnuté nálezy se neopakují. Na konci je verdikt a merge po potvrzení uživatele. Použij, když uživatel chce review před merge nebo napíše /codex-review.
argument-hint: "[číslo PR; bez něj nejnovější otevřený PR]"
allowed-tools: [Read, Edit, Write, Glob, Grep, Bash, AskUserQuestion]
---

# /codex-review – review → opravy → verdikt → merge po potvrzení

Odpovídej česky. **Cíl je rozhodnout, jestli změna může bezpečně do produkce, ne dosáhnout dokonalého kódu.** Codex běží **jednou**. Druhé kolo review není.

## Proč se kola opakují a jak tomu skill brání

| Příčina opakovaných kol | Pojistka |
|---|---|
| reviewer hlásí, co by chytil lint nebo testy | testy a lint se pouští **před** review (krok 2), reviewer je dostane jako hotový fakt |
| zamítnutý nález se objeví znovu v příštím review | zamítnuté nálezy jsou v `docs/review.md` a jdou do zadání, dokud se kód na daném místě nezmění (krok 1) |
| reviewer neví, co změna má dělat, a hlásí „mohlo by to být jinak“ | do zadání jde záměr: popis PR a příslušná část `docs/PRD.md` nebo `docs/PLAN.md` |
| nálezy mimo diff („když už jsem tu…“) | hlásí se jen to, co změna zavedla nebo spustila; starší vady jdou do `todo.md` |
| drobnosti s nízkou jistotou | každý nález má scénář selhání a jistotu; bez scénáře se nehlásí |
| dlouhý seznam, ve kterém se ztratí podstatné | nejvýš 10 nálezů, z toho nejvýš 5 drobných, seřazeno podle závažnosti |
| opravy se znovu reviewují | po opravách stačí zelené testy; velkou opravu skill nedělá, zapíše ji jako úkol |
| stejná třída chyby se vrací review po review | podruhé nalezená třída chyby → návrh pravidla do `CLAUDE.md` → `# Pravidla` nebo do lintu |

## 1. Co se kontroluje

- **Argument je číslo PR:** `gh pr view <číslo> --json number,title,body,headRefName,baseRefName,url`, pracuj na jeho větvi.
- **Bez argumentu:** vezmi nejnovější otevřený PR (`gh pr list --state open --limit 1 --json number,title,headRefName`). Jednou větou řekni, který PR kontroluješ. Žádný otevřený PR neexistuje: skonči a řekni to.
- Pusť `git fetch origin`. Na necommitnuté změny uživatele nesahej. Když na větvi PR překážejí, zeptej se.
- **Záměr:** zjisti, co má změna dělat. Zdrojem je tělo PR a v `docs/PRD.md` a `docs/PLAN.md` část, které se změna týká. Shrň ho do 3–5 vět. Nevíš-li, co má změna dělat, zeptej se dřív, než pustíš Codex.
- **Zamítnuté nálezy:** přečti `docs/review.md`, pokud existuje. U každého záznamu ověř, jestli se kód na jeho místě od zápisu změnil:

  ```bash
  git log --oneline <hash ze záznamu>..origin/<větev> -- <soubor ze záznamu>
  ```

  Prázdný výstup znamená, že záznam platí a jde do zadání jako „nehlásit“. Neprázdný výstup znamená, že záznam expiroval a do zadání nejde.

## 2. Testy před review

Pusť v pořadí z `CLAUDE.md` → `# Příkazy`: typecheck, lint, testy, build.

- **Něco padá:** skonči s verdiktem ❌. Review nad rozbitým stavem jen přidá šum. Uživateli napiš, co padá.
- **Všechno prošlo:** zapiš to do zadání, ať to reviewer neověřuje znovu.
- **Projekt žádné testy nemá:** napiš to do verdiktu jako výhradu.

## 3. Codex (jeden běh)

Pusť ho v samostatném worktree, ať nezasahuje do pracovní kopie:

```bash
git worktree add /tmp/codex-review-<větev> origin/<větev>
codex exec -s read-only -C /tmp/codex-review-<větev> -o <scratchpad>/codex-review-zaver.md "<zadání>" > <scratchpad>/codex-review-log.txt 2>&1
```

- `codex review --base` nejde kombinovat s vlastním zadáním, proto `codex exec` jen pro čtení. `-o` uloží jen závěrečnou zprávu.
- Pusť ho na pozadí (`run_in_background`). Běží obvykle 5–15 minut. Mezitím na větvi nic neměň.
- **Codex selže** (limit, síť, chyba CLI, není nainstalovaný): řekni to a skonči bez verdiktu. Jiný reviewer, třeba vestavěné `/code-review`, jen se souhlasem uživatele.

**Zadání** (vlož celé, s vyplněnými částmi):

> Jsi code reviewer. Posuzuješ změny `git diff origin/<base>...HEAD` v tomto repozitáři. Okolní kód číst můžeš, nic neupravuj.
>
> **Záměr změny:** <3–5 vět z kroku 1>
>
> **Už ověřeno:** <typecheck / lint / testy / build – prošlo>. Neověřuj je znovu a nehlas, co by chytily.
>
> **Nehlásit (dřív posouzeno a zamítnuto):** <platné záznamy z docs/review.md: soubor – nález – důvod; nebo „nic“>
>
> Hlas jen problémy, které změna zavedla nebo spustila a které v reálném provozu pravděpodobně nastanou. Starší vady v nezměněném kódu hlas jen tehdy, když je změna nově zpřístupňuje.
>
> Každý nález má **BLOKUJÍCÍ** nebo **DROBNÝ**, `soubor:řádek`, konkrétní scénář selhání (vstup nebo stav → špatný výsledek) a jistotu (vysoká / střední). Nález bez scénáře selhání nebo s nízkou jistotou nehlas.
>
> BLOKUJÍCÍ znamená: ztráta nebo poškození dat, chybné peníze, platby nebo fakturace, bezpečnostní díra, pád nebo chybný výsledek na běžné cestě, rozbitý build nebo nasazení, migrace, která rozbije produkci. Teoretické souběhy, nepravděpodobné vstupy, styl, pojmenování, refaktoring a chybějící testy okrajových případů jsou nanejvýš DROBNÉ. Raději je ale nehlas vůbec.
>
> Nejvýš 10 nálezů, z toho nejvýš 5 drobných, seřazených od nejzávažnějšího. Na konci napiš sekci ZÁVĚR se seznamem nálezů, nebo „Žádné nálezy“.

**Úklid:** na konci odstraň worktree příkazem `git worktree remove /tmp/codex-review-<větev>`. Když git hlásí nezařazené soubory, zkontroluj je. Soubory s diakritikou v názvu (NFC/NFD na macOS) jsou artefakt checkoutu, tam použij `--force`. Jiné změny nejdřív ukaž uživateli.

## 4. Ověření nálezů

Každý nález zkontroluj v kódu sám a **zkus ho vyvrátit**: najdi důvod, proč scénář nemůže nastat (validace výš, typ, test, který tu cestu pokrývá). Výsledek je jeden z těchto:

- **Blokující – potvrzený:** scénář je reálný a odpovídá definici. Označení od Codexu nepřebírej automaticky. Drobnost vydávanou za blokující přeřaď.
- **Drobný:** nález je pravdivý, ale provoz neohrožuje.
- **Nepotvrzený:** kód se tak nechová, nebo scénář nemůže nastat. Uveď jednou větou proč.
- **Mimo rozsah:** vada existovala už před změnou. Patří do `docs/todo.md`, ne do tohoto PR.

Pochybuješ, jestli je okrajový případ reálný? Zeptej se sám sebe: stane se to při běžném používání v příštích týdnech? Pokud ne, je to drobný nález.

## 5. Opravy (nejvýš 10 kroků)

- **Pořadí:** nejdřív **všechny potvrzené blokující**, pak **drobné**. Jeden krok je jedna oprava, testy dotčené oblasti (a typecheck, má-li ho projekt) a commit na větev PR. Související drobnosti ve stejném souboru smíš spojit do jednoho kroku.
- **Drobný nález opravuj jen tehdy, když je oprava malá, lokální a má jasný výsledek.** Vyžadovala by přestavbu, změnu rozhraní nebo zásah mimo změněné soubory? Pak ji neopravuj a zapiš ji do `docs/todo.md` s odhadem práce. Velký zásah bez nového review by nikdo nezkontroloval.
- **Minimální zásah** ve stylu okolního kódu. K opravě chyby přidej test, který bez opravy padá, pokud to jde rozumně.
- **Po 10. kroku přestaň**, i když něco zbývá.
- **Commity pushni** na větev PR, nikdy s `--force`. Nedělej deploy, produkční migrace ani zápisy do produkčních dat.
- **Po opravách nespouštěj nové review.** Stačí zelené testy.

## 6. Zápis, aby se nálezy neopakovaly

Do `docs/review.md` (chybí-li, založ ho) zapiš:

- **každý nepotvrzený nález**,
- **každý drobný nález, který uživatel rozhodl neopravovat.**

Datum vyrob `date +%F` a hash `git rev-parse --short HEAD`, obojí příkazem:

```
## Zamítnuté nálezy

- **YYYY-MM-DD** · `<hash>` · `soubor:řádek` · <nález jednou větou> · <proč se neopravuje>
```

Do `docs/todo.md` patří drobné nálezy odložené jako úkol a vady mimo rozsah.

**Opakující se třída chyby:** stejný typ nálezu se objevil už v dřívějším review (podle `docs/review.md` nebo historie PR)? Navrhni uživateli obecné pravidlo do `CLAUDE.md` → `# Pravidla` nebo pravidlo do lintu. Chybu pak chytí nástroj nebo ji Claude nezavede, místo aby ji hledal reviewer.

## 7. Verdikt

Začni jedním řádkem:

- ✅ **Lze mergovat:** nezbyl žádný blokující ani drobný nález (kromě zamítnutých) a testy prošly.
- ⚠️ **Lze mergovat s výhradou:** zbyly jen drobnosti odložené jako úkol, nebo věc k ověření po nasazení (napiš jaká).
- ❌ **Nemergovat:** zbyl blokující problém, padají testy, nebo Codex nedoběhl.

Pak krátká tabulka:

| Nález | Soubor | Hodnocení | Co se stalo |
|---|---|---|---|

Ve sloupci „Co se stalo“ je jedno z: opraveno (commit), odloženo do todo, zamítnuto (důvod), mimo rozsah, nestihlo se v 10 krocích.

Nakonec uveď počet kroků, výsledky testů a odkaz na PR.

## 8. Merge

- Při ✅ nebo ⚠️ se jednou větou zeptej, jestli mergovat. U ⚠️ připomeň výhradu. Merge do main je u většiny projektů okamžitý produkční deploy.
- Teprve po výslovném souhlasu počkej na zelené CI (`gh pr checks <PR> --watch`) a pak spusť `gh pr merge <PR> --merge`, styl merge podle zvyklosti repa. Když CI padá nebo je PR v konfliktu, nemerguj a řekni proč.
- Při ❌ merge nenabízej.
