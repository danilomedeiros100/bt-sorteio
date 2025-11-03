#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste: Permitir duplas repetidas mas garantir 5 jogos para todos
"""

import random
from collections import defaultdict
from typing import List, Dict

def gerar_5_rodadas_permitir_repeticao(homens: List[str], mulheres: List[str]) -> Dict:
    """
    Gera 5 rodadas PERMITINDO repetição de duplas
    MAS GARANTINDO que todos jogam exatamente 5 vezes
    """
    # Embaralha para aleatoriedade
    homens_shuffled = homens.copy()
    mulheres_shuffled = mulheres.copy()
    random.shuffle(homens_shuffled)
    random.shuffle(mulheres_shuffled)
    
    # Tracking de quantos jogos cada pessoa já fez
    jogos_por_pessoa = defaultdict(int)
    
    rodadas_geradas = []
    
    # Para cada rodada
    for rodada_num in range(5):
        # Decide quem vai descansar nesta rodada
        # Quem já jogou MENOS, joga primeiro
        homens_ordenados = sorted(homens_shuffled, key=lambda h: jogos_por_pessoa[h])
        mulheres_ordenadas = sorted(mulheres_shuffled, key=lambda m: jogos_por_pessoa[m])
        
        descansando = []
        diferenca = len(homens_ordenados) - len(mulheres_ordenadas)
        
        if diferenca > 0:  # Mais homens
            # Homens com MENOS jogos descansam primeiro (para equilibrar depois)
            descansando.extend(homens_ordenados[:diferenca])
        elif diferenca < 0:  # Mais mulheres
            descansando.extend(mulheres_ordenadas[:-diferenca])
        
        # Quem vai jogar
        homens_disponiveis = [h for h in homens_ordenados if h not in descansando]
        mulheres_disponiveis = [m for m in mulheres_ordenadas if m not in descansando]
        
        # Prioriza quem já jogou MENOS para formar duplas primeiro
        # Isso garante que todos consigam jogar
        homens_prioridade = sorted(homens_disponiveis, key=lambda h: jogos_por_pessoa[h])
        mulheres_prioridade = sorted(mulheres_disponiveis, key=lambda m: jogos_por_pessoa[m])
        
        # Embaralha um pouco mas mantém prioridade
        random.shuffle(homens_prioridade[:max(1, len(homens_prioridade)//2)])
        random.shuffle(mulheres_prioridade[:max(1, len(mulheres_prioridade)//2)])
        
        # Forma duplas (pode repetir!)
        duplas_rodada = []
        idx_h = 0
        idx_m = 0
        
        while idx_h < len(homens_prioridade) and idx_m < len(mulheres_prioridade):
            dupla = (homens_prioridade[idx_h], mulheres_prioridade[idx_m])
            duplas_rodada.append(dupla)
            idx_h += 1
            idx_m += 1
        
        # Se sobrou alguém, pode descansar ou tentar ajustar
        if idx_h < len(homens_prioridade):
            descansando.extend(homens_prioridade[idx_h:])
        if idx_m < len(mulheres_prioridade):
            descansando.extend(mulheres_prioridade[idx_m:])
        
        # Atualiza contadores
        for dupla in duplas_rodada:
            jogos_por_pessoa[dupla[0]] += 1
            jogos_por_pessoa[dupla[1]] += 1
        
        # Cria confrontos
        confrontos = []
        metade = len(duplas_rodada) // 2
        
        for i in range(metade):
            dupla1 = duplas_rodada[i]
            dupla2_idx = metade + i
            
            if dupla2_idx < len(duplas_rodada):
                dupla2 = duplas_rodada[dupla2_idx]
                
                confronto = {
                    "quadra": i + 1,
                    "dupla1": {
                        "jogador1": dupla1[0],
                        "jogador2": dupla1[1]
                    },
                    "dupla2": {
                        "jogador1": dupla2[0],
                        "jogador2": dupla2[1]
                    },
                    "resultado": {
                        "games_dupla1": 0,
                        "games_dupla2": 0,
                        "finalizado": False
                    }
                }
                confrontos.append(confronto)
        
        rodadas_geradas.append({
            "numero": rodada_num + 1,
            "confrontos": confrontos,
            "descansando": list(set(descansando))
        })
    
    return {
        "total_rodadas": 5,
        "rodadas": rodadas_geradas
    }

# TESTE
print("\n" + "="*90)
print("TESTE: PERMITIR DUPLAS REPETIDAS - 9H + 10M = 19")
print("="*90 + "\n")

homens = [f"Homem{i+1}" for i in range(9)]
mulheres = [f"Mulher{i+1}" for i in range(10)]

rodadas_data = gerar_5_rodadas_permitir_repeticao(homens, mulheres)

# Analisa
jogos_por_pessoa = defaultdict(int)
duplas_vistas = defaultdict(int)

for rodada in rodadas_data["rodadas"]:
    print(f"Rodada {rodada['numero']}:")
    for confronto in rodada["confrontos"]:
        j1_d1 = confronto["dupla1"]["jogador1"]
        j2_d1 = confronto["dupla1"]["jogador2"]
        j1_d2 = confronto["dupla2"]["jogador1"]
        j2_d2 = confronto["dupla2"]["jogador2"]
        
        for j in [j1_d1, j2_d1, j1_d2, j2_d2]:
            jogos_por_pessoa[j] += 1
        
        dupla1 = tuple(sorted([j1_d1, j2_d1]))
        dupla2 = tuple(sorted([j1_d2, j2_d2]))
        duplas_vistas[dupla1] += 1
        duplas_vistas[dupla2] += 1
        
        print(f"  Quadra {confronto['quadra']}: {j1_d1} & {j2_d1} VS {j1_d2} & {j2_d2}")
    
    if rodada["descansando"]:
        print(f"  Descansando: {', '.join(rodada['descansando'])}")
    print()

# Resultado
print("="*90)
print("RESULTADO:")
print("="*90)
print(f"\n{'Jogador':<15} | {'Jogos':<6} | Status")
print("-" * 40)

todos_5 = True
for pessoa in sorted(set(homens + mulheres)):
    jogos = jogos_por_pessoa.get(pessoa, 0)
    if jogos == 5:
        status = "✓ OK"
    else:
        status = f"✗ ERRO ({5-jogos} faltando)"
        todos_5 = False
    print(f"{pessoa:<15} | {jogos:<6} | {status}")

# Duplas repetidas
duplas_rep = [d for d, v in duplas_vistas.items() if v > 1]
print(f"\nDuplas que se repetiram: {len(duplas_rep)}")
for dupla, vezes in [(d, duplas_vistas[d]) for d in duplas_rep]:
    print(f"  {dupla[0]} & {dupla[1]}: {vezes} vezes")

print("\n" + "="*90)
if todos_5:
    print("✓✓✓ SUCESSO! TODOS JOGARAM 5 VEZES! ✓✓✓")
    print("(Mesmo com algumas duplas repetidas)")
else:
    print("✗ AINDA FALHOU - Precisa melhorar algoritmo")
print("="*90 + "\n")

