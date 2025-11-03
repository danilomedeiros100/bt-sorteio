#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste com os jogadores REAIS do sistema
10 Homens + 9 Mulheres = 19 participantes
"""

import json
from collections import defaultdict
from utils.sorteio_rodadas import gerar_5_rodadas

# Cores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*90}{Colors.END}")
print(f"{Colors.BOLD}{Colors.CYAN}TESTE COM JOGADORES REAIS: 10H + 9M = 19 PARTICIPANTES{Colors.END}")
print(f"{Colors.BOLD}{Colors.CYAN}{'='*90}{Colors.END}\n")

# Carrega jogadores reais
with open('data/jogadores.json', 'r', encoding='utf-8') as f:
    jogadores_data = json.load(f)

# Separa confirmados por gênero
homens = [j['nome'] for j in jogadores_data if j['confirmado'] and j['sexo'] == 'M']
mulheres = [j['nome'] for j in jogadores_data if j['confirmado'] and j['sexo'] == 'F']

print(f"{Colors.BOLD}PARTICIPANTES:{Colors.END}")
print(f"  Homens ({len(homens)}): {', '.join(homens)}")
print(f"  Mulheres ({len(mulheres)}): {', '.join(mulheres)}")
print(f"  Total: {len(homens) + len(mulheres)}\n")

# Gera rodadas
print(f"{Colors.BOLD}GERANDO 5 RODADAS...{Colors.END}")
rodadas_data = gerar_5_rodadas(homens, mulheres)

if not rodadas_data or "erro" in rodadas_data:
    print(f"{Colors.RED}✗ FALHOU: {rodadas_data.get('erro', 'Erro desconhecido')}{Colors.END}")
    exit(1)

print(f"{Colors.GREEN}✓ Gerou {len(rodadas_data['rodadas'])} rodadas{Colors.END}\n")

# Conta jogos por pessoa
jogos_por_pessoa = defaultdict(int)

for rodada in rodadas_data["rodadas"]:
    for confronto in rodada["confrontos"]:
        for jogador in [confronto["dupla1"]["jogador1"], confronto["dupla1"]["jogador2"],
                       confronto["dupla2"]["jogador1"], confronto["dupla2"]["jogador2"]]:
            jogos_por_pessoa[jogador] += 1

# Análise
print(f"{Colors.BOLD}DISTRIBUIÇÃO DE JOGOS:{Colors.END}\n")
print(f"{'Jogador':<20} | {'Jogos':<6} | Status")
print("-" * 60)

todos_com_5 = True
problemas = []

for pessoa in sorted(set(homens + mulheres)):
    jogos = jogos_por_pessoa.get(pessoa, 0)
    
    if jogos == 5:
        status = f"{Colors.GREEN}✓ OK{Colors.END}"
    else:
        status = f"{Colors.RED}✗ ERRO ({abs(5-jogos)} {'a mais' if jogos > 5 else 'faltando'}){Colors.END}"
        todos_com_5 = False
        problemas.append(f"{pessoa}: {jogos} jogos")
    
    print(f"{pessoa:<20} | {jogos:<6} | {status}")

# Resultado
print(f"\n{Colors.BOLD}{'='*90}{Colors.END}")
if todos_com_5:
    print(f"{Colors.GREEN}{Colors.BOLD}✓✓✓ SUCESSO! TODOS JOGAM EXATAMENTE 5 VEZES! ✓✓✓{Colors.END}\n")
else:
    print(f"{Colors.RED}{Colors.BOLD}✗ FALHOU: {len(problemas)} pessoa(s) não jogaram 5 vezes{Colors.END}\n")
    print(f"{Colors.YELLOW}Problemas encontrados:{Colors.END}")
    for p in problemas:
        print(f"  - {p}")
print(f"{Colors.BOLD}{'='*90}{Colors.END}\n")

