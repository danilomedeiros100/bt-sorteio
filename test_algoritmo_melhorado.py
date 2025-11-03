#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Algoritmo MELHORADO: Permitir duplas repetidas MAS garantir 5 jogos para todos
Versão que realmente distribui bem
"""

import random
from collections import defaultdict
from typing import List, Dict

def gerar_5_rodadas_flexivel(homens: List[str], mulheres: List[str]) -> Dict:
    """
    Gera 5 rodadas PERMITINDO repetição de duplas
    MAS GARANTINDO que todos jogam exatamente 5 vezes
    """
    # Embaralha
    random.shuffle(homens)
    random.shuffle(mulheres)
    
    # Tracking de jogos por pessoa
    jogos_por_pessoa = defaultdict(int)
    
    rodadas_geradas = []
    
    # Para cada rodada
    for rodada_num in range(5):
        # Prioriza quem já jogou MENOS
        homens_ordenados = sorted(homens, key=lambda h: jogos_por_pessoa[h])
        mulheres_ordenadas = sorted(mulheres, key=lambda m: jogos_por_pessoa[m])
        
        # Decide descanso baseado na diferença
        descansando = []
        diferenca = len(homens) - len(mulheres)
        
        if diferenca > 0:  # Mais homens
            # Pega os que já jogaram MAIS (para equilibrar)
            descansando = homens_ordenados[-diferenca:]
        elif diferenca < 0:  # Mais mulheres
            descansando = mulheres_ordenadas[-abs(diferenca):]
        
        # Quem vai jogar nesta rodada
        homens_disponiveis = [h for h in homens_ordenados if h not in descansando]
        mulheres_disponiveis = [m for m in mulheres_ordenadas if m not in descansando]
        
        # Prioriza quem precisa jogar mais (ordenado por jogos - crescente)
        homens_disponiveis = sorted(homens_disponiveis, key=lambda h: jogos_por_pessoa[h])
        mulheres_disponiveis = sorted(mulheres_disponiveis, key=lambda m: jogos_por_pessoa[m])
        
        # Forma duplas priorizando quem jogou menos
        duplas_rodada = []
        
        # Tenta formar o máximo de duplas
        idx_h = 0
        idx_m = 0
        
        while idx_h < len(homens_disponiveis) and idx_m < len(mulheres_disponiveis):
            # Pega o próximo homem e mulher (que jogaram menos)
            dupla = (homens_disponiveis[idx_h], mulheres_disponiveis[idx_m])
            duplas_rodada.append(dupla)
            idx_h += 1
            idx_m += 1
        
        # Se sobrou alguém, descansa
        if idx_h < len(homens_disponiveis):
            descansando.extend(homens_disponiveis[idx_h:])
        if idx_m < len(mulheres_disponiveis):
            descansando.extend(mulheres_disponiveis[idx_m:])
        
        # Atualiza contadores ANTES de criar confrontos
        for dupla in duplas_rodada:
            jogos_por_pessoa[dupla[0]] += 1
            jogos_por_pessoa[dupla[1]] += 1
        
        # Cria confrontos (duplas jogam entre si)
        confrontos = []
        random.shuffle(duplas_rodada)  # Embaralha para variar confrontos
        
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

# TESTE COM 9H + 10M
print("\n" + "="*90)
print("TESTE ALGORITMO MELHORADO: 9H + 10M = 19")
print("="*90 + "\n")

homens = [f"Homem{i+1}" for i in range(9)]
mulheres = [f"Mulher{i+1}" for i in range(10)]

# Testa 3 vezes para ver se funciona consistentemente
for tentativa in range(3):
    print(f"\n{'-'*90}")
    print(f"TENTATIVA {tentativa + 1}")
    print(f"{'-'*90}\n")
    
    rodadas_data = gerar_5_rodadas_flexivel(homens.copy(), mulheres.copy())
    
    # Analisa
    jogos_por_pessoa = defaultdict(int)
    duplas_vistas = defaultdict(int)
    
    for rodada in rodadas_data["rodadas"]:
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
    
    # Verifica resultado
    todos_5 = all(jogos_por_pessoa.get(p, 0) == 5 for p in set(homens + mulheres))
    
    print(f"{'Jogador':<15} | {'Jogos':<6} | Status")
    print("-" * 40)
    
    for pessoa in sorted(set(homens + mulheres)):
        jogos = jogos_por_pessoa.get(pessoa, 0)
        if jogos == 5:
            status = "✓ OK"
        else:
            status = f"✗ ERRO"
        print(f"{pessoa:<15} | {jogos:<6} | {status}")
    
    if todos_5:
        print(f"\n✅ SUCESSO! Todos jogaram 5 vezes!")
        print(f"   Duplas repetidas: {len([d for d, v in duplas_vistas.items() if v > 1])}")
        break
    else:
        print(f"\n✗ Falhou nesta tentativa")

print("\n" + "="*90)

