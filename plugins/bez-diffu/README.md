# bez-diffu – klidnější obrazovka

Mod pro Claude Code. Po každé úpravě souboru (Edit, Write, MultiEdit, NotebookEdit) nevypisuje celý diff ani obsah nového souboru. Místo něj ukáže jeden řádek:

```
  ⎿  SKILL.md · +12 −3 (diff: ctrl+o)
```

Celý diff zůstává k dispozici:
- **ctrl+o** otevře rozbalený přepis,
- **`claude --verbose`** ukáže diffy rovnou.

Chyby nástrojů se vypisují jako dřív.

Hodí se tam, kde vás zajímá výsledek a ne každá změněná řádka: dlouhé úpravy dokumentů, workshop na projektoru, práce, kterou stejně zkontroluje `/codex-review`.

Mod mění jen výpis v terminálu. To, co Claude zapíše do souborů, zůstává stejné. Dialog se žádostí o povolení úpravy ukazuje diff dál, takže ho před schválením vidíte.

## Instalace

```
/plugin install bez-diffu@claudecode-workshop
```

Nebo spolu s celým balíkem, viz [hlavní README](../../README.md#instalace). Vypnout jde v `/plugin` nebo `claude plugin disable bez-diffu@claudecode-workshop`.

Vyzkoušet bez instalace: `claude --plugin-dir plugins/bez-diffu`.
