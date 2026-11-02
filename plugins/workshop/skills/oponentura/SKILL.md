---
name: oponentura
description: Použij, když uživatel napíše "/oponentura" nebo chce prověřit PRD, návrh, plán či jen myšlenku dřív, než se začne stavět ("rozcupuj to", "najdi slabá místa", "dává to smysl?"). Nezávislí oponenti bez kontextu session posoudí věc každý z jednoho hlediska, námitky se pokusí vyvrátit a co přežije, se roztřídí podle Rumsfeldovy matice a probere s uživatelem.
argument-hint: "[cesta k dokumentu, nebo myšlenka v textu; bez argumentu docs/PRD.md]"
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch]
---

# /oponentura – než se začne stavět

Kód se dá otestovat, zadání ne. Chyba v PRD se projeví až v hotovém produktu, kdy je nejdražší ji opravit. Tenhle skill hledá **důvody, proč by to nemělo vyjít**, dokud změna stojí jen přepsání odstavce.

Pravidla:

- **Nechválí.** Co je v pořádku, nevypisuje.
- **Bez souhlasu nic nemění.**
- **Na kód nepatří.** Na ten je `/codex-review`.
- **Oponuje se hotová úvaha.** Na kostru dokumentu vyjdou jen nálezy „tady chybí obsah“, což autor ví. U torza se zeptej, jestli oponovat teď.

## 1. Předmět

- **Argument je cesta:** oponuj ten dokument. Bez argumentu vezmi `docs/PRD.md`, a když neexistuje, zeptej se.
- **Argument je text** (myšlenka, záměr, nápad): ulož ho doslova do `<scratchpad>/oponentura-predmet.md`. S tímhle souborem pak pracují oponenti.
- **Souvislosti:** přečti `CLAUDE.md`, a když se k předmětu vážou, i `docs/readers.md` a `docs/inputs.md`. Pak přečti `docs/decisions.md`, tedy co už se rozhodlo a hlavně **které námitky se dřív zamítly** (sekce `## Zamítnuté námitky`).
- **Jak to chápu:** nejdřív sám napiš **nejsilnější verzi** předmětu, tři věty: co se staví, pro koho a proč to má vyjít. Ukaž ji uživateli. Když ji nedokážeš napsat, je to první a největší nález: předmět neříká, co chce.

## 2. Hlediska

Vyber **3 až 5 hledisek**, a to ta, kde by chyba stála nejvíc, ne ta, kde se nález hledá nejsnáz. Každý oponent dostane jedno hledisko. Široké zadání nepokryje víc, jen rozmělní výstup.

| Hledisko | Otázka oponenta | Kdy ho vzít |
|---|---|---|
| **Pre-mortem** | Je rok poté a projekt selhal. Popiš konkrétní sled událostí. Který předpoklad padl první? | vždy |
| **Předpoklady** | Co musí platit, aby závěr platil, a dokument to nikde neříká? Čím by se to dalo nejlevněji ověřit? | vždy |
| **Uživatel** | Čti to očima cílové osoby, která nezná alternativy. Pochopí to? Uvěří tomu? Kde odpadne? Co dnes používá místo toho? | produkt pro lidi, `docs/readers.md` |
| **Proveditelnost** | Dá se to postavit, jak je to popsané? Odkud se vezmou data, kdo je zdrojem pravdy, co když vstup chybí nebo je špatně? | stavba software, `docs/inputs.md` |
| **Ekonomika** | Sedí čísla: cena, náklady, kapacita, čas? Kdo to bude dělat, jak často, a co když to neudělá? | peníze, provoz, ruční práce |
| **Alternativy a řez** | Šel by stejný cíl splnit jednodušeji, nebo vůbec jinak? Co zbude, když se rozsah zkrátí na polovinu? | velký rozsah, dlouhý plán |
| **Nevratnost a závislosti** | Které rozhodnutí nejde vzít zpět? Na čem cizím to stojí (služba, cena, zákon, jeden člověk)? | smlouvy, platby, migrace, cizí API |
| **Zneužití a právo** | Kdo má motiv to obejít? Osobní údaje, spotřebitelské právo, autorská práva. | veřejný provoz, platby, data o lidech |

