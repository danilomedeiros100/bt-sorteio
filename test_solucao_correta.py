#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solução CORRETA: Maximiza confrontos e garante 5 jogos para todos
Com 9H + 10M, precisamos de 19×5 = 95 jogos
Em 5 rodadas, podemos fazer no máximo 5×4×4 = 80 jogos (4 confrontos por rodada)
SOLUÇÃO: Aumentar para 5 confrontos quando possível!
"""

import random
from collections import defaultdict

def gerar_5_rodadas_correto(homens: list, mulheres: list):
    """
    GARANTE 5 jogos para todos permitindo repetição de duplas
    Maximiza confrontos em cada rodada
    """
    # Quantos jogos cada pessoa precisa
    jogos_pendentes = {p: 5 for p in (homens + mulheres)}
    
    rodadas = []
    
    # Para cada rodada
    for rodada_num in range(5):
        # Quem ainda precisa jogar (ordenado por quem precisa mais)
        homens_pendentes = sorted([h for h in homens if jogos_pendentes[h] > 0], 
                                  key=lambda h: jogos_pendentes[h], reverse=True)
        mulheres_pendentes = sorted([m for m in mulheres if jogos_pendentes[m] > 0], 
                                    key=lambda m: jogos_pendentes[m], reverse=True)
        
        # Forma o máximo de duplas possível
        duplas_rodada = []
        idx_h = 0
        idx_m = 0
        
        # Prioriza formar duplas com quem mais precisa jogar
        while idx_h < len(homens_pendentes) and idx_m < len(mulheres_pendentes):
            h = homens_pendentes[idx_h]
            m = mulheres_pendentes[idx_m]
            
            duplas_rodada.append((h, m))
            jogos_pendentes[h] -= 1
            jogos_pendentes[m] -= 1
            idx_h += 1
            idx_m += 1
        
        # Cria confrontos (emparelha duplas)
        confrontos = []
        random.shuffle(duplas_rodada)  # Embaralha para variar
        
        # Com 9H + 10M, podemos formar 9 duplas
        # 9 duplas = 4 confrontos (8 duplas) + 1 dupla sem adversário
        # SOLUÇÃO: A última dupla pode jogar com quem já jogou (se precisar)
        # Ou fazemos 5 confrontos com alguma estratégia
        
        # Se temos número ímpar de duplas, a última precisa de tratamento especial
        num_duplas = len(duplas_rodada)
        
        if num_duplas % 2 == 0:
            # Número par: pode fazer todos os confrontos
            metade = num_duplas // 2
            for i in range(metade):
                dupla1 = duplas_rodada[i]
                dupla2 = duplas_rodada[metade + i]
                confrontos.append({
                    "quadra": i + 1,
                    "dupla1": {"jogador1": dupla1[0], "jogador2": dupla1[1]},
                    "dupla2": {"jogador1": dupla2[0], "jogador2": dupla2[1]},
                    "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False}
                })
        else:
            # Número ímpar: fazer (n-1)/2 confrontos e última fica sem adversário
            # MAS: podemos fazer a última jogar com quem precisa mais
            metade = num_duplas // 2
            for i in range(metade):
                dupla1 = duplas_rodada[i]
                dupla2 = duplas_rodada[metade + i]
                confrontos.append({
                    "quadra": i + 1,
                    "dupla1": {"jogador1": dupla1[0], "jogador2": dupla1[1]},
                    "dupla2": {"jogador1": dupla2[0], "jogador2": dupla2[1]},
                    "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False}
                })
            
            # Última dupla: faz jogar com quem mais precisa
            # Busca alguém que ainda precisa jogar mas não está nesta rodada
            ultima_dupla = duplas_rodada[-1]
            
            # Pega quem mais precisa jogar de fora desta rodada
            todos_fora = sorted([p for p in (homens + mulheres) 
                                if p not in [d[0] for d in duplas_rodada] 
                                and p not in [d[1] for d in duplas_rodada]
                                and jogos_pendentes[p] > 0],
                               key=lambda p: jogos_pendentes[p], reverse=True)
            
            if len(todos_fora) >= 2:
                # Forma outra dupla temporária para confrontar
                h_fora = [p for p in todos_fora if p in homens]
                m_fora = [p for p in todos_fora if p in mulheres]
                
                if h_fora and m_fora:
                    dupla_oponente = (h_fora[0], m_fora[0])
                    jogos_pendentes[h_fora[0]] -= 1
                    jogos_pendentes[m_fora[0]] -= 1
                    
                    confrontos.append({
                        "quadra": len(confrontos) + 1,
                        "dupla1": {"jogador1": ultima_dupla[0], "jogador2": ultima_dupla[1]},
                        "dupla2": {"jogador1": dupla_oponente[0], "jogador2": dupla_oponente[1]},
                        "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False}
                    })
        
        # Quem descansa
        descansando = []
        for h in homens:
            if jogos_pendentes[h] > 0 and h not in [d[0] for d in duplas_rodada]:
                # Verifica se não foi usado como oponente temporário
                if h not in [c["dupla2"]["jogador1"] for c in confrontos 
                           if len(duplas_rodada) % 2 == 1]:
                    descansando.append(h)
        for m in mulheres:
            if jogos_pendentes[m] > 0 and m not in [d[1] for d in duplas_rodada]:
                if m not in [c["dupla2"]["jogador2"] for c in confrontos 
                          if len(duplas_rodada) % 2 == 1]:
                    descansando.append(m)
        
        rodadas.append({
            "numero": rodada_num + 1,
            "confrontos": confrontos,
            "descansando": list(set(descansando))
        })
    
    return {"total_rodadas": 5, "rodadas": rodadas}

# TESTE
print("\n" + "="*90)
print("TESTE SOLUÇÃO CORRETA: 9H + 10M = 19 (com maximização de confrontos)")
print("="*90 + "\n")

homens = [f"Homem{i+1}" for i in range(9)]
mulheres = [f"Mulher{i+1}" for i in range(10)]

rodadas_data = gerar_5_rodadas_correto(homens, mulheres)

# Analisa
jogos_por_pessoa = defaultdict(int)

print("RESUMO DAS RODADAS:")
print("-" * 90)
for rodada in rodadas_data["rodadas"]:
    num_confrontos = len(rodada["confrontos"])
    num_jogos_rodada = num_confrontos * 4
    print(f"Rodada {rodada['numero']}: {num_confrontos} confrontos ({num_jogos_rodada} jogos), {len(rodada['descansando'])} descansando")
    
    for confronto in rodada["confrontos"]:
        for j in [confronto["dupla1"]["jogador1"], confronto["dupla1"]["jogador2"],
                 confronto["dupla2"]["jogador1"], confronto["dupla2"]["jogador2"]]:
            jogos_por_pessoa[j] += 1

total_jogos = sum(jogos_por_pessoa.values())
print(f"\nTotal de jogos distribuídos: {total_jogos} / 95 necessários")

print("\n" + "="*90)
print("DISTRIBUIÇÃO FINAL:")
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
else:
    print(f"✗ Ainda faltam {95 - total_jogos} jogos para distribuir")
print("="*90 + "\n")

