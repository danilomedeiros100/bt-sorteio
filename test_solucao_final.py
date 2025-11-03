#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solução Final: Força todos a jogarem 5 vezes permitindo duplas repetidas
"""

import random
from collections import defaultdict

def gerar_5_rodadas_final(homens: list, mulheres: list):
    """
    Estratégia: Garantir que todos joguem 5 vezes
    Permite repetição de duplas
    """
    # Calcula total de jogos necessários por pessoa
    todas_pessoas = homens + mulheres
    jogos_necessarios_por_pessoa = {p: 5 for p in todas_pessoas}
    
    rodadas = []
    
    # Para cada rodada
    for rodada_num in range(5):
        # Quem ainda precisa jogar nesta rodada?
        homens_pendentes = [h for h in homens if jogos_necessarios_por_pessoa[h] > 0]
        mulheres_pendentes = [m for m in mulheres if jogos_necessarios_por_pessoa[m] > 0]
        
        # Ordena por quem tem mais jogos pendentes (prioridade)
        homens_pendentes.sort(key=lambda h: jogos_necessarios_por_pessoa[h], reverse=True)
        mulheres_pendentes.sort(key=lambda m: jogos_necessarios_por_pessoa[m], reverse=True)
        
        # Forma duplas priorizando quem precisa mais
        duplas_rodada = []
        idx_h = 0
        idx_m = 0
        
        # Forma o máximo de duplas possível
        while idx_h < len(homens_pendentes) and idx_m < len(mulheres_pendentes):
            h = homens_pendentes[idx_h]
            m = mulheres_pendentes[idx_m]
            
            # Forma a dupla
            duplas_rodada.append((h, m))
            jogos_necessarios_por_pessoa[h] -= 1
            jogos_necessarios_por_pessoa[m] -= 1
            idx_h += 1
            idx_m += 1
        
        # Quem ficou sem dupla descansa
        descansando = []
        # Homens que ainda precisam mas não formaram dupla
        for h in homens_pendentes:
            if jogos_necessarios_por_pessoa[h] > 0 and h not in [d[0] for d in duplas_rodada]:
                descansando.append(h)
        # Mulheres que ainda precisam mas não formaram dupla
        for m in mulheres_pendentes:
            if jogos_necessarios_por_pessoa[m] > 0 and m not in [d[1] for d in duplas_rodada]:
                descansando.append(m)
        
        # Cria confrontos
        confrontos = []
        random.shuffle(duplas_rodada)  # Embaralha
        
        metade = len(duplas_rodada) // 2
        for i in range(metade):
            dupla1 = duplas_rodada[i]
            dupla2_idx = metade + i
            
            if dupla2_idx < len(duplas_rodada):
                dupla2 = duplas_rodada[dupla2_idx]
                
                confrontos.append({
                    "quadra": i + 1,
                    "dupla1": {"jogador1": dupla1[0], "jogador2": dupla1[1]},
                    "dupla2": {"jogador1": dupla2[0], "jogador2": dupla2[1]},
                    "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False}
                })
        
        rodadas.append({
            "numero": rodada_num + 1,
            "confrontos": confrontos,
            "descansando": descansando
        })
    
    return {"total_rodadas": 5, "rodadas": rodadas}

# TESTE
print("\n" + "="*90)
print("TESTE SOLUÇÃO FINAL: 9H + 10M = 19")
print("="*90 + "\n")

homens = [f"Homem{i+1}" for i in range(9)]
mulheres = [f"Mulher{i+1}" for i in range(10)]

rodadas_data = gerar_5_rodadas_final(homens, mulheres)

# Analisa
jogos_por_pessoa = defaultdict(int)

print("RESUMO DAS RODADAS:")
print("-" * 90)
for rodada in rodadas_data["rodadas"]:
    duplas_formadas = len(rodada["confrontos"]) * 2
    print(f"Rodada {rodada['numero']}: {len(rodada['confrontos'])} confrontos ({duplas_formadas} duplas), {len(rodada['descansando'])} descansando")
    
    for confronto in rodada["confrontos"]:
        for j in [confronto["dupla1"]["jogador1"], confronto["dupla1"]["jogador2"],
                 confronto["dupla2"]["jogador1"], confronto["dupla2"]["jogador2"]]:
            jogos_por_pessoa[j] += 1

print("\n" + "="*90)
print("DISTRIBUIÇÃO FINAL DE JOGOS:")
print("="*90)
print(f"\n{'Jogador':<15} | {'Jogos':<6} | Status")
print("-" * 40)

todos_5 = True
for pessoa in sorted(set(homens + mulheres)):
    jogos = jogos_por_pessoa.get(pessoa, 0)
    if jogos == 5:
        status = "✓ OK"
    else:
        status = f"✗ ERRO (esperado 5)"
        todos_5 = False
    print(f"{pessoa:<15} | {jogos:<6} | {status}")

print("\n" + "="*90)
if todos_5:
    print("✅✅✅ SUCESSO! TODOS JOGARAM EXATAMENTE 5 VEZES! ✅✅✅")
    print("✅ Permissão de repetição de duplas resolveu o problema!")
else:
    print("✗ Ainda não funciona - vou investigar mais")
print("="*90 + "\n")

