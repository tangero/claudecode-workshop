# Hlídač kontextu

Model sám nevidí, jak plný má kontext. Plný kontext je přitom nejčastější důvod, proč začne Claude zapomínat dohody a kompaktace zahodí rozdělanou práci.

`hlidac-kontextu.py` je `UserPromptSubmit` hook a při každé vaší zprávě kontext změří:

- **od 60 %:** po dokončení kroku Claude jednou větou navrhne `/konec` a novou session s `/pokracuj`,
- **od 80 %:** Claude nezačne nové větší téma, dokončí rozdělané a `/konec` navrhne hned.

Na každém prahu se ozve jen jednou. Když kontext klesne (po kompaktaci), prahy se znovu odjistí.

Přesné zaplnění bere ze [statusline](../statusline/). Bez ní ho spočítá ze záznamu session a velikost okna odhadne na 200 000 tokenů. Pro modely s oknem 1M nastavte `KONEC_OKNO=1000000`, nebo použijte statusline. Prahy se mění proměnnou `KONEC_PRAHY` (např. `50,75`).

## Instalace

Je součástí pluginu `workshop`, viz [instalace v hlavním README](../../../README.md#instalace).

Plugin registruje i `uvitani.py`: po instalaci představí balík, po aktualizaci shrne novinky z [CHANGELOG](../CHANGELOG.md) a udržuje aktuální kopii statusline v `~/.claude/workshop-balik/`.
