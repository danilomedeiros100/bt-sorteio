#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de fluxo completo do sistema:
- Valida arquivos de rodadas (mista, masculino, feminino)
- Simula preenchimento de resultados (placares) em memória
- Calcula ranking para cada categoria usando as mesmas funções do backend

OBS: Este script NÃO sobrescreve os arquivos JSON existentes.
É apenas uma validação offline, usando os dados atuais.
"""

import json
from collections import defaultdict
from pathlib import Path

from app import (
    calcular_ranking_individual,
    separar_ranking_por_genero,
    carregar_jogadores,
)


BASE = Path("data")


def validar_rodadas(path: Path, categoria_label: str):
    """Valida rodadas: jogos por jogador e duplas repetidas."""
    print("=" * 80)
    print(f"VALIDAÇÃO DE RODADAS - {categoria_label.upper()} ({path.name})")
    print("=" * 80)

    if not path.exists():
        print("Arquivo não encontrado. Pulando...\n")
        return None

    with path.open("r", encoding="utf-8") as f:
        dados = json.load(f)

    jogos_por_jogador = defaultdict(int)
    duplas = set()
    duplas_repetidas = []

    rodadas = dados.get("rodadas", [])
    total_confrontos = 0

    for rodada in rodadas:
        num = rodada.get("numero")
        for c in rodada.get("confrontos", []):
            total_confrontos += 1
            d1 = c.get("dupla1")
            d2 = c.get("dupla2")

            if d1:
                t1 = tuple(sorted([d1["jogador1"], d1["jogador2"]]))
                if t1 in duplas:
                    duplas_repetidas.append((num, t1))
                duplas.add(t1)
                jogos_por_jogador[d1["jogador1"]] += 1
                jogos_por_jogador[d1["jogador2"]] += 1

            if d2:
                t2 = tuple(sorted([d2["jogador1"], d2["jogador2"]]))
                if t2 in duplas:
                    duplas_repetidas.append((num, t2))
                duplas.add(t2)
                jogos_por_jogador[d2["jogador1"]] += 1
                jogos_por_jogador[d2["jogador2"]] += 1

    print(f"Total de rodadas: {dados.get('total_rodadas')}")
    print(f"Total de confrontos: {total_confrontos}")
    print(f"Total de duplas únicas: {len(duplas)}")

    jogos_esperados = dados.get("jogos_por_pessoa")
    problemas_jogos = []

    print("\nJogos por jogador:")
    for j, n in sorted(jogos_por_jogador.items()):
        ok = (jogos_esperados is None) or (n == jogos_esperados)
        print(f"  {'✓' if ok else '✗'} {j}: {n} jogos")
        if not ok:
            problemas_jogos.append((j, n))

    print("\nDuplas repetidas:")
    if duplas_repetidas:
        for num, dupla in duplas_repetidas:
            print(f"  Rodada {num}: {dupla[0]} + {dupla[1]}")
    else:
        print("  Nenhuma")

    print("\nResumo:")
    if jogos_esperados is not None:
        print(f"  Jogos esperados por jogador: {jogos_esperados}")
    if not problemas_jogos and not duplas_repetidas:
        print("  ✓ Arquivo consistente com as regras (sem problemas encontrados).")
    else:
        if problemas_jogos:
            print(f"  ✗ {len(problemas_jogos)} jogador(es) com quantidade diferente de jogos.")
        if duplas_repetidas:
            print(f"  ✗ {len(duplas_repetidas)} dupla(s) repetida(s).")

    print()
    return dados


def simular_resultados(dados: dict) -> dict:
    """
    Retorna uma cópia das rodadas com resultados simulados:
    - Alterna vitórias entre dupla1 e dupla2 para distribuir vitórias.
    """
    import copy

    dados_sim = copy.deepcopy(dados)
    vence_dupla1 = True

    for rodada in dados_sim.get("rodadas", []):
        for c in rodada.get("confrontos", []):
            if not c.get("dupla2"):
                # Confronto BYE – mantém sem resultado
                continue

            if vence_dupla1:
                c["resultado"]["games_dupla1"] = 6
                c["resultado"]["games_dupla2"] = 4
            else:
                c["resultado"]["games_dupla1"] = 4
                c["resultado"]["games_dupla2"] = 6

            c["resultado"]["finalizado"] = True
            vence_dupla1 = not vence_dupla1

    return dados_sim


def testar_ranking_masculino(dados_masc: dict):
    print("=" * 80)
    print("RANKING - MASCULINO (simulação)")
    print("=" * 80)
    dados_sim = simular_resultados(dados_masc)
    ranking = calcular_ranking_individual(dados_sim["rodadas"])

    print("\nTop 5 jogadores:")
    for pos, j in enumerate(ranking[:5], start=1):
        print(
            f"  {pos}. {j['nome']} - V:{j['vitorias']} D:{j['derrotas']} "
            f"Saldo:{j['games_feitos'] - j['games_sofridos']}"
        )
    print()


def testar_ranking_feminino(dados_fem: dict):
    print("=" * 80)
    print("RANKING - FEMININO (simulação)")
    print("=" * 80)
    dados_sim = simular_resultados(dados_fem)
    ranking = calcular_ranking_individual(dados_sim["rodadas"])

    print("\nTop 5 jogadoras:")
    for pos, j in enumerate(ranking[:5], start=1):
        print(
            f"  {pos}. {j['nome']} - V:{j['vitorias']} D:{j['derrotas']} "
            f"Saldo:{j['games_feitos'] - j['games_sofridos']}"
        )
    print()


def testar_ranking_mista(dados_mista: dict):
    print("=" * 80)
    print("RANKING - MISTA (simulação)")
    print("=" * 80)
    dados_sim = simular_resultados(dados_mista)
    ranking_ind = calcular_ranking_individual(dados_sim["rodadas"])

    jogadores = carregar_jogadores()
    ranking_sep = separar_ranking_por_genero(ranking_ind, jogadores)

    print("\nTop 5 Masculino (Mista):")
    for pos, j in enumerate(ranking_sep["masculino"][:5], start=1):
        print(
            f"  {pos}. {j['nome']} - V:{j['vitorias']} D:{j['derrotas']} "
            f"Saldo:{j['games_feitos'] - j['games_sofridos']}"
        )

    print("\nTop 5 Feminino (Mista):")
    for pos, j in enumerate(ranking_sep["feminino"][:5], start=1):
        print(
            f"  {pos}. {j['nome']} - V:{j['vitorias']} D:{j['derrotas']} "
            f"Saldo:{j['games_feitos'] - j['games_sofridos']}"
        )
    print()


def main():
    # 1) Validar rodadas
    dados_masc = validar_rodadas(BASE / "rodadas_masculino.json", "masculino")
    dados_fem = validar_rodadas(BASE / "rodadas_feminino.json", "feminino")
    dados_mista = validar_rodadas(BASE / "rodadas_mista.json", "mista")

    # 2) Simular resultados e validar ranking
    if dados_masc:
        testar_ranking_masculino(dados_masc)
    if dados_fem:
        testar_ranking_feminino(dados_fem)
    if dados_mista:
        testar_ranking_mista(dados_mista)


if __name__ == "__main__":
    main()