U každého zvoleného hlediska napiš jednou větou, co v předmětu tě k němu vedlo. Jmenuj i **jedno hledisko, které jsi vědomě vynechal, a proč**.

## 3. Nezávislí oponenti

Pusť oponenty **paralelně** přes `Agent` (`general-purpose`), všechny v jedné odpovědi. **Kontext session jim nepředávej.** Mají jen cestu k předmětu a k souborům projektu. Oponent, který ví, jak to autor myslel, najde jen to, co autor sám.

Zadání oponenta (vlož celé):

> Jsi oponent. Posuzuješ `<cesta>` z jediného hlediska: **<hledisko – otázka z tabulky>**. Přečíst smíš i `CLAUDE.md` a `docs/` v `<kořen projektu>`. Nic neupravuj. Nechval.
>
> Nehlásit, protože to bylo dřív zamítnuto: <seznam z decisions.md, nebo „nic“>.
>
> Vrať nejvýš 5 námitek, seřazených podle síly. U každé uveď:
> - **kde:** citaci věty nebo sekci,
> - **co:** jednou větou,
> - **důsledek:** konkrétní, ne obecný („nebude to škálovat“ nestačí: kdy, při kolika, co se stane),
> - **síla:** BOŘÍ (bez vyřešení nemá smysl stavět) / OSLABUJE (sníží užitek nebo zvýší cenu) / DROBNÁ,
> - **jak to ověřit:** nejlevnější krok, který námitku potvrdí nebo vyvrátí (rozhovor, čísla, prototyp, rešerše),
> - **typ:** TVRZENÍ BEZ PODKLADU / CHYBĚJÍCÍ ČÁST / ROZPOR / RIZIKO.
>
> Nemáš-li k hledisku nic podstatného, napiš „Nic podstatného“. Nevymýšlej.

## 4. Pokus o vyvrácení

Na každou námitku se silou BOŘÍ nebo OSLABUJE pusť **ověřovatele**, opět bez kontextu session. Má jediný úkol: **námitku vyvrátit**.

Ověřovatel hledá, jestli:

- odpověď v předmětu nebo v `docs/` už není,
- důsledek opravdu plyne,
- tvrzení „to nikdo nepoužívá / to už existuje / to stojí X“ odpovídá skutečnosti. Tady smí použít web a uvádí zdroj.

Vrací jeden z výsledků:

- **obstála** (s důvodem),
- **vyvrácena** (s citací),
- **nelze rozhodnout** (s tím, co chybí).

Vyvrácené námitky uživateli neukazuj, jen je spočítej. DROBNÉ námitky neověřuj. Do závěru jdou nanejvýš jako náměty.

## 5. Roztřídění podle Rumsfeldovy matice

Námitky, které obstály, a ty, o kterých nelze rozhodnout, zařaď do pole matice:

| Pole | Co sem patří | Co s tím |
|---|---|---|
| **Mylně známé** | předmět tvrdí jako fakt něco, co ověření vyvrátilo nebo co nemá podklad | **nejvyšší priorita:** stavba by stála na omylu |
| **Známé neznámé** | předpoklad, o kterém se ví, že je nejistý: poptávka, cena, ochota platit | pojmenuj **nejlevnější test** a **kritérium zastavení** (co by muselo vyjít, abychom to nestavěli) |
| **Neznámé známé** | autor to ví nebo to v projektu někde je, ale v předmětu to chybí: implicitní předpoklad, zamlčené omezení, rozhodnutí bez důvodu | doplnit do předmětu |
| **Neznámé neznámé** | co oponentura nemohla posoudit: chybějící data, hledisko, které nikdo nedostal, trh, který se nedá ověřit od stolu | přiznat v závěru, ne zamlčet |
| **Známé známé** | co obstálo a je doložené | nevypisovat |

