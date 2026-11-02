# /codex-review – code review před merge v jednom kole

Jedno review větve nebo PR přes Codex. Nálezy se ověří a opraví (nejvýš 10 kroků). Pak přijde verdikt ✅ / ⚠️ / ❌ a po vašem souhlasu merge.

Proti původnímu `codex-merge-review` má navíc pojistky, aby se review neopakovalo kvůli okrajovým věcem:

- **testy a lint se pouští před review:** reviewer nehlásí, co chytí nástroje,
- **do zadání jde záměr změny** z popisu PR a `docs/PRD.md`,
- **zamítnuté nálezy** se zapisují do `docs/review.md` a příští review je nevznese, dokud se kód na daném místě nezmění,
- **nálezy mimo diff** jdou do `todo.md`, ne do PR,
- **strop:** 10 nálezů, z toho nejvýš 5 drobných, každý se scénářem selhání a jistotou,
- **třída chyby, která se vrací,** se stane pravidlem v `CLAUDE.md` nebo v lintu.

Potřebuje [Codex CLI](https://github.com/openai/codex) a `gh`.

Vychází z mého skillu `codex-merge-review` (Patrick Zandl).
