# Claude Code workshop

Pět příkazů pro Claude Code, se kterými se práce neztrácí mezi sessions a nápady se prověří dřív, než se začnou stavět.

```
nápad / PRD ──/oponentura──► stavba ──/codex-review──► merge
      ▲                                           │
      └──── /pokracuj ◄── /clear ◄── /konec ──────┘
```

## Instalace

V terminálu jedním příkazem:

```sh
curl -fsSL https://raw.githubusercontent.com/tangero/claudecode-workshop/main/instaluj.sh | bash
```

Skript nainstaluje oba pluginy, zapne jejich automatické aktualizace a nastaví statusline. Předtím zazálohuje `~/.claude/settings.json`. Jde ho pouštět opakovaně. Kdo nechce spouštět skript z internetu, přečte si ho [tady](instaluj.sh) nebo nainstaluje balík přímo v Claude Code:

```
/plugin marketplace add tangero/claudecode-workshop
/plugin install workshop@claudecode-workshop
/plugin install bez-diffu@claudecode-workshop
/pruvodce
```

`/pruvodce` pak nabídne zapnutí automatických aktualizací a statusline. Bez něj by se plugin z cizího marketplace sám neaktualizoval.

Potřebujete Claude Code, Python 3 a git. Pro `/codex-review` navíc [GitHub CLI](https://cli.github.com) a [Codex CLI](https://github.com/openai/codex).

Po instalaci otevřete nové okno Claude Code ve svém projektu. Claude vás přivítá a nabídne `/pruvodce`, který vysvětlí postup a připraví strukturu projektu.

## Aktualizace

Probíhají samy. Claude Code se na novou verzi podívá do 10 minut po první zprávě v session a načte ji v příštím okně (nebo hned po `/reload-plugins`). Co je nového, vám Claude jednou řekne na začátku session. Seznam změn je v [CHANGELOG](plugins/workshop/CHANGELOG.md).

Ručně: `claude plugin marketplace update claudecode-workshop`.

## Příkazy

| Příkaz | Kdy | Co zanechá v projektu |
|---|---|---|
| [`/pruvodce`](plugins/workshop/skills/pruvodce/) | po instalaci, nebo kdykoli nevíte jak dál | kostru `CLAUDE.md` a `docs/`, jen se souhlasem |
| [`/oponentura`](plugins/workshop/skills/oponentura/) | před stavbou, nad PRD nebo myšlenkou | úpravy PRD, `decisions.md` (i zamítnuté námitky), otevřené otázky s testem v `todo.md` |
| [`/codex-review`](plugins/workshop/skills/codex-review/) | před merge větve nebo PR | opravy na větvi, `docs/review.md` se zamítnutými nálezy, odložené věci v `todo.md` |
| [`/konec`](plugins/workshop/skills/konec/) | na konci každé session | `## Kde jsme skončili` v `todo.md` + všechno rozhodnuté na svém místě |
| [`/pokracuj`](plugins/workshop/skills/pokracuj/) | po `/clear` nebo druhý den | nic, jen ověří předávku a začne prvním krokem |

Všechny pracují nad stejnou strukturou projektu (`CLAUDE.md`, `docs/PRD.md`, `PLAN.md`, `todo.md`, `decisions.md`, `gotchas.md`…) a stejně třídí nálezy:

- **vada:** opravit,
- **k rozhodnutí:** zeptat se, po jedné,
- **námět:** nejvýš tři,
- **drobnost:** nehlásit.

## Běží samo

| Část | Co dělá |
|---|---|
| [statusline](plugins/workshop/statusline/) | model, adresář, větev, PR, zaplnění kontextu, cena podle API, limity předplatného |
| [hlídač kontextu](plugins/workshop/hooks/) | při plném kontextu navrhne `/konec` → `/clear` → `/pokracuj` |
| [uvítání](plugins/workshop/hooks/) | po instalaci představí balík, po aktualizaci řekne, co je nového |
| [bez-diffu](plugins/bez-diffu/) | místo diffu po každé úpravě jen řádek `soubor · +12 −3`, celý diff pod **ctrl+o** |

## Materiály

- [Rychlý start](karta/rychly-start.pdf): jedna strana A4, kdy a jak který příkaz použít.
- [Jak funguje oponentura](karta/oponentura.html): průvodce pro začátečníky.

## Odinstalace

```sh
claude plugin uninstall workshop@claudecode-workshop
claude plugin uninstall bez-diffu@claudecode-workshop
claude plugin marketplace remove claudecode-workshop
```

Pak z `~/.claude/settings.json` odstraňte `statusLine` a smažte `~/.claude/workshop-balik/`.

## Autor a licence

Patrick Zandl. [MIT](LICENSE).