Pak **roztřiď podle nejhoršího rozumného důsledku**:

- **vada:** BOŘÍ, musí se vyřešit, než se začne stavět,
- **k rozhodnutí:** víc obhajitelných odpovědí, volba je na uživateli,
- **námět:** nejvýš tři,
- **drobnost:** nehlásit.

Dlouhý seznam ředí pozornost. Raději pět námitek, které něco rozhodnou, než dvacet, které autor přeskočí.

## 6. Průchod s uživatelem

Nejdřív krátký přehled, nejvýš 12 řádků:

**Verdikt:** jeden z
- 🟢 **Stavět:** nic nebourá, zbývají jen náměty,
- 🟡 **Stavět po vyřešení:** <vady, krátce>,
- 🟠 **Nejdřív ověřit:** <známé neznámé s testem, bez kterého je stavba sázka>,
- 🔴 **Přepracovat:** <co nedrží>.

**Nejsilnější verze:** <3 věty z kroku 1>
**Panel:** <hlediska> · N námitek → M po vyvrácení
**Mylně známé:** … · **Známé neznámé k ověření:** … · **Neznámé známé k doplnění:** …
**Meze oponentury:** <neznámé neznámé>

Pak námitky probírej **po jedné**, od nejsilnější. Použij `AskUserQuestion` s `header` ve tvaru `Námitka N/celkem`. Před otázkou napiš odstavec:

- citace z předmětu,
- námitka,
- co z ní plyne,
- jak dopadl pokus o vyvrácení.

Volby dávej věcné:

- konkrétní úpravy předmětu,
- „ověřit testem <X>“,
- „zamítnout, protože…“.

Nenabízej obecné volby typu „opravit / přeskočit“.

## 7. Zápis

Teprve po průchodu zapiš všechno najednou:

| Rozhodnutí | Kam |
|---|---|
| přijatá úprava | do předmětu (u myšlenky do nového `docs/PRD.md`, jen se souhlasem) a rozhodnutí do `docs/decisions.md` i s důvodem |
| ověřit testem | `docs/todo.md` → `## Otevřené otázky`: předpoklad · test · kritérium zastavení |
| zamítnuto | `docs/decisions.md` → `## Zamítnuté námitky`: datum · námitka · důvod. Příští oponentura ji nevznese znovu, dokud se předmět v tom místě nezmění |
| odloženo | `docs/todo.md` s kontextem |

Datum vyrob `date +%F`. Na konci napiš jednu větu:

- `Oponentura hotová – N námitek vypořádáno, verdikt <…>.`, nebo
- `Nevypořádáno: <co a proč>.`

**Stránka pro tým (jen na přání):** když máš nástroj `Artifact`, polož po zápisu jednu otázku: *„Mám z toho udělat stránku pro tým?“* Nic nepublikuj automaticky. I soukromá stránka odešle obsah předmětu na claude.ai. Když nástroj nemáš, otázku vynech.

Při souhlasu stránku sestav až ze zapsaného stavu, ne ze syrových námitek. Obsahuje:
- verdikt,
- nejsilnější verzi,
- vypořádané námitky s rozhodnutím a důvodem,
- otevřené testy s kritériem zastavení,
- meze oponentury.

Vyvrácené námitky a drobnosti na stránku nepatří. Do patičky napiš datum a zdrojové soubory (`docs/decisions.md`, `docs/todo.md`). Platí soubory, stránka je jen snímek. Když je výstup tak dlouhý, že by „potřeboval stránku“, nejdřív zpřísni třídění v kroku 5.

**Opakovaná oponentura nad stejným předmětem:** použij stejná hlediska jako minule. Jen tak jdou počty srovnat. Námitka, která se vrátila, znamená, že se neopravila, jen se přeformulovala. Řekni to výslovně.
