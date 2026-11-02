#!/usr/bin/env bash
# Instalace workshopového balíku pro Claude Code.
#
#   curl -fsSL https://raw.githubusercontent.com/tangero/claudecode-workshop/main/instaluj.sh | bash
#   nebo z naklonovaného repozitáře: ./instaluj.sh
#
# Nainstaluje pluginy workshop a bez-diffu z GitHubu, zapne jejich automatické
# aktualizace a nastaví statusline. Lze pouštět opakovaně, nic nezdvojí.
# Uklidí i starou instalaci kopírováním do ~/.claude (do zálohy, nic nemaže).
set -euo pipefail

REPO_GH="tangero/claudecode-workshop"
MARKET="claudecode-workshop"
CIL="$HOME/.claude"
BALIK="$CIL/workshop-balik"
RAW="https://raw.githubusercontent.com/$REPO_GH/main"

command -v python3 >/dev/null || { echo "Chybí python3. Na macOS: xcode-select --install"; exit 1; }
command -v claude  >/dev/null || { echo "Chybí Claude Code (příkaz claude). Návod: https://code.claude.com"; exit 1; }
command -v git     >/dev/null || { echo "Chybí git. Na macOS: xcode-select --install"; exit 1; }

mkdir -p "$BALIK"
ZALOHA="$BALIK/zaloha-$(date +%Y%m%d-%H%M%S)"

# 1. Úklid staré instalace kopírováním (do verze z 2. 11. 2026)
for s in pruvodce oponentura codex-review konec pokracuj; do
  if grep -qs "^name: $s\$" "$CIL/skills/$s/SKILL.md"; then
    mkdir -p "$ZALOHA/skills" && mv "$CIL/skills/$s" "$ZALOHA/skills/"
  fi
done
for h in hlidac-kontextu.py uvitani.py; do
  if [ -f "$CIL/hooks/$h" ]; then mkdir -p "$ZALOHA/hooks" && mv "$CIL/hooks/$h" "$ZALOHA/hooks/"; fi
done

# 2. Marketplace z GitHubu (lokální složku z dřívějška nahradí)
if claude plugin marketplace list 2>/dev/null | grep -A1 "❯ $MARKET\$" | grep -q "Folder"; then
  claude plugin marketplace remove "$MARKET" >/dev/null 2>&1 || true
fi
claude plugin marketplace add "$REPO_GH" >/dev/null 2>&1 || claude plugin marketplace update "$MARKET" >/dev/null 2>&1 || true
for p in workshop bez-diffu; do
  claude plugin install "$p@$MARKET" --scope user >/dev/null 2>&1 \
    || echo "Pozor: plugin $p se nenainstaloval. Zkuste: claude plugin install $p@$MARKET"
done

# 3. Statusline: první kopie (dál ji při startu aktualizuje plugin)
ZDE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -f "$ZDE/plugins/workshop/statusline/statusline.py" ]; then
  cp "$ZDE/plugins/workshop/statusline/statusline.py" "$BALIK/statusline.py"
else
  curl -fsSL "$RAW/plugins/workshop/statusline/statusline.py" -o "$BALIK/statusline.py" || true
fi

# 4. settings.json: auto-update, statusline, úklid starých hooků
[ -f "$CIL/settings.json" ] || echo '{}' > "$CIL/settings.json"
mkdir -p "$ZALOHA" && cp "$CIL/settings.json" "$ZALOHA/settings.json"
python3 -I - "$CIL/settings.json" "$MARKET" "$REPO_GH" <<'EOF'
import json, os, sys
p, market, repo = sys.argv[1:4]
with open(p, encoding="utf-8") as f:
    d = json.load(f)

m = d.setdefault("extraKnownMarketplaces", {}).setdefault(market, {})
m["source"] = {"source": "github", "repo": repo}
m["autoUpdate"] = True

nova = "python3 ~/.claude/workshop-balik/statusline.py"
sl = (d.get("statusLine") or {}).get("command", "")
if not sl or "statusline.py" in sl and ("~/.claude/statusline.py" in sl or "workshop-balik" in sl):
    d["statusLine"] = {"type": "command", "command": nova, "padding": 0}
    print("statusline: nastavená")
else:
    print(f"statusline: ponechána vaše ({sl}). Naši zapnete v /pruvodce.")

# Hooky ze staré instalace teď nese plugin
for udalost, skript in (("UserPromptSubmit", "hlidac-kontextu.py"), ("SessionStart", "uvitani.py")):
    skupiny = d.get("hooks", {}).get(udalost)
    if not skupiny:
        continue
    for g in skupiny:
        g["hooks"] = [h for h in g.get("hooks", []) if not any(
            f"{koren}/.claude/hooks/{skript}" in (h.get("command") or "")
            for koren in ("~", "$HOME", os.path.expanduser("~")))]
    d["hooks"][udalost] = [g for g in skupiny if g.get("hooks")]
    if not d["hooks"][udalost]:
        del d["hooks"][udalost]

with open(p, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
EOF

# 5. Uvítání v příští session
rm -f "$BALIK/uvitano"

cat <<EOF

Hotovo. Balík je nainstalovaný a bude se sám aktualizovat.

  /oponentura    před stavbou: prověří nápad nebo docs/PRD.md
  /codex-review  před merge: jedno kolo review, opravy, verdikt
  /konec         na konci session: uloží práci a „kde jsme skončili“
  /pokracuj      na začátku další session: naváže prvním krokem
  /pruvodce      vysvětlí postup a připraví strukturu projektu

Další krok: otevřete nové okno Claude Code ve svém projektu.
Claude vás přivítá a nabídne /pruvodce.

Záloha nastavení: $ZALOHA
EOF
