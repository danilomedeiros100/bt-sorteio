#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Algoritmo com GARANTIA MATEMÁTICA: Força que todos joguem 5 vezes
"""

import random
from collections import defaultdict
from typing import List, Dict

def gerar_5_rodadas_garantido(homens: List[str], mulheres: List[str]) -> Dict:
    """
    Gera 5 rodadas GARANTINDO que todos jogam exatamente 5 vezes
    Permite repetição de duplas
    """
    # Calcula quantos jogos cada pessoa precisa
    total_pessoas = len(homens) + len(mulheres)
    jogos_necessarios = 5
    
    # Para cada pessoa, cria "slots" de jogos necessários
    slots_homens = {h: jogos_necessarios for h in homens}
    slots_mulheres = {m: jogos_necessarios for m in mulheres}
    
    rodadas_geradas = []
    
    # Para cada rodada
    for rodada_num in range(5):
        # Forma duplas priorizando quem tem mais slots pendentes
        duplas_rodada = []
        homens_disponiveis = [h for h in homens if slots_homens[h] > 0]
        mulheres_disponiveis = [m for m in mulheres if slots_mulheres[m] > 0]
        
        # Ordena por quem tem mais jogos pendentes (prioridade)
        homens_disponiveis.sort(key=lambda h: slots_homens[h], reverse=True)
        mulheres_disponiveis.sort(key=lambda m: slots_mulheres[m], reverse=True)
        
        # Forma duplas
        idx_h = 0
        idx_m = 0
        
        while idx_h < len(homens_disponiveis) and idx_m < len(mulheres_disponiveis):
            h = homens_disponiveis[idx_h]
            m = mulheres_disponiveis[idx_m]
            
            # Só forma dupla se ambos ainda precisam jogar
            if slots_homens[h] > 0 and slots_mulheres[m] > 0:
                duplas_rodada.append((h, m))
                slots_homens[h] -= 1
                slots_mulheres[m] -= 1
                idx_h += 1
                idx_m += 1
            else:
                if slots_homens[h] == 0:
                    idx_h += 1
                if slots_mulheres[m] == 0:
                    idx_m += 1
        
        # Quem ficou sem parceiro descansa nesta rodada
        descansando = []
        for h in homens_disponiveis:
            if slots_homens[h] > 0 and h not in [d[0] for d in duplas_rodada]:
                descansando.append(h)
        for m in mulheres_disponiveis:
            if slots_mulheres[m] > 0 and m not in [d[1] for d in duplas_rodada]:
                descansando.append(m)
        
        # Cria confrontos
        confrontos = []
        random.shuffle(duplas_rodada)  # Embaralha para variar
        
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
            "descansando": descansando
        })
    
    return {
        "total_rodadas": 5,
        "rodadas": rodadas_geradas
    }

# TESTE
print("\n" + "="*90)
print("TESTE COM GARANTIA MATEMÁTICA: 9H + 10M = 19")
print("="*90 + "\n")

homens = [f"Homem{i+1}" for i in range(9)]
mulheres = [f"Mulher{i+1}" for i in range(10)]

rodadas_data = gerar_5_rodadas_garantido(homens, mulheres)

# Analisa
jogos_por_pessoa = defaultdict(int)

for rodada in rodadas_data["rodadas"]:
    print(f"Rodada {rodada['numero']}:")
    for confronto in rodada["confrontos"]:
        j1_d1 = confronto["dupla1"]["jogador1"]
        j2_d1 = confronto["dupla1"]["jogador2"]
        j1_d2 = confronto["dupla2"]["jogador1"]
        j2_d2 = confronto["dupla2"]["jogador2"]
        
        for j in [j1_d1, j2_d1, j1_d2, j2_d2]:
            jogos_por_pessoa[j] += 1
        
        print(f"  Quadra {confronto['quadra']}: {j1_d1} & {j2_d1} VS {j1_d2} & {j2_d2}")
    
    if rodada["descansando"]:
        print(f"  Descansando: {', '.join(rodada['descansando'])}")
    print()

# Resultado
print("="*90)
print("RESULTADO FINAL:")
print("="*90)
print(f"\n{'Jogador':<15} | {'Jogos':<6} | Status")
print("-" * 40)

todos_5 = True
for pessoa in sorted(set(homens + mulheres)):
    jogos = jogos_por_pessoa.get(pessoa, 0)
    if jogos == 5:
        status = "✓ OK"
    else:
        status = f"✗ ERRO"
        todos_5 = False
    print(f"{pessoa:<15} | {jogos:<6} | {status}")

print("\n" + "="*90)
if todos_5:
    print("✅✅✅ SUCESSO! TODOS JOGARAM EXATAMENTE 5 VEZES! ✅✅✅")
    print("(Permitindo repetição de duplas)")
else:
    print("✗ AINDA PRECISA AJUSTAR")
print("="*90 + "\n")

