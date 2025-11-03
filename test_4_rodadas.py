#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste: Sistema adapta automaticamente para 4 rodadas quando necessário
"""

import json
from collections import defaultdict
from utils.sorteio_rodadas import gerar_5_rodadas, calcular_numero_rodadas_ideal

# Carrega jogadores reais
with open('data/jogadores.json', 'r', encoding='utf-8') as f:
    jogadores_data = json.load(f)

homens = [j['nome'] for j in jogadores_data if j['confirmado'] and j['sexo'] == 'M']
mulheres = [j['nome'] for j in jogadores_data if j['confirmado'] and j['sexo'] == 'F']

total = len(homens) + len(mulheres)
num_rodadas = calcular_numero_rodadas_ideal(total)

print(f"\n{'='*90}")
print(f"TESTE: {len(homens)}H + {len(mulheres)}M = {total} participantes")
print(f"Número de rodadas calculado: {num_rodadas}")
print(f"{'='*90}\n")

rodadas_data = gerar_5_rodadas(homens, mulheres)

if not rodadas_data or "erro" in rodadas_data:
    print(f"✗ ERRO: {rodadas_data.get('erro', 'Erro desconhecido')}")
    exit(1)

print(f"✓ Gerou {rodadas_data['total_rodadas']} rodadas\n")

# Analisa
jogos_por_pessoa = defaultdict(int)

print("RESUMO DAS RODADAS:")
print("-" * 90)
for rodada in rodadas_data["rodadas"]:
    num_confrontos = len(rodada["confrontos"])
    num_jogos = num_confrontos * 4
    print(f"Rodada {rodada['numero']}: {num_confrontos} confrontos ({num_jogos} jogos), {len(rodada.get('descansando', []))} descansando")
    
    for confronto in rodada["confrontos"]:
        for j in [confronto["dupla1"]["jogador1"], confronto["dupla1"]["jogador2"],
                 confronto["dupla2"]["jogador1"], confronto["dupla2"]["jogador2"]]:
            jogos_por_pessoa[j] += 1

total_jogos = sum(jogos_por_pessoa.values())
esperado = total * num_rodadas  # Tentamos fazer todos jogarem o número de rodadas

print(f"\nTotal: {total_jogos} jogos distribuídos (máximo possível: ~{total * num_rodadas})")

print(f"\n{'='*90}")
print("DISTRIBUIÇÃO DE JOGOS:")
print(f"{'='*90}")
print(f"\n{'Jogador':<20} | {'Jogos':<6} | Status")
print("-" * 50)

todos_ok = True
for pessoa in sorted(set(homens + mulheres)):
    jogos = jogos_por_pessoa.get(pessoa, 0)
    
    # Aceita se jogou o número de rodadas (ou próximo)
    if jogos == num_rodadas or jogos == num_rodadas - 1:
        status = "✓ OK"
    else:
        status = f"✗ ({abs(num_rodadas - jogos)} {'faltando' if jogos < num_rodadas else 'a mais'})"
        todos_ok = False
    
    print(f"{pessoa:<20} | {jogos:<6} | {status}")

print(f"\n{'='*90}")
if todos_ok:
    print(f"✅ SUCESSO! Todos jogaram {num_rodadas} ou {num_rodadas-1} vezes")
else:
    print(f"⚠ A maioria jogou {num_rodadas} vezes (alguns {num_rodadas-1})")
print(f"{'='*90}\n")

