#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync data/rodadas_mista.json rounds with what is currently rendered at
http://127.0.0.1:5001/rodadas?categoria=mista (local service must be running).

No code changes, only local JSON update.
"""
import json
import re
import sys
from urllib.request import urlopen, Request
from html import unescape
from pathlib import Path

MISTA_URL = "http://127.0.0.1:5001/rodadas?categoria=mista"
JSON_PATH = Path(__file__).resolve().parent.parent / "data" / "rodadas_mista.json"

ROUND_H_RE = re.compile(r"<h2[^>]*>\s*<i[^>]*>\s*</i>\s*RODADA\s+(\d+)\s*</h2>", re.IGNORECASE)
MATCH_BLOCK_RE = re.compile(
    r'<div class="matchup-container[^>]*?data-jogadores="([^"]*)".*?'
    r'Quadra\s*(\d+).*?'
    r'(?:</span>\s*</div>|</div>)',  # stop after quadra block; we don’t rely on inner content parsing
    re.IGNORECASE | re.DOTALL
)
DESC_RE = re.compile(r'data-descansando="([^"]*)"', re.IGNORECASE)

def fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def parse_rounds(html: str):
    """
    Return list of rounds:
    [
      {
        "numero": int,
        "confrontos": [ { "dupla1": {...}, "dupla2": {...}|None, "resultado": {...}, "quadra": int }, ... ],
        "descansando": [ ... ]
      },
      ...
    ]
    """
    rounds = []
    # Split by round header
    parts = list(ROUND_H_RE.split(html))
    # parts = [before, num1, after1, num2, after2, ...]
    if len(parts) < 3:
        return []
    it = iter(parts)
    _ = next(it)  # skip prefix
    for num_str, block in zip(it, it):
        try:
            numero = int(num_str)
        except ValueError:
            continue
        # Extract match blocks within this round block (until next header, but we already split)
        confrontos = []
        for m in MATCH_BLOCK_RE.finditer(block):
            players_csv = unescape(m.group(1))
            quadra = int(m.group(2))
            # Prefer the data-jogadores attribute which lists players in order: j1,j2,j3,j4
            p = [s.strip() for s in players_csv.split(",") if s.strip()]
            if len(p) >= 4:
                d1 = {"jogador1": p[0], "jogador2": p[1]}
                d2 = {"jogador1": p[2], "jogador2": p[3]}
            elif len(p) >= 2:
                d1 = {"jogador1": p[0], "jogador2": p[1]}
                d2 = None
            else:
                continue
            confronto = {
                "dupla1": d1,
                "dupla2": d2,
                "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False},
                "quadra": quadra
            }
            rounds.append((numero, confronto))
        # Descansando for this block
        desc = []
        desc_match = DESC_RE.search(block)
        if desc_match:
            raw = unescape(desc_match.group(1)).strip()
            if raw:
                desc = [s.strip() for s in raw.split(",") if s.strip()]
        # group confrontos by numero
    # Consolidate by round
    round_map = {}
    for numero, conf in rounds:
        round_map.setdefault(numero, {"numero": numero, "confrontos": [], "descansando": []})
        round_map[numero]["confrontos"].append(conf)
    # For descansando per round, reparse with per-block approach
    # Simpler: pass 2 – iterate again to attach descansando by matching nearest header block
    parts2 = list(ROUND_H_RE.finditer(html))
    for i, m in enumerate(parts2):
        numero = int(m.group(1))
        start = m.end()
        end = parts2[i+1].start() if i+1 < len(parts2) else len(html)
        block = html[start:end]
        desc_match = DESC_RE.search(block)
        if desc_match:
            raw = unescape(desc_match.group(1)).strip()
            desc = [s.strip() for s in raw.split(",") if s.strip()]
            round_map.setdefault(numero, {"numero": numero, "confrontos": [], "descansando": []})
            round_map[numero]["descansando"] = desc
    # Sort confrontos by quadra
    result = []
    for k in sorted(round_map.keys()):
        rd = round_map[k]
        rd["confrontos"].sort(key=lambda c: c.get("quadra", 0))
        result.append(rd)
    return result

def main():
    try:
        html = fetch_html(MISTA_URL)
    except Exception as e:
        print("Erro ao acessar URL local:", e, file=sys.stderr)
        sys.exit(1)
    rounds = parse_rounds(html)
    if not rounds:
        print("Não foi possível extrair as rodadas da página. Verifique se o serviço local está exibindo /rodadas?categoria=mista")
        sys.exit(2)
    # Load current JSON to keep metadata
    if JSON_PATH.exists():
        data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        meta = {
            "categoria": data.get("categoria", "mista"),
            "data_sorteio": data.get("data_sorteio"),
            "total_homens": data.get("total_homens"),
            "total_mulheres": data.get("total_mulheres"),
            "total_rodadas": data.get("total_rodadas", len(rounds)),
        }
    else:
        meta = {
            "categoria": "mista",
            "data_sorteio": None,
            "total_homens": None,
            "total_mulheres": None,
            "total_rodadas": len(rounds),
        }
    out = dict(meta)
    out["rodadas"] = rounds
    JSON_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Atualizado: {JSON_PATH}")
    print(f"Rodadas sincronizadas a partir do HTML. Total de rodadas: {len(rounds)}")

if __name__ == "__main__":
    main()


