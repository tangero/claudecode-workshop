# Statusline

Dva řádky dole v Claude Code:

```
Opus 5.5 · high │ rodokmen │ ⎇ main ●3 ↑1 │ PR #12 ✓
▓▓▓▓▓▓▓░░░ 72 % kontextu (145k/200k) → /konec │ ≈ $1.84 API · 37 min │ 5h 31 % · týden 12 % │ +120 −15
```

| Část | Co znamená |
|---|---|
| model · effort (⚡ = fast mode) | čím se právě pracuje |
| adresář | aktuální složka; když se Claude přesune do podsložky, je vidět `projekt/podsložka` |
| ⎇ větev ●N ↑a ↓b | větev, počet necommitnutých souborů, kolik commitů je napřed a pozadu proti remote |
| PR #n ✓ ✗ … ✎ | otevřený PR k větvi a stav review |
| pruh kontextu | zelená do 60 %, žlutá do 80 %, pak červená; od 70 % ukazuje `→ /konec` |
| ≈ $ API | odhad podle ceníku API. Na předplatném Pro, Max nebo Ultra to **neplatíte**, ale vidíte, kolik by to stálo |
| 5h / týden | čerpání limitů předplatného (jen na Pro, Max a Ultra) |
| +/− | řádky změněné v této session |

Stačí Python 3, jiné balíčky nejsou potřeba. Skript navíc ukládá zaplnění kontextu do `~/.claude/stav-kontextu/`, odkud ho čte [hlídač kontextu](../hooks/).

## Instalace

Je součástí pluginu `workshop`, viz [instalace v hlavním README](../../../README.md#instalace).

Plugin nemůže sám nastavit statusline, to udělá instalační skript nebo `/pruvodce`. Do `~/.claude/settings.json` přijde:

```json
"statusLine": { "type": "command", "command": "python3 ~/.claude/workshop-balik/statusline.py" }
```

Kopii v `~/.claude/workshop-balik/` při každém startu session aktualizuje plugin, takže se statusline obnovuje spolu s ním.
