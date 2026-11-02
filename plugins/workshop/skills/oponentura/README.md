# /oponentura – PRD nebo myšlenka pod palbou

Než se začne stavět, pošle na zadání (nebo jen na myšlenku napsanou do chatu) 3–5 nezávislých oponentů. Ti neznají kontext session a každý se dívá z jednoho hlediska: pre-mortem, předpoklady, uživatel, proveditelnost, ekonomika… Každou závažnou námitku pak dostane ověřovatel, který ji má **vyvrátit**. Uvidíte jen to, co přežije.

Co přežije, roztřídí podle Rumsfeldovy matice:

- **mylně známé:** fakta, která nejsou fakty,
- **známé neznámé:** předpoklady, které je potřeba ověřit nejlevnějším testem, s kritériem zastavení,
- **neznámé známé:** co autor ví, ale v textu chybí,
- **neznámé neznámé:** co oponentura posoudit nemohla.

Verdikt má čtyři stupně: 🟢 stavět / 🟡 stavět po vyřešení / 🟠 nejdřív ověřit / 🔴 přepracovat. Námitky se pak probírají po jedné. Zamítnuté se zapíšou do `docs/decisions.md`, aby se příště nevracely.

Vychází z postupu `/kritika-clanku`.
